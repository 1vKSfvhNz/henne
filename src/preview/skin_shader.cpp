#include "skin_shader.hpp"

SkinShader::SkinShader()
    : diffuse_strength(0.8f)
    , specular_strength(0.3f)
    , subsurface_scattering(0.15f) {}

nlohmann::json SkinShader::apply_skin(const nlohmann::json& mesh, const std::string& skin_type) {
    // Simulation: retourner le mesh inchangé
    nlohmann::json result = mesh;
    result["shader_applied"] = "skin";
    result["skin_type"] = skin_type;
    return result;
}

void SkinShader::set_parameters(float diffuse, float specular, float subsurface) {
    diffuse_strength = diffuse;
    specular_strength = specular;
    subsurface_scattering = subsurface;
}