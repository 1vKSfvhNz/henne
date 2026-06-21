#ifndef MODEL_INFERENCE_HPP
#define MODEL_INFERENCE_HPP

#include <string>
#include <vector>
#include <nlohmann/json.hpp>

class ModelInference {
public:
    ModelInference();
    
    bool load_model(const std::string& model_path);
    nlohmann::json infer(const nlohmann::json& input);
    
    void set_simulation_mode(bool sim);
    
    // Modèles spécifiques
    nlohmann::json pointnet_infer(const std::vector<float>& point_cloud);
    nlohmann::json spiralnet_infer(const nlohmann::json& svg, const nlohmann::json& mesh);
    nlohmann::json lstm_infer(const std::vector<float>& sensor_history);
    
private:
    bool simulation_mode;
    std::string current_model_path;
    
    nlohmann::json simulate_inference(const nlohmann::json& input);
};

#endif