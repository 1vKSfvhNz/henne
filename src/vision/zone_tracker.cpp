#include "zone_tracker.hpp"
#include "../utils/logger.hpp"
#include <random>

ZoneTracker::ZoneTracker()
    : simulation_mode(true)
    , current_zone("avant_bras") {}

ZonePose ZoneTracker::track_zone(const std::vector<uint8_t>& rgb_image, const std::vector<float>& depth_data) {
    if (simulation_mode) {
        return simulate_pose();
    }
    return current_pose;
}

ZonePose ZoneTracker::simulate_pose() {
    static float t = 0;
    t += 0.01f;
    
    ZonePose pose;
    pose.x = 0.1f * std::sin(t);
    pose.y = 0.2f * std::cos(t * 0.7f);
    pose.z = 0.5f + 0.05f * std::sin(t * 1.3f);
    pose.roll = 0.05f * std::sin(t * 2.0f);
    pose.pitch = 0.03f * std::cos(t);
    pose.yaw = 0.02f * std::sin(t * 1.5f);
    pose.zone_id = current_zone;
    pose.confidence = 0.92f;
    
    return pose;
}

void ZoneTracker::update_zone(const std::string& zone_type) {
    current_zone = zone_type;
    LOG_DEBUG("Zone tracker mis à jour: {}", zone_type);
}

void ZoneTracker::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}