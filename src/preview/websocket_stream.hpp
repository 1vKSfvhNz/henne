#ifndef WEBSOCKET_STREAM_HPP
#define WEBSOCKET_STREAM_HPP

#include <string>
#include <functional>
#include <nlohmann/json.hpp>

class WebSocketStream {
public:
    WebSocketStream();
    ~WebSocketStream();
    
    bool connect(const std::string& url);
    void disconnect();
    
    void send_json(const nlohmann::json& data);
    void send_binary(const std::vector<uint8_t>& data);
    
    void set_on_message(std::function<void(const nlohmann::json&)> callback);
    
    void set_simulation_mode(bool sim);
    
private:
    bool simulation_mode;
    bool connected;
    std::function<void(const nlohmann::json&)> message_callback;
    
    void simulation_send(const nlohmann::json& data);
};

#endif