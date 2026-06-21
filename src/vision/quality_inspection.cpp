#include "quality_inspection.hpp"
#include "../utils/logger.hpp"
#include <random>

QualityInspection::QualityInspection()
    : simulation_mode(true) {}

QualityReport QualityInspection::inspect(const std::vector<uint8_t>& image, int width, int height,
                                          const nlohmann::json& reference_trajectory) {
    if (simulation_mode) {
        return simulate_inspection();
    }
    return real_inspection(image, width, height, reference_trajectory);
}

QualityReport QualityInspection::simulate_inspection() {
    QualityReport report;
    
    static std::random_device rd;
    static std::mt19937 gen(rd());
    static std::normal_distribution<> score_dist(92.0f, 5.0f);
    
    report.overall_score = std::clamp(score_dist(gen), 60.0f, 100.0f);
    report.edge_accuracy = 0.88f + (report.overall_score - 50.0f) / 100.0f;
    report.thickness_uniformity = 0.85f + (report.overall_score - 50.0f) / 200.0f;
    report.coverage = 0.95f;
    
    if (report.overall_score >= 90) {
        report.verdict = "EXCELLENT";
    } else if (report.overall_score >= 75) {
        report.verdict = "GOOD";
    } else {
        report.verdict = "NEEDS_RETOUCH";
    }
    
    // Simuler quelques défauts
    if (report.overall_score < 85) {
        report.defect_positions.push_back({0.2f, 0.3f});
    }
    
    LOG_INFO("Qualité: score={:.1f} - {}", report.overall_score, report.verdict);
    
    return report;
}

nlohmann::json QualityInspection::generate_heatmap(const QualityReport& report) const {
    nlohmann::json heatmap;
    for (const auto& defect : report.defect_positions) {
        heatmap.push_back({{"x", defect.first}, {"y", defect.second}, {"intensity", 1.0f}});
    }
    return heatmap;
}

QualityReport QualityInspection::real_inspection(const std::vector<uint8_t>& image, int w, int h, const nlohmann::json& ref) {
    return {};  // À implémenter avec réseau siamois
}

void QualityInspection::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}