#ifndef SKIN_SHADER_HPP
#define SKIN_SHADER_HPP

#include <nlohmann/json.hpp>

class SkinShader {
public:
    SkinShader();
    
    nlohmann::json apply_skin(const nlohmann::json& mesh, 
                               const std::string& skin_type = "default");
    
    void set_parameters(float diffuse, float specular, float subsurface);
    
private:
    float diffuse_strength;
    float specular_strength;
    float subsurface_scattering;
};

#endif