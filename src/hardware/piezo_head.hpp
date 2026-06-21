#ifndef PIEZO_HEAD_HPP
#define PIEZO_HEAD_HPP

#include <array>
#include <nlohmann/json.hpp>

class PiezoHead {
public:
    PiezoHead();
    
    bool init();
    void enable_buse(int buse_id, bool enable);
    void set_amplitude(int buse_id, float amplitude);
    void set_frequency(int buse_id, float frequency_hz);
    void set_flow_rate(int buse_id, float flow_ul_s);
    
    nlohmann::json get_status() const;
    
    void set_simulation_mode(bool sim);
    
    static constexpr int NUM_BUSES = 12;
    
private:
    bool simulation_mode;
    struct BuseState {
        bool enabled = false;
        float amplitude = 0.0f;
        float frequency = 10000.0f;
        float flow_rate = 0.0f;
        float temperature = 25.0f;
    };
    
    std::array<BuseState, NUM_BUSES> buses;
};

#endif