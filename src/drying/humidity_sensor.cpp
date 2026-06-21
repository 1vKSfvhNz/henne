#include "humidity_sensor.hpp"
#include "../utils/logger.hpp"
#include <random>

HumiditySensor::HumiditySensor()
    : simulation_mode(true)
    , simulated_humidity(40.0f) {}

bool HumiditySensor::init() {
    if (simulation_mode) {
        LOG_INFO("Capteur d'humidité [simulé] initialisé");
        return true;
    }
    return true;
}

float HumiditySensor::read_humidity_percent() {
    if (simulation_mode) {
        static std::random_device rd;
        static std::mt19937 gen(rd());
        static std::normal_distribution<> dist(25.0f, 5.0f);
        
        // L'humidité diminue avec le séchage
        simulated_humidity = std::max(10.0f, dist(gen));
        return simulated_humidity;
    }
    return 0.0f;
}

void HumiditySensor::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}