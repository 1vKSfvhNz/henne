#ifndef MAIN_HPP
#define MAIN_HPP

#include <string>
#include <memory>

// Forward declarations
class MachineState;
class JobManager;
class SafetyMonitor;

struct GlobalContext {
    std::shared_ptr<MachineState> machine_state;
    std::shared_ptr<JobManager> job_manager;
    std::shared_ptr<SafetyMonitor> safety_monitor;
    
    bool simulation_mode = true;
    std::string config_path = "../config/";
};

#endif // MAIN_HPP