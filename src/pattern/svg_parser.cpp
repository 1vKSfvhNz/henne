#include "svg_parser.hpp"
#include "../utils/logger.hpp"
#include <fstream>
#include <regex>
#include <random>

SVGParser::SVGParser()
    : simulation_mode(true) {}

std::vector<SVGPath> SVGParser::parse(const std::string& svg_file_path) {
    if (simulation_mode) {
        LOG_INFO("Parse SVG [simulé] depuis {}", svg_file_path);
        return parse_mock_svg();
    }
    return parse_real_svg(svg_file_path);
}

std::vector<SVGPath> SVGParser::parse_mock_svg() {
    std::vector<SVGPath> paths;
    
    // Génération d'un motif mandala simulé
    SVGPath mandala;
    mandala.thickness = 0.5f;
    mandala.color = "#8B5A2B";
    mandala.estimated_length_cm = 25.0f;
    
    // Cercles concentriques simulés
    for (float r = 0.2f; r <= 1.0f; r += 0.2f) {
        for (float angle = 0; angle < 2 * M_PI; angle += M_PI / 8) {
            BezierCurve curve;
            curve.x0 = r * cos(angle);
            curve.y0 = r * sin(angle);
            curve.x1 = r * cos(angle + M_PI / 16);
            curve.y1 = r * sin(angle + M_PI / 16);
            curve.x2 = curve.x1;
            curve.y2 = curve.y1;
            curve.x3 = r * cos(angle + M_PI / 8);
            curve.y3 = r * sin(angle + M_PI / 8);
            curve.is_cubic = false;
            mandala.curves.push_back(curve);
        }
    }
    
    paths.push_back(mandala);
    LOG_DEBUG("Mock SVG généré: {} courbes", mandala.curves.size());
    
    return paths;
}

std::vector<SVGPath> SVGParser::parse_real_svg(const std::string& file_path) {
    // Utilisation d'une bibliothèque comme nanosvg
    LOG_WARN("Parse réel non implémenté");
    return {};
}

nlohmann::json SVGParser::to_json(const std::vector<SVGPath>& paths) const {
    nlohmann::json json_paths = nlohmann::json::array();
    for (const auto& path : paths) {
        nlohmann::json json_path;
        json_path["thickness"] = path.thickness;
        json_path["color"] = path.color;
        json_path["length_cm"] = path.estimated_length_cm;
        
        nlohmann::json json_curves = nlohmann::json::array();
        for (const auto& curve : path.curves) {
            json_curves.push_back({
                {"x0", curve.x0}, {"y0", curve.y0},
                {"x1", curve.x1}, {"y1", curve.y1},
                {"x2", curve.x2}, {"y2", curve.y2},
                {"x3", curve.x3}, {"y3", curve.y3},
                {"is_cubic", curve.is_cubic}
            });
        }
        json_path["curves"] = json_curves;
        json_paths.push_back(json_path);
    }
    return json_paths;
}

void SVGParser::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}