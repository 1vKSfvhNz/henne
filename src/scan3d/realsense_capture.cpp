#include "realsense_capture.hpp"
#include "../utils/logger.hpp"
#include <random>
#include <cmath>

RealSenseCapture::RealSenseCapture()
    : simulation_mode(true)
    , device_id(0)
    , width(640)
    , height(480) {}

RealSenseCapture::~RealSenseCapture() {}

bool RealSenseCapture::init(int id) {
    device_id = id;
    if (simulation_mode) {
        LOG_INFO("RealSense D455 [simulé] initialisé (device {})", id);
        generate_mock_cloud();
        return true;
    }
    // Code réel RealSense SDK ici
    LOG_WARN("Mode réel non implémenté - utiliser simulation");
    return false;
}

bool RealSenseCapture::capture_depth_image() {
    if (simulation_mode) {
        generate_mock_cloud();
        return true;
    }
    return false;
}

bool RealSenseCapture::capture_rgb_image() {
    if (simulation_mode) {
        return true;
    }
    return false;
}

void RealSenseCapture::generate_mock_cloud() {
    current_point_cloud.clear();
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis_x(-0.5, 0.5);
    std::uniform_real_distribution<> dis_y(-1.0, 1.0);
    std::uniform_real_distribution<> dis_z(0.0, 0.8);
    std::uniform_int_distribution<> dis_color(100, 200);
    
    // Génération d'un nuage simulant un avant-bras
    for (int i = 0; i < 5000; ++i) {
        Point3D p;
        p.x = dis_x(gen);
        p.y = dis_y(gen);
        // Forme cylindrique
        p.z = 0.5f + 0.3f * (1.0f - std::abs(p.x) / 0.5f);
        p.r = dis_color(gen);
        p.g = static_cast<uint8_t>(p.r * 0.8);
        p.b = static_cast<uint8_t>(p.r * 0.6);
        current_point_cloud.push_back(p);
    }
    
    LOG_DEBUG("Nuage mock généré: {} points", current_point_cloud.size());
}

std::vector<Point3D> RealSenseCapture::get_point_cloud() const {
    return current_point_cloud;
}

nlohmann::json RealSenseCapture::get_point_cloud_json() const {
    nlohmann::json json_cloud = nlohmann::json::array();
    for (const auto& p : current_point_cloud) {
        json_cloud.push_back({{"x", p.x}, {"y", p.y}, {"z", p.z}, {"r", p.r}, {"g", p.g}, {"b", p.b}});
    }
    return json_cloud;
}

void RealSenseCapture::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}

void RealSenseCapture::load_mock_scan(const std::string& filename) {
    LOG_INFO("Chargement scan mock depuis {}", filename);
    generate_mock_cloud();
}