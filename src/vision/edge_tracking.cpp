#include "edge_tracking.hpp"
#include "../utils/logger.hpp"
#include <random>

EdgeTracking::EdgeTracking()
    : simulation_mode(true)
    , current_edge{0.0f, 0.0f, 0.95f, 0.0f} {}

void EdgeTracking::update(const std::vector<uint8_t>& image, int width, int height) {
    if (simulation_mode) {
        simulate_tracking();
    }
}

TrackedEdge EdgeTracking::get_current_position() const {
    return current_edge;
}

float EdgeTracking::get_lateral_error(float target_x) const {
    return target_x - current_edge.x;
}

void EdgeTracking::simulate_tracking() {
    static float t = 0;
    t += 0.001f;
    
    // Simuler une trajectoire sinusoïdale
    current_edge.x = 0.1f * std::sin(t * 10.0f);
    current_edge.y = 0.3f * std::sin(t * 5.0f);
    current_edge.confidence = 0.85f + 0.1f * std::sin(t);
    
    if (track_callback) {
        track_callback(current_edge.x, current_edge.y);
    }
}

void EdgeTracking::set_on_track(std::function<void(float, float)> callback) {
    track_callback = callback;
}

void EdgeTracking::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}