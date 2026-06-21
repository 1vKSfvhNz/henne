#include "tof_sensor.hpp"
#include "../utils/logger.hpp"
#include <random>

ToFSensor::ToFSensor(int id)
    : sensor_id(id)
    , simulation_mode(true)
    , simulated_distance(10.0f) {}

bool ToFSensor::init() {
    if (simulation_mode) {
        LOG_INFO("Capteur ToF [simulé] ID{} initialisé", sensor_id);
        return true;
    }
    return true;
}

float ToFSensor::read_distance_mm() {
    if (simulation_mode) {
        static std::random_device rd;
        static std::mt19937 gen(rd());
        static std::normal_distribution<> dist(8.0f, 1.0f);
        return dist(gen);
    }
    return 0.0f;
}

void ToFSensor::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}