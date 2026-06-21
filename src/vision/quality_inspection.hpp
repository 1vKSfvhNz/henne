#ifndef QUALITY_INSPECTION_HPP
#define QUALITY_INSPECTION_HPP

#include <string>
#include <nlohmann/json.hpp>

struct QualityReport {
    float overall_score;  // 0-100
    float edge_accuracy;
    float thickness_uniformity;
    float coverage;
    std::vector<std::pair<float, float>> defect_positions;
    std::string verdict;  // "EXCELLENT", "GOOD", "NEEDS_RETOUCH"
};

class QualityInspection {
public:
    QualityInspection();
    
    QualityReport inspect(const std::vector<uint8_t>& image, int width, int height,
                          const nlohmann::json& reference_trajectory);
    
    nlohmann::json generate_heatmap(const QualityReport& report) const;
    
    void set_simulation_mode(bool sim);
    
private:
    bool simulation_mode;
    
    QualityReport simulate_inspection();
    QualityReport real_inspection(const std::vector<uint8_t>& image, int w, int h, const nlohmann::json& ref);
};

#endif