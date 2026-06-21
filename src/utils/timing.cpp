#include "timing.hpp"

Timer::Timer()
    : running(false) {}

void Timer::start() {
    start_time = std::chrono::steady_clock::now();
    running = true;
}

void Timer::stop() {
    end_time = std::chrono::steady_clock::now();
    running = false;
}

void Timer::reset() {
    running = false;
}

double Timer::elapsed_ms() const {
    auto end = running ? std::chrono::steady_clock::now() : end_time;
    return std::chrono::duration<double, std::milli>(end - start_time).count();
}

double Timer::elapsed_us() const {
    auto end = running ? std::chrono::steady_clock::now() : end_time;
    return std::chrono::duration<double, std::micro>(end - start_time).count();
}

FPS_Counter::FPS_Counter()
    : frame_count(0)
    , current_fps(0.0f) {
    last_time = std::chrono::steady_clock::now();
}

void FPS_Counter::tick() {
    frame_count++;
    auto now = std::chrono::steady_clock::now();
    auto elapsed = std::chrono::duration<double>(now - last_time).count();
    
    if (elapsed >= 1.0) {
        current_fps = static_cast<float>(frame_count / elapsed);
        frame_count = 0;
        last_time = now;
    }
}

float FPS_Counter::get_fps() const {
    return current_fps;
}