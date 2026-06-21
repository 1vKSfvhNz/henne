#ifndef EDGE_TRACKING_HPP
#define EDGE_TRACKING_HPP

#include <vector>
#include <functional>
#include <nlohmann/json.hpp>

struct TrackedEdge {
    float x, y;
    float confidence;
    float angle_rad;
};

class EdgeTracking {
public:
    EdgeTracking();
    
    void update(const std::vector<uint8_t>& image, int width, int height);
    TrackedEdge get_current_position() const;
    float get_lateral_error(float target_x) const;
    
    void set_on_track(std::function<void(float error_x, float error_y)> callback);
    
    void set_simulation_mode(bool sim);
    
private:
    bool simulation_mode;
    TrackedEdge current_edge;
    std::function<void(float, float)> track_callback;
    
    void simulate_tracking();
};

#endif