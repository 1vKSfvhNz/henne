#include "ir_leds.hpp"
#include "../utils/logger.hpp"
#include <thread>
#include <chrono>

IRLEDs::IRLEDs()
    : simulation_mode(true)
    , drying_active(false)
    , current_power(0.0f) {}

bool IRLEDs::init() {
    if (simulation_mode) {
        LOG_INFO("LEDs IR [simulées] initialisées ({} LEDs)", NUM_LEDS);
        return true;
    }
    return true;
}

void IRLEDs::set_power(float intensity_percent) {
    current_power = std::clamp(intensity_percent, 0.0f, 100.0f);
    LOG_DEBUG("LEDs IR puissance: {:.1f}%", current_power);
}

void IRLEDs::start_drying(int duration_seconds) {
    if (drying_active) return;
    drying_active = true;
    
    if (simulation_mode) {
        std::thread([this, duration_seconds]() {
            LOG_INFO("Séchage IR démarré ({}s)", duration_seconds);
            std::this_thread::sleep_for(std::chrono::seconds(duration_seconds));
            stop_drying();
            LOG_INFO("Séchage IR terminé");
        }).detach();
    }
}

void IRLEDs::stop_drying() {
    drying_active = false;
    current_power = 0.0f;
}

bool IRLEDs::is_drying() const {
    return drying_active;
}

float IRLEDs::get_temperature() const {
    if (simulation_mode) {
        return 35.0f + current_power * 0.3f;
    }
    return 0.0f;
}

void IRLEDs::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}