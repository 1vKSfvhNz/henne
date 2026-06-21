#include "piezo_head.hpp"
#include "../utils/logger.hpp"

PiezoHead::PiezoHead()
    : simulation_mode(true) {}

bool PiezoHead::init() {
    if (simulation_mode) {
        LOG_INFO("Tête piézo 12 buses [simulée] initialisée");
        for (int i = 0; i < NUM_BUSES; ++i) {
            buses[i].enabled = false;
            buses[i].temperature = 25.0f;
        }
        return true;
    }
    return true;
}

void PiezoHead::enable_buse(int buse_id, bool enable) {
    if (buse_id >= 0 && buse_id < NUM_BUSES) {
        buses[buse_id].enabled = enable;
        if (simulation_mode) {
            LOG_TRACE("Buse[{}] enable={}", buse_id, enable);
        }
    }
}

void PiezoHead::set_amplitude(int buse_id, float amplitude) {
    if (buse_id >= 0 && buse_id < NUM_BUSES) {
        buses[buse_id].amplitude = std::clamp(amplitude, 0.0f, 1.0f);
    }
}

void PiezoHead::set_frequency(int buse_id, float frequency_hz) {
    if (buse_id >= 0 && buse_id < NUM_BUSES) {
        buses[buse_id].frequency = std::clamp(frequency_hz, 1000.0f, 50000.0f);
    }
}

void PiezoHead::set_flow_rate(int buse_id, float flow_ul_s) {
    if (buse_id >= 0 && buse_id < NUM_BUSES) {
        buses[buse_id].flow_rate = std::clamp(flow_ul_s, 0.0f, 60.0f);
    }
}

nlohmann::json PiezoHead::get_status() const {
    nlohmann::json status;
    for (int i = 0; i < NUM_BUSES; ++i) {
        status[std::to_string(i)] = {
            {"enabled", buses[i].enabled},
            {"amplitude", buses[i].amplitude},
            {"frequency", buses[i].frequency},
            {"flow", buses[i].flow_rate}
        };
    }
    return status;
}

void PiezoHead::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}