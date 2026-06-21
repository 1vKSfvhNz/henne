#include "hand_detection.hpp"
#include "../utils/logger.hpp"

HandDetection::HandDetection()
    : simulation_mode(true) {}

bool HandDetection::is_hand_present(const std::vector<uint8_t>& image, int width, int height) {
    if (simulation_mode) {
        return simulate_detection();
    }
    return true;  // Code réel avec MediaPipe
}

bool HandDetection::simulate_detection() {
    static bool present = true;
    // Simulation: main toujours présente sauf urgence
    return present;
}

std::vector<std::pair<int, int>> HandDetection::get_hand_landmarks() const {
    return {};  // Points clés MediaPipe
}

void HandDetection::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}