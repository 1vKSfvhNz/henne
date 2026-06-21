#include "henne_material.hpp"

HenneMaterial::HenneMaterial()
    : opacity(0.95f)
    , glossiness(0.4f) {}

nlohmann::json HenneMaterial::create_material(const std::string& color_name, float thickness) {
    nlohmann::json material;
    material["type"] = "henne";
    material["color"] = color_name;
    material["thickness"] = thickness;
    material["opacity"] = opacity;
    material["glossiness"] = glossiness;
    return material;
}

void HenneMaterial::set_opacity(float op) {
    opacity = std::clamp(op, 0.0f, 1.0f);
}

void HenneMaterial::set_glossiness(float gloss) {
    glossiness = std::clamp(gloss, 0.0f, 1.0f);
}