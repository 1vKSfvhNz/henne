#ifndef AGING_SIMULATION_HPP
#define AGING_SIMULATION_HPP

#include <nlohmann/json.hpp>

class AgingSimulation {
public:
    AgingSimulation();
    
    nlohmann::json apply_aging(const nlohmann::json& trajectory, int days);
    float get_color_fade_factor(int days) const;
    float get_cracking_factor(int days) const;
    
private:
    float fade_curve(int days) const;
    float cracking_curve(int days) const;
};

#endif