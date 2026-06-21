#include "main.hpp"
#include "core/machine_state.hpp"
#include "core/job_manager.hpp"
#include "core/safety_monitor.hpp"
#include "utils/logger.hpp"
#include <iostream>
#include <thread>
#include <chrono>

int main(int argc, char** argv) {
    Logger::init("logs/mihi_cn.log");
    LOG_INFO("Démarrage MIHI-CN v2.0 - Mode Simulation");
    
    GlobalContext ctx;
    ctx.simulation_mode = true;
    
    // Initialisation des composants
    ctx.machine_state = std::make_shared<MachineState>();
    ctx.job_manager = std::make_shared<JobManager>();
    ctx.safety_monitor = std::make_shared<SafetyMonitor>();
    
    LOG_INFO("Composants initialisés");
    
    // Boucle principale de simulation
    int cycle_count = 0;
    while (cycle_count < 10) {
        LOG_INFO("Cycle {} - En attente de client...", cycle_count);
        
        // Simulation d'un client
        std::this_thread::sleep_for(std::chrono::seconds(2));
        
        // Scan 3D simulé
        ctx.machine_state->set_zone("avant_bras");
        LOG_INFO("Scan 3D terminé - Zone: {}", ctx.machine_state->get_current_zone());
        
        // Preview (simulé)
        LOG_INFO("Preview envoyé à l'écran client");
        std::this_thread::sleep_for(std::chrono::seconds(1));
        
        // Validation client
        LOG_INFO("Client a validé le motif");
        
        // Traçage simulé
        LOG_INFO("Début du traçage (70s simulées)");
        for (int i = 0; i <= 100; i += 10) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
            LOG_DEBUG("Progression: {}%", i);
        }
        
        // Séchage
        LOG_INFO("Séchage terminé (10s)");
        
        // Contrôle qualité
        LOG_INFO("Score qualité: 94/100");
        
        cycle_count++;
    }
    
    LOG_INFO("Arrêt de la machine - 10 cycles complétés");
    return 0;
}