#include "machine_state.hpp"

MachineState::MachineState()
    : current_phase(MachinePhase::IDLE)
    , quality_score(0.0f) {}

void MachineState::set_phase(MachinePhase phase) {
    std::lock_guard<std::mutex> lock(mtx);
    current_phase = phase;
}

MachinePhase MachineState::get_phase() const {
    std::lock_guard<std::mutex> lock(mtx);
    return current_phase;
}

void MachineState::set_zone(const std::string& zone) {
    std::lock_guard<std::mutex> lock(mtx);
    current_zone = zone;
}

std::string MachineState::get_current_zone() const {
    std::lock_guard<std::mutex> lock(mtx);
    return current_zone;
}

void MachineState::set_motif_path(const std::string& path) {
    std::lock_guard<std::mutex> lock(mtx);
    motif_path = path;
}

std::string MachineState::get_motif_path() const {
    std::lock_guard<std::mutex> lock(mtx);
    return motif_path;
}

void MachineState::set_mesh_data(const nlohmann::json& mesh) {
    std::lock_guard<std::mutex> lock(mtx);
    mesh_data = mesh;
}

nlohmann::json MachineState::get_mesh_data() const {
    std::lock_guard<std::mutex> lock(mtx);
    return mesh_data;
}

void MachineState::set_trajectory(const nlohmann::json& traj) {
    std::lock_guard<std::mutex> lock(mtx);
    trajectory = traj;
}

nlohmann::json MachineState::get_trajectory() const {
    std::lock_guard<std::mutex> lock(mtx);
    return trajectory;
}

void MachineState::set_quality_score(float score) {
    std::lock_guard<std::mutex> lock(mtx);
    quality_score = score;
}

float MachineState::get_quality_score() const {
    std::lock_guard<std::mutex> lock(mtx);
    return quality_score;
}

void MachineState::reset() {
    std::lock_guard<std::mutex> lock(mtx);
    current_phase = MachinePhase::IDLE;
    current_zone.clear();
    motif_path.clear();
    mesh_data.clear();
    trajectory.clear();
    quality_score = 0.0f;
}