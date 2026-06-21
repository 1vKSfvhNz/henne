#include "realtime_controller.hpp"
#include "../utils/logger.hpp"
#include <chrono>
#include <cmath>

RealtimeController::RealtimeController()
    : running(false)
    , loop_frequency(1000)
    , current_point_index(0)
    , current_x(0), current_y(0), current_z(0)
    , current_pressure(2.0f)
    , current_temp(25.0f)
    , pid_error_x(0), pid_integral_x(0), pid_prev_error_x(0)
    , pid_kp(1.2f), pid_ki(0.05f), pid_kd(0.1f) {}

RealtimeController::~RealtimeController() {
    stop_control_loop();
}

void RealtimeController::start_control_loop(int frequency_hz) {
    if (running) return;
    loop_frequency = frequency_hz;
    running = true;
    control_thread = std::make_unique<std::thread>(&RealtimeController::control_loop, this);
    LOG_INFO("Boucle contrôle temps réel démarrée à {} Hz", loop_frequency);
}

void RealtimeController::stop_control_loop() {
    running = false;
    if (control_thread && control_thread->joinable()) {
        control_thread->join();
    }
    LOG_INFO("Boucle contrôle arrêtée");
}

void RealtimeController::control_loop() {
    const std::chrono::duration<double> period(1.0 / loop_frequency);
    auto next_time = std::chrono::steady_clock::now();
    
    while (running) {
        auto start = std::chrono::steady_clock::now();
        
        // Calcul de la commande
        if (!trajectory.empty() && current_point_index < static_cast<int>(trajectory.size())) {
            float target_x = trajectory[current_point_index]["x"];
            float target_y = trajectory[current_point_index]["y"];
            float target_z = trajectory[current_point_index]["z"];
            
            update_pid(target_x, current_x, 1.0f / loop_frequency);
            
            float flow = compute_flow_from_error(pid_error_x);
            float pressure = trajectory[current_point_index].value("pressure", 2.0f);
            float speed = trajectory[current_point_index].value("speed", 25.0f);
            
            if (command_callback) {
                command_callback(flow, pressure, speed);
            }
            
            // Avancer dans la trajectoire si l'erreur est faible
            if (std::abs(pid_error_x) < 0.05f) {
                current_point_index++;
            }
        }
        
        // Timing pour maintenir la fréquence
        auto elapsed = std::chrono::steady_clock::now() - start;
        auto sleep_time = period - elapsed;
        if (sleep_time > std::chrono::microseconds(0)) {
            std::this_thread::sleep_for(sleep_time);
        }
    }
}

void RealtimeController::update_pid(float target, float current, float dt) {
    float error = target - current;
    pid_integral_x += error * dt;
    float derivative = (error - pid_prev_error_x) / dt;
    pid_error_x = pid_kp * error + pid_ki * pid_integral_x + pid_kd * derivative;
    pid_prev_error_x = error;
}

float RealtimeController::compute_flow_from_error(float error) {
    // Mapper l'erreur de position vers un débit
    float base_flow = 30.0f;
    float correction = std::clamp(error * 10.0f, -15.0f, 15.0f);
    return std::max(5.0f, base_flow + correction);
}

void RealtimeController::set_trajectory(const nlohmann::json& traj) {
    trajectory = traj;
    current_point_index = 0;
    pid_integral_x = 0;
    pid_prev_error_x = 0;
    LOG_INFO("Trajectoire chargée: {} points", trajectory.size());
}

void RealtimeController::update_sensor_data(float x, float y, float z,
                                             float pressure, float temperature) {
    current_x = x;
    current_y = y;
    current_z = z;
    current_pressure = pressure;
    current_temp = temperature;
}

nlohmann::json RealtimeController::get_actuator_commands() const {
    return {
        {"flow_ul_s", 35.0f},
        {"pressure_bar", current_pressure},
        {"speed_mm_s", 25.0f},
        {"position", {current_x, current_y, current_z}}
    };
}

void RealtimeController::set_on_command(std::function<void(float, float, float)> callback) {
    command_callback = callback;
}