#include "renderer.hpp"
#include "../utils/logger.hpp"

PreviewRenderer::PreviewRenderer()
    : simulation_mode(true)
    , width(1920)
    , height(1080)
    , henne_color{0.545f, 0.353f, 0.169f}  // #8B5A2B
    , aging_days(0) {}

bool PreviewRenderer::init(int w, int h) {
    width = w;
    height = h;
    if (simulation_mode) {
        LOG_INFO("Moteur de rendu 3D [simulé] - {}x{}", width, height);
        return true;
    }
    // OpenGL / Vulkan init
    return true;
}

void PreviewRenderer::render_mesh(const nlohmann::json& mesh, const nlohmann::json& trajectory) {
    current_mesh = mesh;
    if (simulation_mode) {
        render_simulation();
    }
}

void PreviewRenderer::set_henne_color(float r, float g, float b) {
    henne_color[0] = r;
    henne_color[1] = g;
    henne_color[2] = b;
    LOG_DEBUG("Couleur henné changée: RGB({:.2f},{:.2f},{:.2f})", r, g, b);
}

void PreviewRenderer::set_aging_days(int days) {
    aging_days = days;
    // Modifier l'apparence du henné selon l'âge
    if (days > 0) {
        henne_color[0] *= (1.0f - days * 0.05f);
        henne_color[1] *= (1.0f - days * 0.03f);
    }
    LOG_DEBUG("Vieillissement J+{}", days);
}

std::vector<uint8_t> PreviewRenderer::get_image() const {
    // Retourne une image simulée (noire)
    return std::vector<uint8_t>(width * height * 3, 128);
}

void PreviewRenderer::render_simulation() {
    // Simulation: rien à faire
    LOG_TRACE("Rendu simulé");
}

void PreviewRenderer::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}