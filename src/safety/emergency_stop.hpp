#ifndef EMERGENCY_STOP_HPP
#define EMERGENCY_STOP_HPP

#include <functional>

class EmergencyStop {
public:
    EmergencyStop();
    
    bool init();
    void trigger();
    void reset();
    
    bool is_triggered() const;
    void set_on_trigger(std::function<void()> callback);
    
    void set_simulation_mode(bool sim);
    
private:
    bool simulation_mode;
    bool triggered;
    std::function<void()> callback;
    
    void hardware_stop();
};

#endif