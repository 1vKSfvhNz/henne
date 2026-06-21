#ifndef IR_LEDS_HPP
#define IR_LEDS_HPP

#include <array>

class IRLEDs {
public:
    IRLEDs();
    
    bool init();
    void set_power(float intensity_percent);  // 0-100
    void start_drying(int duration_seconds);
    void stop_drying();
    
    bool is_drying() const;
    float get_temperature() const;
    
    void set_simulation_mode(bool sim);
    
private:
    bool simulation_mode;
    bool drying_active;
    float current_power;
    static constexpr int NUM_LEDS = 6;
    std::array<float, NUM_LEDS> led_temperatures;
};

#endif