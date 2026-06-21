#ifndef LINEAR_ACTUATOR_HPP
#define LINEAR_ACTUATOR_HPP

class LinearActuator {
public:
    LinearActuator(int axis_id);
    
    bool init();
    void move_to(float position_mm, float speed_mm_s);
    void set_acceleration(float accel_mm_s2);
    float get_current_position() const;
    bool is_moving() const;
    
    void set_simulation_mode(bool sim);
    void update_simulation(float dt);
    
private:
    int axis_id;
    bool simulation_mode;
    float target_position;
    float current_position;
    float current_speed;
    float acceleration;
    bool moving;
    
    void real_move_to(float position, float speed);
};

#endif