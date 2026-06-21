#include "mesh_reconstruction.hpp"
#include "../utils/logger.hpp"
#include <random>

MeshReconstruction::MeshReconstruction()
    : resolution(0.2f)
    , simulation_mode(true) {}

Mesh MeshReconstruction::reconstruct(const std::vector<Point3D>& point_cloud) {
    if (simulation_mode) {
        LOG_INFO("Reconstruction 3D [simulée] - {} points", point_cloud.size());
        return poisson_reconstruction(point_cloud);
    }
    return ball_pivoting(point_cloud);
}

Mesh MeshReconstruction::poisson_reconstruction(const std::vector<Point3D>& cloud) {
    Mesh mesh;
    
    // Simulation simple : créer un maillage à partir du nuage
    // Dans la réalité, on utiliserait libigl ou Open3D
    
    // Copier tous les points comme vertices
    mesh.vertices = cloud;
    
    // Générer des triangles simulés (connectivité naïve)
    for (size_t i = 0; i + 2 < cloud.size(); i += 3) {
        Triangle t;
        t.v1 = static_cast<int>(i);
        t.v2 = static_cast<int>(i + 1);
        t.v3 = static_cast<int>(i + 2);
        mesh.triangles.push_back(t);
    }
    
    mesh.metadata["num_vertices"] = mesh.vertices.size();
    mesh.metadata["num_triangles"] = mesh.triangles.size();
    mesh.metadata["resolution_mm"] = resolution;
    
    LOG_DEBUG("Maillage généré: {} vertices, {} triangles", 
              mesh.vertices.size(), mesh.triangles.size());
    
    return mesh;
}

Mesh MeshReconstruction::ball_pivoting(const std::vector<Point3D>& cloud) {
    // Version simplifiée - identique pour la simulation
    return poisson_reconstruction(cloud);
}

nlohmann::json MeshReconstruction::export_to_obj(const Mesh& mesh) {
    nlohmann::json obj_data;
    obj_data["vertices"] = nlohmann::json::array();
    obj_data["faces"] = nlohmann::json::array();
    
    for (const auto& v : mesh.vertices) {
        obj_data["vertices"].push_back({v.x, v.y, v.z});
    }
    
    for (const auto& t : mesh.triangles) {
        obj_data["faces"].push_back({t.v1, t.v2, t.v3});
    }
    
    return obj_data;
}

void MeshReconstruction::set_resolution(float resolution_mm) {
    resolution = resolution_mm;
}

void MeshReconstruction::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}