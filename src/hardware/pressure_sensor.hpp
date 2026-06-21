#ifndef PRESSURE_SENSOR_HPP
#define PRESSURE_SENSOR_HPP

class PressureSensor {
public:
    PressureSensor(int sensor_id);
    
    bool init();
    float read_pressure_bar();
    
    void set_simulation_mode(bool sim);
    
private:
    int sensor_id;
    bool simulation_mode;
    float simulated_pressure;
};

#endif