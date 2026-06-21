#include "emergency_stop.hpp"
#include "../utils/logger.hpp"

EmergencyStop::EmergencyStop()
    : simulation_mode(true)
    , triggered(false) {}

bool EmergencyStop::init() {
    if (simulation_mode) {
        LOG_INFO("Bouton arrêt urgence [simulé] initialisé");
        return true;
    }
    return true;
}

void EmergencyStop::trigger() {
    triggered = true;
    LOG_WARN("⚠️ ARRÊT URGENCE DÉCLENCHÉ ⚠️");
    
    if (callback) {
        callback();
    }
    
    if (!simulation_mode) {
        hardware_stop();
    }
}

void EmergencyStop::reset() {
    triggered = false;
    LOG_INFO("Arrêt urgence réinitialisé");
}

bool EmergencyStop::is_triggered() const {
    return triggered;
}

void EmergencyStop::set_on_trigger(std::function<void()> cb) {
    callback = cb;
}

void EmergencyStop::hardware_stop() {
    // Couper les moteurs et les buses
}

void EmergencyStop::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}