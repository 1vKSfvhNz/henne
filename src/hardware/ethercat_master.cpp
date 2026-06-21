#include "ethercat_master.hpp"
#include "../utils/logger.hpp"
#include <thread>
#include <chrono>

EtherCATMaster::EtherCATMaster()
    : simulation_mode(true)
    , running(false)
    , motor_positions(4, 0.0f) {}

EtherCATMaster::~EtherCATMaster() {
    stop_cycle();
}

bool EtherCATMaster::init(const std::string& interface) {
    if (simulation_mode) {
        LOG_INFO("EtherCAT Master [simulé] sur interface {}", interface);
        return true;
    }
    // Code réel SOEM ou IgH
    return true;
}

void EtherCATMaster::start_cycle(int cycle_time_us) {
    if (running) return;
    running = true;
    
    if (simulation_mode) {
        std::thread([this]() {
            while (running) {
                simulation_cycle();
                std::this_thread::sleep_for(std::chrono::microseconds(2000));
            }
        }).detach();
    } else {
        std::thread([this]() { real_cycle(); }).detach();
    }
    
    LOG_INFO("Cycle EtherCAT démarré (simulé)");
}

void EtherCATMaster::stop_cycle() {
    running = false;
    LOG_INFO("Cycle EtherCAT arrêté");
}

void EtherCATMaster::simulation_cycle() {
    // Simuler des lectures capteurs
    static float t = 0;
    t += 0.002f;
    
    for (int i = 0; i < 4; ++i) {
        motor_positions[i] += 0.1f;  // Mouvement simulé
    }
}

void EtherCATMaster::send_motor_command(int slave_id, float position_mm, float speed_mm_s) {
    if (simulation_mode) {
        LOG_TRACE("Moteur[{}] commande: pos={:.2f}mm speed={:.1f}mm/s", 
                  slave_id, position_mm, speed_mm_s);
    }
}

void EtherCATMaster::send_piezo_command(int buse_id, bool enable, float amplitude) {
    if (simulation_mode) {
        LOG_TRACE("Buse[{}] enable={} amplitude={:.2f}", buse_id, enable, amplitude);
    }
}

nlohmann::json EtherCATMaster::read_sensors() {
    nlohmann::json sensors;
    sensors["motor_positions"] = motor_positions;
    sensors["pressure"] = 2.2f;
    sensors["temperature"] = 28.5f;
    sensors["flow_rate"] = 32.0f;
    return sensors;
}

void EtherCATMaster::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}

void EtherCATMaster::real_cycle() {
    // Implémentation réelle
    while (running) {
        std::this_thread::sleep_for(std::chrono::microseconds(2000));
    }
}