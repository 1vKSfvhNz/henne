#include "aging_simulation.hpp"
#include <cmath>

AgingSimulation::AgingSimulation() {}

nlohmann::json AgingSimulation::apply_aging(const nlohmann::json& trajectory, int days) {
    nlohmann::json aged = trajectory;
    
    float fade = fade_curve(days);
    float cracking = cracking_curve(days);
    
    for (auto& point : aged) {
        point["fade"] = fade;
        point["cracking"] = cracking;
    }
    
    return aged;
}

float AgingSimulation::fade_curve(int days) const {
    // Modèle exponentiel de décoloration
    return std::exp(-days / 10.0f);
}

float AgingSimulation::cracking_curve(int days) const {
    // Apparition de craquelures après J+3
    if (days < 3) return 0.0f;
    return std::min(1.0f, (days - 3) / 14.0f);
}

float AgingSimulation::get_color_fade_factor(int days) const {
    return fade_curve(days);
}

float AgingSimulation::get_cracking_factor(int days) const {
    return cracking_curve(days);
}