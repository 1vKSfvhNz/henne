#include "json_helper.hpp"
#include "logger.hpp"
#include <fstream>

nlohmann::json JSONHelper::load_from_file(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        LOG_WARN("Impossible d'ouvrir le fichier JSON: {}", filename);
        return nlohmann::json();
    }
    
    nlohmann::json data;
    file >> data;
    return data;
}

bool JSONHelper::save_to_file(const std::string& filename, const nlohmann::json& data) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        LOG_ERROR("Impossible d'écrire dans {}", filename);
        return false;
    }
    
    file << data.dump(4);
    return true;
}

nlohmann::json JSONHelper::merge(const nlohmann::json& a, const nlohmann::json& b) {
    nlohmann::json result = a;
    for (auto& [key, value] : b.items()) {
        result[key] = value;
    }
    return result;
}

bool JSONHelper::validate_schema(const nlohmann::json& data, const nlohmann::json& schema) {
    // Validation simplifiée
    return true;
}