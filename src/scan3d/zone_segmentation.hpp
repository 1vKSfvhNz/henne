#ifndef ZONE_SEGMENTATION_HPP
#define ZONE_SEGMENTATION_HPP

#include <string>
#include <vector>
#include <nlohmann/json.hpp>

struct ZoneMask {
    std::vector<int> vertex_indices;
    std::string zone_type;  // main, pied, avant_bras, jambe
    float confidence;
};

class ZoneSegmentation {
public:
    ZoneSegmentation();
    
    std::string classify_zone(const nlohmann::json& mesh);
    std::vector<ZoneMask> segment_avoid_zones(const nlohmann::json& mesh);
    nlohmann::json get_avoidance_mask() const;
    
    void set_simulation_mode(bool sim);
    
private:
    bool simulation_mode;
    nlohmann::json avoidance_mask;
    
    std::string rule_based_classification(const nlohmann::json& mesh);
    std::vector<ZoneMask> detect_cicatrices_grains(const nlohmann::json& mesh);
};

#endif