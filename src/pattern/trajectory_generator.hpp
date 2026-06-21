#ifndef TRAJECTORY_GENERATOR_HPP
#define TRAJECTORY_GENERATOR_HPP

#include <vector>
#include <nlohmann/json.hpp>
#include "spiralnet_deformer.hpp"

struct TrajectorySegment {
    float x, y, z;
    float speed_mm_s;
    float flow_rate_ul_s;
    float pressure_bar;
    float thickness_mm;
    int buse_id;  // 0-11
};

class TrajectoryGenerator {
public:
    TrajectoryGenerator();
    
    std::vector<TrajectorySegment> generate(const std::vector<DeformedPoint>& deformed_points,
                                             const std::string& zone_type);
    
    nlohmann::json to_json(const std::vector<TrajectorySegment>& trajectory) const;
    
    void set_zone_params(const std::string& zone, float speed, float thickness);
    
private:
    std::unordered_map<std::string, ZoneParams> zone_params;
    
    struct ZoneParams {
        float base_speed = 25.0f;
        float base_thickness = 0.5f;
        float base_flow = 30.0f;
        float pressure = 2.0f;
    };
    
    void init_default_params();
    int select_buse(float thickness);
};

#endif