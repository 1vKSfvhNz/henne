#include "math_helpers.hpp"

namespace MathHelpers {
    
    float compute_curvature(const std::vector<float>& points, int idx) {
        if (idx < 1 || idx >= static_cast<int>(points.size()) - 1) {
            return 0.0f;
        }
        
        float p0 = points[idx - 1];
        float p1 = points[idx];
        float p2 = points[idx + 1];
        
        float dx1 = p1 - p0;
        float dx2 = p2 - p1;
        float ddx = dx2 - dx1;
        
        return ddx;
    }
    
    std::vector<float> smooth_trajectory(const std::vector<float>& trajectory, float sigma) {
        if (trajectory.size() < 3) return trajectory;
        
        std::vector<float> smoothed(trajectory.size());
        int kernel_size = static_cast<int>(sigma * 3);
        
        for (size_t i = 0; i < trajectory.size(); ++i) {
            float sum = 0.0f;
            float weight_sum = 0.0f;
            
            for (int j = -kernel_size; j <= kernel_size; ++j) {
                int idx = static_cast<int>(i) + j;
                if (idx >= 0 && idx < static_cast<int>(trajectory.size())) {
                    float weight = gaussian(static_cast<float>(j), 0.0f, sigma);
                    sum += trajectory[idx] * weight;
                    weight_sum += weight;
                }
            }
            
            smoothed[i] = sum / weight_sum;
        }
        
        return smoothed;
    }
    
}