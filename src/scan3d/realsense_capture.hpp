#ifndef REALSENSE_CAPTURE_HPP
#define REALSENSE_CAPTURE_HPP

#include <string>
#include <vector>
#include <nlohmann/json.hpp>

struct Point3D {
    float x, y, z;
    uint8_t r, g, b;
};

class RealSenseCapture {
public:
    RealSenseCapture();
    ~RealSenseCapture();
    
    bool init(int device_id = 0);
    bool capture_depth_image();
    bool capture_rgb_image();
    
    std::vector<Point3D> get_point_cloud() const;
    nlohmann::json get_point_cloud_json() const;
    
    // Pour la simulation
    void set_simulation_mode(bool sim);
    void load_mock_scan(const std::string& filename);
    
    int get_width() const { return width; }
    int get_height() const { return height; }
    
private:
    bool simulation_mode;
    int device_id;
    int width, height;
    std::vector<Point3D> current_point_cloud;
    
    void generate_mock_cloud();
};

#endif