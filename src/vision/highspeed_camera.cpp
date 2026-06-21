#include "highspeed_camera.hpp"
#include "../utils/logger.hpp"
#include <thread>
#include <chrono>

HighSpeedCamera::HighSpeedCamera()
    : simulation_mode(true)
    , fps(1000)
    , streaming(false) {}

HighSpeedCamera::~HighSpeedCamera() {
    stop_streaming();
}

bool HighSpeedCamera::init(int initial_fps) {
    fps = initial_fps;
    if (simulation_mode) {
        LOG_INFO("Caméra haute vitesse [simulée] - {} FPS", fps);
        return true;
    }
    return true;
}

void HighSpeedCamera::start_streaming() {
    if (streaming) return;
    streaming = true;
    
    if (simulation_mode) {
        std::thread([this]() { simulation_loop(); }).detach();
    }
    LOG_INFO("Streaming caméra démarré");
}

void HighSpeedCamera::stop_streaming() {
    streaming = false;
    LOG_INFO("Streaming caméra arrêté");
}

std::vector<uint8_t> HighSpeedCamera::capture_frame() {
    // Retourne une frame simulée
    return std::vector<uint8_t>(640 * 480 * 3, 128);
}

void HighSpeedCamera::simulation_loop() {
    while (streaming) {
        if (frame_callback) {
            std::vector<uint8_t> frame(640 * 480, 255);
            frame_callback(frame);
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(1000 / fps));
    }
}

void HighSpeedCamera::set_on_frame(std::function<void(const std::vector<uint8_t>&)> callback) {
    frame_callback = callback;
}

void HighSpeedCamera::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}