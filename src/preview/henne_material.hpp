#ifndef HENNE_MATERIAL_HPP
#define HENNE_MATERIAL_HPP

#include <string>
#include <nlohmann/json.hpp>

class HenneMaterial {
public:
    HenneMaterial();
    
    nlohmann::json create_material(const std::string& color_name, float thickness);
    void set_opacity(float opacity);
    void set_glossiness(float gloss);
    
private:
    float opacity;
    float glossiness;
};

#endif