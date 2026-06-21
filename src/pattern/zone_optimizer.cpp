#include "zone_optimizer.hpp"
#include "../utils/logger.hpp"

ZoneOptimizer::ZoneOptimizer() {
    init_constraints();
}

void ZoneOptimizer::init_constraints() {
    constraints["main"] = {0.8f, 25.0f, true};
    constraints["pied"] = {0.7f, 30.0f, true};
    constraints["avant_bras"] = {0.3f, 45.0f, false};
    constraints["jambe"] = {0.2f, 60.0f, false};
}

nlohmann::json ZoneOptimizer::optimize_for_zone(const nlohmann::json& trajectory,
                                                  const std::string& zone) {
    nlohmann::json optimized = trajectory;
    
    auto it = constraints.find(zone);
    if (it != constraints.end()) {
        // Ajuster la trajectoire selon les contraintes de la zone
        for (auto& point : optimized) {
            if (it->second.has_fingers) {
                // Ralentir dans les zones digitées
                if (std::abs(point["x"].get<float>()) > 0.6f) {
                    point["speed"] = point["speed"].get<float>() * 0.5f;
                }
            }
        }
        LOG_DEBUG("Trajectoire optimisée pour zone: {}", zone);
    }
    
    return optimized;
}

std::string ZoneOptimizer::suggest_best_zone(const nlohmann::json& svg) {
    // Calculer la surface approximative du motif
    float area_cm2 = 30.0f;  // Valeur simulée
    
    for (const auto& [zone, constraints] : this->constraints) {
        if (area_cm2 <= constraints.min_area_cm2) {
            LOG_INFO("Zone suggérée: {} (surface: {:.1f} cm²)", zone, area_cm2);
            return zone;
        }
    }
    
    return "avant_bras";
}

void ZoneOptimizer::set_zone_constraints(const std::string& zone, float max_curvature, float min_area) {
    constraints[zone].max_curvature = max_curvature;
    constraints[zone].min_area_cm2 = min_area;
}