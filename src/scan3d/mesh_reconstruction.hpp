#ifndef MESH_RECONSTRUCTION_HPP
#define MESH_RECONSTRUCTION_HPP

#include <vector>
#include <nlohmann/json.hpp>
#include "realsense_capture.hpp"

struct Triangle {
    int v1, v2, v3;
};

struct Mesh {
    std::vector<Point3D> vertices;
    std::vector<Triangle> triangles;
    nlohmann::json metadata;
};

class MeshReconstruction {
public:
    MeshReconstruction();
    
    Mesh reconstruct(const std::vector<Point3D>& point_cloud);
    nlohmann::json export_to_obj(const Mesh& mesh);
    
    void set_resolution(float resolution_mm);
    void set_simulation_mode(bool sim);
    
private:
    float resolution;
    bool simulation_mode;
    
    Mesh poisson_reconstruction(const std::vector<Point3D>& cloud);
    Mesh ball_pivoting(const std::vector<Point3D>& cloud);
};

#endif