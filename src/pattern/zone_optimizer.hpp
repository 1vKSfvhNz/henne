#ifndef ZONE_OPTIMIZER_HPP
#define ZONE_OPTIMIZER_HPP

#include <string>
#include <nlohmann/json.hpp>

class ZoneOptimizer {
public:
    ZoneOptimizer();
    
    nlohmann::json optimize_for_zone(const nlohmann::json& trajectory, 
                                      const std::string& zone);
    
    std::string suggest_best_zone(const nlohmann::json& svg);
    
    void set_zone_constraints(const std::string& zone, float max_curvature, float min_area);
    
private:
    struct ZoneConstraints {
        float max_curvature = 0.5f;
        float min_area_cm2 = 10.0f;
        bool has_fingers = false;
    };
    
    std::unordered_map<std::string, ZoneConstraints> constraints;
    void init_constraints();
};

#endif