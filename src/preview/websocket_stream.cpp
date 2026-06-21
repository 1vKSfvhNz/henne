#include "websocket_stream.hpp"
#include "../utils/logger.hpp"

WebSocketStream::WebSocketStream()
    : simulation_mode(true)
    , connected(false) {}

WebSocketStream::~WebSocketStream() {
    disconnect();
}

bool WebSocketStream::connect(const std::string& url) {
    if (simulation_mode) {
        LOG_INFO("WebSocket [simulé] connecté à {}", url);
        connected = true;
        return true;
    }
    // Implémentation réelle websocketpp
    return false;
}

void WebSocketStream::disconnect() {
    connected = false;
    LOG_INFO("WebSocket déconnecté");
}

void WebSocketStream::send_json(const nlohmann::json& data) {
    if (simulation_mode && connected) {
        simulation_send(data);
    }
}

void WebSocketStream::send_binary(const std::vector<uint8_t>& data) {
    if (simulation_mode && connected) {
        LOG_TRACE("Envoi binaire: {} bytes", data.size());
    }
}

void WebSocketStream::simulation_send(const nlohmann::json& data) {
    LOG_TRACE("WebSocket envoi: {}", data.dump().substr(0, 100));
}

void WebSocketStream::set_on_message(std::function<void(const nlohmann::json&)> callback) {
    message_callback = callback;
}

void WebSocketStream::set_simulation_mode(bool sim) {
    simulation_mode = sim;
}