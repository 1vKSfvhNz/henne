#include "zone_segmentation.hpp"
#include "../utils/logger.hpp"
#include <random>

ZoneSegmentation::ZoneSegmentation()
    : simulation_mode(true) {}

std::string ZoneSegmentation::classify_zone(const nlohmann::json& mesh) {
    if (simulation_mode) {
        // Simulation: retourne une zone aléatoire pondérée
        static std::random_device rd;
        static std::mt19937 gen(rd());
        static std::discrete_distribution<> dist({0.3, 0.2, 0.35, 0.15});
        
        int idx = dist(gen);
        std::vector<std::string> zones = {"main", "pied", "avant_bras", "jambe"};
        LOG_INFO("Zone classifiée [simulée]: {}", zones[idx]);
        return zones[idx];
    }
    return rule_based_classification(mesh);
}

std::string ZoneSegmentation::rule_based_classification(const nlohmann::json& mesh) {
    // Ici, code réel basé sur la forme du mesh
    return "avant_bras";
}

std::vector<ZoneMask> ZoneSegmentation::segment_avoid_zones(const nlohmann::json& mesh) {
    std::vector<ZoneMask> masks;
    
    if (simulation_mode) {
        // Simuler quelques zones à éviter
        ZoneMask mask;
        mask.zone_type = "cicatrice_simulee";
        mask.confidence = 0.85f;
        for (int i = 0; i < 50; ++i) {
            mask.vertex_indices.push_back(100 + i);
        }
        masks.push_back(mask);
        
        LOG_DEBUG("Zones d'évitement simulées: {} zones", masks.size());
    } else {
        masks = detect_cicatrices_grains(mesh);
    }
    
    return masks;
}

std::vector<ZoneMask> ZoneSegmentation::detect_cicatrices_grains(const nlohmann::json& mesh) {
    // Implémentation réelle avec vision par ordinateur
    return {};
}

nlohmann::json ZoneSegmentation::get_avoidance_mask() const {
    return avoidance_mask;
}

void ZoneSegmentation::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}