#include "logger.hpp"

std::ofstream Logger::file_stream;
LogLevel Logger::current_level = LogLevel::DEBUG;
std::mutex Logger::log_mutex;

void Logger::init(const std::string& log_file) {
    if (!log_file.empty()) {
        file_stream.open(log_file, std::ios::out | std::ios::app);
    }
    LOG_INFO("Logger initialisé");
}

void Logger::set_level(LogLevel level) {
    current_level = level;
}