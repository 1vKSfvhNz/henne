#ifndef CURVATURE_MAP_HPP
#define CURVATURE_MAP_HPP

#include <vector>
#include <nlohmann/json.hpp>

struct CurvaturePoint {
    int vertex_id;
    float mean_curvature;
    float gaussian_curvature;
    float max_stretch;  // Élasticité maximale
};

class CurvatureMap {
public:
    CurvatureMap();
    
    std::vector<CurvaturePoint> compute_curvature(const nlohmann::json& mesh);
    nlohmann::json export_heatmap() const;
    
    float get_elasticity_at_point(int vertex_id) const;
    
    void set_simulation_mode(bool sim);
    
private:
    bool simulation_mode;
    std::vector<CurvaturePoint> curvature_data;
    
    void compute_mock_curvature(const nlohmann::json& mesh);
};

#endif