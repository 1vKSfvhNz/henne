#include "trajectory_generator.hpp"
#include "../utils/logger.hpp"
#include <cmath>

TrajectoryGenerator::TrajectoryGenerator() {
    init_default_params();
}

void TrajectoryGenerator::init_default_params() {
    zone_params["main"] = {15.0f, 0.3f, 20.0f, 2.2f};
    zone_params["pied"] = {20.0f, 0.5f, 25.0f, 2.5f};
    zone_params["avant_bras"] = {35.0f, 0.6f, 35.0f, 2.0f};
    zone_params["jambe"] = {40.0f, 0.8f, 45.0f, 1.8f};
}

std::vector<TrajectorySegment> TrajectoryGenerator::generate(
    const std::vector<DeformedPoint>& deformed_points,
    const std::string& zone_type) {
    
    std::vector<TrajectorySegment> trajectory;
    
    auto params_it = zone_params.find(zone_type);
    if (params_it == zone_params.end()) {
        LOG_WARN("Zone {} inconnue, utilisation paramètres par défaut", zone_type);
        params_it = zone_params.find("avant_bras");
    }
    
    const auto& params = params_it->second;
    
    for (size_t i = 0; i < deformed_points.size(); ++i) {
        TrajectorySegment seg;
        seg.x = deformed_points[i].x;
        seg.y = deformed_points[i].y;
        seg.z = deformed_points[i].z;
        seg.speed_mm_s = params.base_speed;
        seg.thickness_mm = params.base_thickness * deformed_points[i].thickness_scale;
        seg.flow_rate_ul_s = params.base_flow * deformed_points[i].thickness_scale;
        seg.pressure_bar = params.pressure;
        seg.buse_id = select_buse(seg.thickness_mm);
        
        trajectory.push_back(seg);
    }
    
    LOG_DEBUG("Trajectoire générée: {} segments pour zone {}", 
              trajectory.size(), zone_type);
    
    return trajectory;
}

int TrajectoryGenerator::select_buse(float thickness) {
    if (thickness < 0.25f) return 0;   // buse 0.2mm
    if (thickness < 0.5f) return 3;    // buse 0.4mm
    return 6;                           // buse 0.8mm
}

nlohmann::json TrajectoryGenerator::to_json(const std::vector<TrajectorySegment>& trajectory) const {
    nlohmann::json json_traj = nlohmann::json::array();
    for (const auto& seg : trajectory) {
        json_traj.push_back({
            {"x", seg.x}, {"y", seg.y}, {"z", seg.z},
            {"speed", seg.speed_mm_s},
            {"flow", seg.flow_rate_ul_s},
            {"pressure", seg.pressure_bar},
            {"thickness", seg.thickness_mm},
            {"buse", seg.buse_id}
        });
    }
    return json_traj;
}

void TrajectoryGenerator::set_zone_params(const std::string& zone, float speed, float thickness) {
    zone_params[zone].base_speed = speed;
    zone_params[zone].base_thickness = thickness;
}