#ifndef PREVIEW_RENDERER_HPP
#define PREVIEW_RENDERER_HPP

#include <string>
#include <vector>
#include <nlohmann/json.hpp>

class PreviewRenderer {
public:
    PreviewRenderer();
    
    bool init(int width, int height);
    void render_mesh(const nlohmann::json& mesh, const nlohmann::json& trajectory);
    void set_henne_color(float r, float g, float b);
    void set_aging_days(int days);
    
    std::vector<uint8_t> get_image() const;
    
    void set_simulation_mode(bool sim);
    
private:
    bool simulation_mode;
    int width, height;
    float henne_color[3];
    int aging_days;
    nlohmann::json current_mesh;
    
    void render_simulation();
};

#endif