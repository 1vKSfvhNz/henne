#ifndef TOF_SENSOR_HPP
#define TOF_SENSOR_HPP

class ToFSensor {
public:
    ToFSensor(int sensor_id);
    
    bool init();
    float read_distance_mm();
    
    void set_simulation_mode(bool sim);
    
private:
    int sensor_id;
    bool simulation_mode;
    float simulated_distance;
};

#endif