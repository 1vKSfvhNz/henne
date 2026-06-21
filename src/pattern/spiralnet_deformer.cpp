#include "spiralnet_deformer.hpp"
#include "../utils/logger.hpp"
#include <random>
#include <cmath>

SpiralNetDeformer::SpiralNetDeformer()
    : simulation_mode(true) {}

std::vector<DeformedPoint> SpiralNetDeformer::deform(const nlohmann::json& svg_paths,
                                                      const Mesh& target_mesh,
                                                      const nlohmann::json& curvature_map) {
    if (simulation_mode) {
        LOG_INFO("Déformation SpiralNet++ [simulée]");
        return simulate_deformation(svg_paths, target_mesh);
    }
    return infer_with_onnx(svg_paths, target_mesh);
}

std::vector<DeformedPoint> SpiralNetDeformer::simulate_deformation(const nlohmann::json& svg_paths,
                                                                     const Mesh& mesh) {
    deformed_points.clear();
    
    // Simulation: projeter les points SVG sur la surface du mesh
    // Créer une trajectoire 3D simulée
    
    int num_points = 500;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis_x(-0.4, 0.4);
    std::uniform_real_distribution<> dis_y(-0.8, 0.8);
    std::normal_distribution<> dis_z(0.5, 0.1);
    
    for (int i = 0; i < num_points; ++i) {
        DeformedPoint p;
        p.x = dis_x(gen);
        p.y = dis_y(gen);
        p.z = 0.5f + 0.2f * (1.0f - std::abs(p.x) / 0.4f);
        p.original_u = (p.x + 0.4f) / 0.8f;
        p.original_v = (p.y + 0.8f) / 1.6f;
        p.thickness_scale = 1.0f;
        deformed_points.push_back(p);
    }
    
    // Trier pour créer une trajectoire continue
    std::sort(deformed_points.begin(), deformed_points.end(),
              [](const DeformedPoint& a, const DeformedPoint& b) {
                  return std::hypot(a.x, a.y) < std::hypot(b.x, b.y);
              });
    
    LOG_DEBUG("Trajectoire déformée: {} points", deformed_points.size());
    
    return deformed_points;
}

std::vector<DeformedPoint> SpiralNetDeformer::infer_with_onnx(const nlohmann::json& svg_paths,
                                                               const Mesh& mesh) {
    // Intégration ONNX Runtime
    LOG_WARN("Inférence ONNX non implémentée - fallback simulation");
    return simulate_deformation(svg_paths, mesh);
}

nlohmann::json SpiralNetDeformer::get_trajectory_json() const {
    nlohmann::json traj = nlohmann::json::array();
    for (const auto& p : deformed_points) {
        traj.push_back({
            {"x", p.x}, {"y", p.y}, {"z", p.z},
            {"u", p.original_u}, {"v", p.original_v},
            {"thickness", p.thickness_scale}
        });
    }
    return traj;
}

void SpiralNetDeformer::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}

void SpiralNetDeformer::load_model_weights(const std::string& model_path) {
    LOG_INFO("Chargement modèle depuis {} [simulé]", model_path);
}