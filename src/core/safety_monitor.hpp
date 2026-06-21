#ifndef SAFETY_MONITOR_HPP
#define SAFETY_MONITOR_HPP

#include <functional>
#include <atomic>
#include <thread>

class SafetyMonitor {
public:
    SafetyMonitor();
    ~SafetyMonitor();
    
    void start();
    void stop();
    
    bool is_emergency_triggered() const;
    void reset_emergency();
    
    void set_on_emergency(std::function<void()> callback);
    
    // Capteurs simulés
    void update_capacitive_sensor(bool triggered);
    void update_hand_presence(bool present);
    void update_temperature(float temp_celsius);
    
private:
    void monitoring_loop();
    
    std::atomic<bool> running;
    std::atomic<bool> emergency_triggered;
    std::atomic<bool> last_capacitive;
    std::atomic<bool> hand_present;
    std::atomic<float> current_temp;
    
    std::function<void()> emergency_callback;
    std::unique_ptr<std::thread> monitor_thread;
    
    static constexpr float MAX_TEMP = 42.0f;  // °C
    static constexpr int HEARTBEAT_TIMEOUT_MS = 100;
};

#endif