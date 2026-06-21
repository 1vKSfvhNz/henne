#ifndef TEMPERATURE_SENSOR_HPP
#define TEMPERATURE_SENSOR_HPP

class TemperatureSensor {
public:
    TemperatureSensor(int sensor_id);
    
    bool init();
    float read_temperature_celsius();
    
    void set_simulation_mode(bool sim);
    
private:
    int sensor_id;
    bool simulation_mode;
};

#endif