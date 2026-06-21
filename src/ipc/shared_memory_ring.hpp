#ifndef SHARED_MEMORY_RING_HPP
#define SHARED_MEMORY_RING_HPP

#include <atomic>
#include <cstdint>
#include <cstring>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <chrono>

#pragma pack(push, 1)
struct TrajectoryPoint {
    float x, y, z;           // Position 3D (12 bytes)
    float thickness;         // Épaisseur trait (4 bytes)
    float speed;             // Vitesse mm/s (4 bytes)
    float flow_rate;         // Débit µl/s (4 bytes)
    uint32_t timestamp_us;   // Microsecondes (4 bytes)
    uint16_t buse_id;        // Buse 0-11 (2 bytes)
    uint8_t flags;           // Bits: start, end, emergency (1 byte)
    uint8_t reserved[5];     // Padding (5 bytes)
    // Total: 36 bytes par point
};
#pragma pack(pop)

struct RingBuffer {
    static constexpr size_t RING_SIZE = 2048;  // 2 secondes à 1kHz
    static constexpr size_t SHM_SIZE = sizeof(RingBuffer);
    
    // Header (premier cache line)
    std::atomic<uint32_t> write_index{0};
    std::atomic<uint32_t> read_index{0};
    alignas(64) std::atomic<bool> running{false};
    alignas(64) std::atomic<bool> emergency{false};
    
    // Données
    TrajectoryPoint trajectory[RING_SIZE];
    
    // Métriques temps réel
    alignas(64) std::atomic<float> current_x{0};
    alignas(64) std::atomic<float> current_y{0};
    alignas(64) std::atomic<float> current_z{0};
    alignas(64) std::atomic<float> current_pressure{2.0f};
    alignas(64) std::atomic<float> current_flow{0};
    alignas(64) std::atomic<float> last_timestamp{0};
    
    bool write(const TrajectoryPoint& point) {
        uint32_t write_idx = write_index.load(std::memory_order_acquire);
        uint32_t next_idx = (write_idx + 1) % RING_SIZE;
        
        // Vérifier si le buffer est plein
        if (next_idx == read_index.load(std::memory_order_acquire)) {
            return false;  // Buffer full
        }
        
        trajectory[write_idx] = point;
        write_index.store(next_idx, std::memory_order_release);
        return true;
    }
    
    bool read(TrajectoryPoint& point) {
        uint32_t read_idx = read_index.load(std::memory_order_acquire);
        if (read_idx == write_index.load(std::memory_order_acquire)) {
            return false;  // Buffer empty
        }
        
        point = trajectory[read_idx];
        read_index.store((read_idx + 1) % RING_SIZE, std::memory_order_release);
        return true;
    }
    
    void clear() {
        write_index.store(0, std::memory_order_release);
        read_index.store(0, std::memory_order_release);
    }
};

class SharedMemoryRing {
public:
    SharedMemoryRing() : shm_fd(-1), ring(nullptr) {}
    
    bool create(const char* name = "/mihi_cn_ring") {
        shm_fd = shm_open(name, O_CREAT | O_RDWR, 0666);
        if (shm_fd == -1) return false;
        
        if (ftruncate(shm_fd, RingBuffer::SHM_SIZE) == -1) return false;
        
        ring = (RingBuffer*)mmap(0, RingBuffer::SHM_SIZE, 
                                  PROT_READ | PROT_WRITE, 
                                  MAP_SHARED, shm_fd, 0);
        
        if (ring == MAP_FAILED) return false;
        
        new (ring) RingBuffer();  // Placement new
        return true;
    }
    
    bool open(const char* name = "/mihi_cn_ring") {
        shm_fd = shm_open(name, O_RDWR, 0666);
        if (shm_fd == -1) return false;
        
        ring = (RingBuffer*)mmap(0, RingBuffer::SHM_SIZE, 
                                  PROT_READ | PROT_WRITE, 
                                  MAP_SHARED, shm_fd, 0);
        
        return ring != MAP_FAILED;
    }
    
    RingBuffer* get() { return ring; }
    
    ~SharedMemoryRing() {
        if (ring) munmap(ring, RingBuffer::SHM_SIZE);
        if (shm_fd != -1) close(shm_fd);
    }
    
private:
    int shm_fd;
    RingBuffer* ring;
};

#endif