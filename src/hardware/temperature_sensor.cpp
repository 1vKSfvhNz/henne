#include "temperature_sensor.hpp"
#include "../utils/logger.hpp"
#include <random>

TemperatureSensor::TemperatureSensor(int id)
    : sensor_id(id)
    , simulation_mode(true) {}

bool TemperatureSensor::init() {
    if (simulation_mode) {
        LOG_INFO("Capteur température [simulé] ID{} initialisé", sensor_id);
        return true;
    }
    return true;
}

float TemperatureSensor::read_temperature_celsius() {
    if (simulation_mode) {
        static std::random_device rd;
        static std::mt19937 gen(rd());
        static std::normal_distribution<> temp(28.0f, 2.0f);
        return temp(gen);
    }
    return 0.0f;
}

void TemperatureSensor::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}