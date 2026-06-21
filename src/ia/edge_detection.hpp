#ifndef EDGE_DETECTION_HPP
#define EDGE_DETECTION_HPP

#include <vector>
#include <nlohmann/json.hpp>

struct EdgePoint {
    float x, y;
    float confidence;
    float gradient_magnitude;
};

class EdgeDetection {
public:
    EdgeDetection();
    
    std::vector<EdgePoint> detect_edges(const std::vector<uint8_t>& image, int width, int height);
    nlohmann::json fit_curve(const std::vector<EdgePoint>& edges);
    
    void set_simulation_mode(bool sim);
    
private:
    bool simulation_mode;
    float low_threshold = 50.0f;
    float high_threshold = 150.0f;
    
    std::vector<EdgePoint> canny_edge_detection(const std::vector<uint8_t>& image, int w, int h);
    std::vector<EdgePoint> simulate_edges();
};

#endif