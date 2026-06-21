#ifndef REALTIME_CONTROLLER_HPP
#define REALTIME_CONTROLLER_HPP

#include <vector>
#include <functional>
#include <atomic>
#include <thread>
#include <nlohmann/json.hpp>

class RealtimeController {
public:
    RealtimeController();
    ~RealtimeController();
    
    void start_control_loop(int frequency_hz = 1000);
    void stop_control_loop();
    
    void set_trajectory(const nlohmann::json& trajectory);
    void update_sensor_data(float current_x, float current_y, float current_z,
                            float pressure, float temperature);
    
    nlohmann::json get_actuator_commands() const;
    
    void set_on_command(std::function<void(float flow, float pressure, float speed)> callback);
    
private:
    void control_loop();
    
    std::atomic<bool> running;
    std::unique_ptr<std::thread> control_thread;
    int loop_frequency;
    
    nlohmann::json trajectory;
    int current_point_index;
    
    float current_x, current_y, current_z;
    float current_pressure;
    float current_temp;
    
    float pid_error_x, pid_integral_x, pid_prev_error_x;
    float pid_kp, pid_ki, pid_kd;
    
    std::function<void(float, float, float)> command_callback;
    
    void update_pid(float target_x, float current_x, float dt);
    float compute_flow_from_error(float error);
};

#endif