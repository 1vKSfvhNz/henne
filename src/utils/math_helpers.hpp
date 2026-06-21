#ifndef MATH_HELPERS_HPP
#define MATH_HELPERS_HPP

#include <cmath>
#include <vector>
#include <random>

namespace MathHelpers {
    inline float clamp(float value, float min, float max) {
        return std::max(min, std::min(value, max));
    }
    
    inline float lerp(float a, float b, float t) {
        return a + t * (b - a);
    }
    
    inline float smoothstep(float edge0, float edge1, float x) {
        float t = clamp((x - edge0) / (edge1 - edge0), 0.0f, 1.0f);
        return t * t * (3.0f - 2.0f * t);
    }
    
    inline float gaussian(float x, float mean, float sigma) {
        return std::exp(-std::pow((x - mean) / sigma, 2) / 2.0f) / (sigma * std::sqrt(2.0f * M_PI));
    }
    
    inline float distance(float x1, float y1, float x2, float y2) {
        return std::hypot(x2 - x1, y2 - y1);
    }
    
    float compute_curvature(const std::vector<float>& points, int idx);
    std::vector<float> smooth_trajectory(const std::vector<float>& trajectory, float sigma);
}

#endif