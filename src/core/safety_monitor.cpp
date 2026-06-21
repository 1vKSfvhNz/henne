#include "safety_monitor.hpp"
#include "../utils/logger.hpp"
#include <chrono>
#include <thread>

SafetyMonitor::SafetyMonitor()
    : running(false)
    , emergency_triggered(false)
    , last_capacitive(false)
    , hand_present(true)
    , current_temp(25.0f) {}

SafetyMonitor::~SafetyMonitor() {
    stop();
}


void SafetyMonitor::start() {
    if (running) return;
    running = true;
    emergency_triggered = false;
    monitor_thread = std::make_unique<std::thread>(&SafetyMonitor::monitoring_loop, this);
    LOG_INFO("SafetyMonitor démarré");
}

void SafetyMonitor::stop() {
    running = false;
    if (monitor_thread && monitor_thread->joinable()) {
        monitor_thread->join();
    }
    LOG_INFO("SafetyMonitor arrêté");
}

void SafetyMonitor::monitoring_loop() {
    while (running) {
        // Vérification des conditions d'urgence
        if (last_capacitive.load()) {
            LOG_WARN("Barre capacitive déclenchée - ARGENT URGENCE");
            emergency_triggered = true;
            if (emergency_callback) emergency_callback();
        }
        
        if (!hand_present.load()) {
            LOG_WARN("Main/pied retiré - Arrêt sécurité");
            emergency_triggered = true;
            if (emergency_callback) emergency_callback();
        }
        
        if (current_temp.load() > MAX_TEMP) {
            LOG_WARN("Surchauffe: {:.1f}°C > {:.1f}°C", current_temp.load(), MAX_TEMP);
            emergency_triggered = true;
            if (emergency_callback) emergency_callback();
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}

bool SafetyMonitor::is_emergency_triggered() const {
    return emergency_triggered.load();
}

void SafetyMonitor::reset_emergency() {
    emergency_triggered = false;
    LOG_INFO("Urgence réinitialisée");
}

void SafetyMonitor::set_on_emergency(std::function<void()> callback) {
    emergency_callback = callback;
}

void SafetyMonitor::update_capacitive_sensor(bool triggered) {
    last_capacitive = triggered;
}

void SafetyMonitor::update_hand_presence(bool present) {
    hand_present = present;
}

void SafetyMonitor::update_temperature(float temp_celsius) {
    current_temp = temp_celsius;
}