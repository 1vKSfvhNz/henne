#ifndef THERMAL_PROTECTION_HPP
#define THERMAL_PROTECTION_HPP

#include <functional>

class ThermalProtection {
public:
    ThermalProtection();
    
    void update_temperature(float temp_celsius);
    bool is_overheating() const;
    void set_on_overheat(std::function<void()> callback);
    
    void set_threshold(float max_temp);
    
private:
    float current_temp;
    float max_threshold;
    std::function<void()> overheat_callback;
};

#endif