#ifndef JSON_HELPER_HPP
#define JSON_HELPER_HPP

#include <nlohmann/json.hpp>
#include <string>
#include <fstream>

class JSONHelper {
public:
    static nlohmann::json load_from_file(const std::string& filename);
    static bool save_to_file(const std::string& filename, const nlohmann::json& data);
    
    static nlohmann::json merge(const nlohmann::json& a, const nlohmann::json& b);
    static bool validate_schema(const nlohmann::json& data, const nlohmann::json& schema);
};

#endif