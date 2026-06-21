#ifndef LOGGER_HPP
#define LOGGER_HPP

#include <string>
#include <iostream>
#include <fstream>
#include <mutex>
#include <chrono>
#include <sstream>
#include <iomanip>

enum class LogLevel {
    DEBUG,
    INFO,
    WARN,
    ERROR
};

class Logger {
public:
    static void init(const std::string& log_file = "");
    static void set_level(LogLevel level);
    
    template<typename... Args>
    static void debug(const std::string& format, Args... args) {
        log(LogLevel::DEBUG, format, args...);
    }
    
    template<typename... Args>
    static void info(const std::string& format, Args... args) {
        log(LogLevel::INFO, format, args...);
    }
    
    template<typename... Args>
    static void warn(const std::string& format, Args... args) {
        log(LogLevel::WARN, format, args...);
    }
    
    template<typename... Args>
    static void error(const std::string& format, Args... args) {
        log(LogLevel::ERROR, format, args...);
    }
    
private:
    static std::ofstream file_stream;
    static LogLevel current_level;
    static std::mutex log_mutex;
    
    template<typename... Args>
    static void log(LogLevel level, const std::string& format, Args... args) {
        if (level < current_level) return;
        
        std::lock_guard<std::mutex> lock(log_mutex);
        
        std::string level_str;
        switch(level) {
            case LogLevel::DEBUG: level_str = "DEBUG"; break;
            case LogLevel::INFO:  level_str = "INFO";  break;
            case LogLevel::WARN:  level_str = "WARN";  break;
            case LogLevel::ERROR: level_str = "ERROR"; break;
        }
        
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;
        
        std::stringstream ss;
        ss << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S");
        ss << '.' << std::setfill('0') << std::setw(3) << ms.count();
        
        std::string message = format_string(format, args...);
        std::string log_line = "[" + ss.str() + "] [" + level_str + "] " + message;
        
        std::cout << log_line << std::endl;
        if (file_stream.is_open()) {
            file_stream << log_line << std::endl;
            file_stream.flush();
        }
    }
    
    template<typename T>
    static std::string to_string(T value) {
        std::stringstream ss;
        ss << value;
        return ss.str();
    }
    
    static std::string format_string(const std::string& format) {
        return format;
    }
    
    template<typename T, typename... Args>
    static std::string format_string(const std::string& format, T first, Args... rest) {
        size_t pos = format.find("{}");
        if (pos == std::string::npos) return format;
        
        std::string result = format.substr(0, pos) + to_string(first) + format.substr(pos + 2);
        return format_string(result, rest...);
    }
};

#define LOG_DEBUG(...) Logger::debug(__VA_ARGS__)
#define LOG_INFO(...)  Logger::info(__VA_ARGS__)
#define LOG_WARN(...)  Logger::warn(__VA_ARGS__)
#define LOG_ERROR(...) Logger::error(__VA_ARGS__)

#endif