#ifndef ZONE_TRACKER_HPP
#define ZONE_TRACKER_HPP

#include <string>
#include <nlohmann/json.hpp>

struct ZonePose {
    float x, y, z;
    float roll, pitch, yaw;
    std::string zone_id;
    float confidence;
};

class ZoneTracker {
public:
    ZoneTracker();
    
    ZonePose track_zone(const std::vector<uint8_t>& rgb_image, const std::vector<float>& depth_data);
    void update_zone(const std::string& zone_type);
    
    void set_simulation_mode(bool sim);
    
private:
    bool simulation_mode;
    std::string current_zone;
    ZonePose current_pose;
    
    ZonePose simulate_pose();
};

#endif