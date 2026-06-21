#include "model_inference.hpp"
#include "../utils/logger.hpp"
#include <random>

ModelInference::ModelInference()
    : simulation_mode(true) {}

bool ModelInference::load_model(const std::string& model_path) {
    current_model_path = model_path;
    if (simulation_mode) {
        LOG_INFO("Modèle chargé (simulation): {}", model_path);
        return true;
    }
    // ONNX Runtime loading
    LOG_WARN("Chargement ONNX réel non implémenté");
    return true;
}

nlohmann::json ModelInference::infer(const nlohmann::json& input) {
    if (simulation_mode) {
        return simulate_inference(input);
    }
    return {};
}

nlohmann::json ModelInference::pointnet_infer(const std::vector<float>& point_cloud) {
    nlohmann::json output;
    output["num_points"] = point_cloud.size() / 3;
    output["mesh_quality"] = 0.95f;
    output["reconstruction_time_ms"] = 350.0f;
    return output;
}

nlohmann::json ModelInference::spiralnet_infer(const nlohmann::json& svg, const nlohmann::json& mesh) {
    nlohmann::json output;
    output["num_deformed_points"] = 500;
    output["deformation_error"] = 0.03f;
    output["inference_time_ms"] = 480.0f;
    return output;
}

nlohmann::json ModelInference::lstm_infer(const std::vector<float>& sensor_history) {
    nlohmann::json output;
    output["predicted_flow"] = 35.0f;
    output["predicted_pressure"] = 2.1f;
    output["confidence"] = 0.92f;
    return output;
}

nlohmann::json ModelInference::simulate_inference(const nlohmann::json& input) {
    static std::random_device rd;
    static std::mt19937 gen(rd());
    static std::normal_distribution<> noise(0.0, 0.02);
    
    nlohmann::json output;
    output["success"] = true;
    output["confidence"] = 0.85f + noise(gen);
    output["latency_ms"] = 25.0f + noise(gen) * 10;
    return output;
}

void ModelInference::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}