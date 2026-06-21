#ifndef SPIRALNET_DEFORMER_HPP
#define SPIRALNET_DEFORMER_HPP

#include <string>
#include <vector>
#include <nlohmann/json.hpp>
#include "../scan3d/mesh_reconstruction.hpp"

struct DeformedPoint {
    float x, y, z;
    float original_u, original_v;
    float thickness_scale;
};

class SpiralNetDeformer {
public:
    SpiralNetDeformer();
    
    std::vector<DeformedPoint> deform(const nlohmann::json& svg_paths, 
                                       const Mesh& target_mesh,
                                       const nlohmann::json& curvature_map);
    
    nlohmann::json get_trajectory_json() const;
    
    void set_simulation_mode(bool sim);
    void load_model_weights(const std::string& model_path);
    
private:
    bool simulation_mode;
    std::vector<DeformedPoint> deformed_points;
    
    std::vector<DeformedPoint> simulate_deformation(const nlohmann::json& svg_paths,
                                                      const Mesh& mesh);
    std::vector<DeformedPoint> infer_with_onnx(const nlohmann::json& svg_paths,
                                                const Mesh& mesh);
};

#endif