#include "linear_actuator.hpp"
#include "../utils/logger.hpp"
#include <cmath>
#include <algorithm>

LinearActuator::LinearActuator(int id)
    : axis_id(id)
    , simulation_mode(true)
    , target_position(0.0f)
    , current_position(0.0f)
    , current_speed(0.0f)
    , acceleration(100.0f)
    , moving(false) {}

bool LinearActuator::init() {
    if (simulation_mode) {
        LOG_INFO("Actionneur linéaire axe{} [simulé] initialisé", axis_id);
        return true;
    }
    return true;
}

void LinearActuator::move_to(float position_mm, float speed_mm_s) {
    target_position = position_mm;
    current_speed = speed_mm_s;
    moving = true;
    
    if (simulation_mode) {
        LOG_TRACE("Axe{}: move_to pos={:.2f}mm speed={:.1f}mm/s", 
                  axis_id, position_mm, speed_mm_s);
    } else {
        real_move_to(position_mm, speed_mm_s);
    }
}

void LinearActuator::set_acceleration(float accel_mm_s2) {
    acceleration = accel_mm_s2;
}

float LinearActuator::get_current_position() const {
    return current_position;
}

bool LinearActuator::is_moving() const {
    return moving;
}

void LinearActuator::update_simulation(float dt) {
    if (!moving) return;
    
    float error = target_position - current_position;
    if (std::abs(error) < 0.01f) {
        moving = false;
        current_position = target_position;
        current_speed = 0;
        return;
    }
    
    float step = current_speed * dt;
    if (std::abs(step) > std::abs(error)) {
        current_position = target_position;
        moving = false;
    } else {
        current_position += (error > 0 ? step : -step);
    }
}

void LinearActuator::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}

void LinearActuator::real_move_to(float position, float speed) {
    // Code réel pour pilote moteur
}