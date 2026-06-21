#include "thermal_protection.hpp"
#include "../utils/logger.hpp"

ThermalProtection::ThermalProtection()
    : current_temp(25.0f)
    , max_threshold(45.0f) {}

void ThermalProtection::update_temperature(float temp_celsius) {
    current_temp = temp_celsius;
    
    if (is_overheating() && overheat_callback) {
        LOG_WARN("Surchauffe détectée: {:.1f}°C > {:.1f}°C", current_temp, max_threshold);
        overheat_callback();
    }
}

bool ThermalProtection::is_overheating() const {
    return current_temp > max_threshold;
}

void ThermalProtection::set_on_overheat(std::function<void()> callback) {
    overheat_callback = callback;
}

void ThermalProtection::set_threshold(float max_temp) {
    max_threshold = max_temp;
}