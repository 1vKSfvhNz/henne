#ifndef SVG_PARSER_HPP
#define SVG_PARSER_HPP

#include <string>
#include <vector>
#include <nlohmann/json.hpp>

struct BezierCurve {
    float x0, y0;
    float x1, y1;
    float x2, y2;
    float x3, y3;  // Pour cubic bezier
    bool is_cubic;
};

struct SVGPath {
    std::vector<BezierCurve> curves;
    float thickness;
    std::string color;
    float estimated_length_cm;
};

class SVGParser {
public:
    SVGParser();
    
    std::vector<SVGPath> parse(const std::string& svg_file_path);
    nlohmann::json to_json(const std::vector<SVGPath>& paths) const;
    
    void set_simulation_mode(bool sim);
    
private:
    bool simulation_mode;
    
    std::vector<SVGPath> parse_mock_svg();
    std::vector<SVGPath> parse_real_svg(const std::string& file_path);
};

#endif