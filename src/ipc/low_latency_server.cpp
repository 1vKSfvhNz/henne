#include <iostream>
#include <thread>
#include <atomic>
#include <chrono>
#include <cstring>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

class UnixDomainSocket {
public:
    UnixDomainSocket() : fd(-1) {}
    
    bool create_server(const char* path = "/tmp/mihi_cn.sock") {
        unlink(path);
        
        fd = socket(AF_UNIX, SOCK_STREAM, 0);
        if (fd < 0) return false;
        
        struct sockaddr_un addr;
        memset(&addr, 0, sizeof(addr));
        addr.sun_family = AF_UNIX;
        strcpy(addr.sun_path, path);
        
        if (bind(fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) return false;
        if (listen(fd, 10) < 0) return false;
        
        return true;
    }
    
    int accept_client() {
        return accept(fd, nullptr, nullptr);
    }
    
    ssize_t send_all(int client_fd, const void* data, size_t len) {
        return write(client_fd, data, len);
    }
    
    ssize_t recv_all(int client_fd, void* buffer, size_t len) {
        return read(client_fd, buffer, len);
    }
    
    ~UnixDomainSocket() {
        if (fd >= 0) close(fd);
    }
    
private:
    int fd;
};

// Structure de données ultra-compacte (16 bytes)
struct __attribute__((packed)) UltraCompactCommand {
    int32_t x_int;        // Position X en micromètres (int32_t)
    int32_t y_int;        // Position Y en micromètres
    int32_t z_int;        // Position Z en micromètres
    uint16_t flow;        // Débit en centièmes de µl/s
    uint8_t buse_mask;    // Bitmask des buses actives
    uint8_t flags;        // Bits: start(1), stop(2), emergency(4)
};

class LowLatencyController {
public:
    void start() {
        UnixDomainSocket server;
        if (!server.create_server()) {
            std::cerr << "Failed to create Unix socket" << std::endl;
            return;
        }
        
        int client_fd = server.accept_client();
        if (client_fd < 0) return;
        
        std::cout << "Client connected" << std::endl;
        
        // Boucle à 1kHz
        auto period = std::chrono::microseconds(1000);
        auto next_time = std::chrono::steady_clock::now();
        
        int seq = 0;
        while (running) {
            UltraCompactCommand cmd;
            cmd.x_int = static_cast<int32_t>(current_x * 1000);  // mm -> µm
            cmd.y_int = static_cast<int32_t>(current_y * 1000);
            cmd.z_int = static_cast<int32_t>(current_z * 1000);
            cmd.flow = static_cast<uint16_t>(current_flow * 100);
            cmd.buse_mask = 0xFF;  // Toutes buses actives
            cmd.flags = 0;
            
            server.send_all(client_fd, &cmd, sizeof(cmd));
            seq++;
            
            next_time += period;
            std::this_thread::sleep_until(next_time);
        }
        
        close(client_fd);
    }
    
    void stop() { running = false; }
    
private:
    std::atomic<bool> running{true};
    float current_x = 0, current_y = 0, current_z = 0;
    float current_flow = 30.0f;
};