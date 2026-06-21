#include "curvature_map.hpp"
#include "../utils/logger.hpp"
#include <random>
#include <cmath>

CurvatureMap::CurvatureMap()
    : simulation_mode(true) {}

std::vector<CurvaturePoint> CurvatureMap::compute_curvature(const nlohmann::json& mesh) {
    if (simulation_mode) {
        compute_mock_curvature(mesh);
        return curvature_data;
    }
    // Algorithme réel de courbure discrète
    return {};
}

void CurvatureMap::compute_mock_curvature(const nlohmann::json& mesh) {
    curvature_data.clear();
    
    int num_vertices = mesh.contains("vertices") ? mesh["vertices"].size() : 1000;
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<> dist_curv(0.0, 0.1);
    std::uniform_real_distribution<> dist_stretch(0.05, 0.25);
    
    for (int i = 0; i < num_vertices; ++i) {
        CurvaturePoint cp;
        cp.vertex_id = i;
        cp.mean_curvature = std::abs(dist_curv(gen));
        cp.gaussian_curvature = dist_curv(gen);
        cp.max_stretch = dist_stretch(gen);
        curvature_data.push_back(cp);
    }
    
    LOG_DEBUG("Carte de courbure simulée: {} points", curvature_data.size());
}

nlohmann::json CurvatureMap::export_heatmap() const {
    nlohmann::json heatmap;
    for (const auto& cp : curvature_data) {
        heatmap[std::to_string(cp.vertex_id)] = cp.mean_curvature;
    }
    return heatmap;
}

float CurvatureMap::get_elasticity_at_point(int vertex_id) const {
    if (vertex_id >= 0 && vertex_id < static_cast<int>(curvature_data.size())) {
        return curvature_data[vertex_id].max_stretch;
    }
    return 0.15f;  // Valeur par défaut
}

void CurvatureMap::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}