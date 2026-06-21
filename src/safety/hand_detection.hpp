#ifndef HAND_DETECTION_HPP
#define HAND_DETECTION_HPP

#include <vector>
#include <nlohmann/json.hpp>

class HandDetection {
public:
    HandDetection();
    
    bool is_hand_present(const std::vector<uint8_t>& image, int width, int height);
    std::vector<std::pair<int, int>> get_hand_landmarks() const;
    
    void set_simulation_mode(bool sim);
    
private:
    bool simulation_mode;
    bool simulate_detection();
};

#endif