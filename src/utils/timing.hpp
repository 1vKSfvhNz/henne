#ifndef TIMING_HPP
#define TIMING_HPP

#include <chrono>

class Timer {
public:
    Timer();
    
    void start();
    void stop();
    void reset();
    
    double elapsed_ms() const;
    double elapsed_us() const;
    
private:
    std::chrono::steady_clock::time_point start_time;
    std::chrono::steady_clock::time_point end_time;
    bool running;
};

class FPS_Counter {
public:
    FPS_Counter();
    
    void tick();
    float get_fps() const;
    
private:
    std::chrono::steady_clock::time_point last_time;
    int frame_count;
    float current_fps;
};

#endif