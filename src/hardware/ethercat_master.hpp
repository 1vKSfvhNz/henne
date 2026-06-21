#ifndef ETHERCAT_MASTER_HPP
#define ETHERCAT_MASTER_HPP

#include <string>
#include <vector>
#include <functional>
#include <nlohmann/json.hpp>

class EtherCATMaster {
public:
    EtherCATMaster();
    ~EtherCATMaster();
    
    bool init(const std::string& interface = "eth0");
    void start_cycle(int cycle_time_us = 2000);
    void stop_cycle();
    
    void send_motor_command(int slave_id, float position_mm, float speed_mm_s);
    void send_piezo_command(int buse_id, bool enable, float amplitude);
    
    nlohmann::json read_sensors();
    
    void set_simulation_mode(bool sim);
    
private:
    bool simulation_mode;
    bool running;
    std::vector<float> motor_positions;
    
    void simulation_cycle();
    void real_cycle();
};

#endif