#ifndef MACHINE_STATE_HPP
#define MACHINE_STATE_HPP

#include <string>
#include <mutex>
#include <vector>
#include <nlohmann/json.hpp>

enum class MachinePhase {
    IDLE,
    SCANNING,
    PROCESSING_IA,
    PREVIEW,
    WAITING_VALIDATION,
    PREPARING,
    TRACING,
    DRYING,
    QUALITY_CHECK,
    FINISHED,
    EMERGENCY_STOP
};

class MachineState {
public:
    MachineState();
    
    void set_phase(MachinePhase phase);
    MachinePhase get_phase() const;
    
    void set_zone(const std::string& zone);
    std::string get_current_zone() const;
    
    void set_motif_path(const std::string& path);
    std::string get_motif_path() const;
    
    void set_mesh_data(const nlohmann::json& mesh);
    nlohmann::json get_mesh_data() const;
    
    void set_trajectory(const nlohmann::json& traj);
    nlohmann::json get_trajectory() const;
    
    void set_quality_score(float score);
    float get_quality_score() const;
    
    void reset();
    
private:
    mutable std::mutex mtx;
    MachinePhase current_phase;
    std::string current_zone;
    std::string motif_path;
    nlohmann::json mesh_data;
    nlohmann::json trajectory;
    float quality_score;
};

#endif