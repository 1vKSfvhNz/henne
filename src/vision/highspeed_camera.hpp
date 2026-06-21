#ifndef HIGHSPEED_CAMERA_HPP
#define HIGHSPEED_CAMERA_HPP

#include <vector>
#include <functional>
#include <nlohmann/json.hpp>

class HighSpeedCamera {
public:
    HighSpeedCamera();
    ~HighSpeedCamera();
    
    bool init(int fps = 1000);
    void start_streaming();
    void stop_streaming();
    
    std::vector<uint8_t> capture_frame();
    void set_on_frame(std::function<void(const std::vector<uint8_t>&)> callback);
    
    void set_simulation_mode(bool sim);
    
private:
    bool simulation_mode;
    int fps;
    bool streaming;
    std::function<void(const std::vector<uint8_t>&)> frame_callback;
    
    void simulation_loop();
};

#endif