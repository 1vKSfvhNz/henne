#ifndef HUMIDITY_SENSOR_HPP
#define HUMIDITY_SENSOR_HPP

class HumiditySensor {
public:
    HumiditySensor();
    
    bool init();
    float read_humidity_percent();
    
    void set_simulation_mode(bool sim);
    
private:
    bool simulation_mode;
    float simulated_humidity;
};

#endif