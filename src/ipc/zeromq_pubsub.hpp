#ifndef ZEROMQ_PUBSUB_HPP
#define ZEROMQ_PUBSUB_HPP

#include <zmq.hpp>
#include <thread>
#include <atomic>
#include <functional>
#include <nlohmann/json.hpp>
#include <chrono>

class ZeroMQHighSpeed {
public:
    ZeroMQHighSpeed() : context(1), running(false) {}
    
    bool init_publisher(int port = 5556) {
        publisher = zmq::socket_t(context, ZMQ_PUB);
        publisher.bind("tcp://*:" + std::to_string(port));
        // Alternative: IPC plus rapide
        // publisher.bind("ipc:///tmp/mihi_cn.ipc");
        return true;
    }
    
    bool init_subscriber(const std::string& endpoint = "tcp://localhost:5556") {
        subscriber = zmq::socket_t(context, ZMQ_SUB);
        subscriber.connect(endpoint);
        subscriber.setsockopt(ZMQ_SUBSCRIBE, "", 0);
        subscriber.setsockopt(ZMQ_RCVTIMEO, 10);  // 10ms timeout
        return true;
    }
    
    // Envoi ultra-rapide (sans copie)
    void publish_raw(const void* data, size_t size) {
        if (publisher) {
            zmq::message_t msg(data, size);
            publisher.send(msg, ZMQ_DONTWAIT);
        }
    }
    
    void publish_json(const nlohmann::json& json) {
        std::string str = json.dump();
        publish_raw(str.c_str(), str.size());
    }
    
    bool receive_raw(std::vector<uint8_t>& buffer, int timeout_ms = 0) {
        zmq::message_t msg;
        if (timeout_ms > 0) {
            zmq::pollitem_t items[] = {{subscriber, 0, ZMQ_POLLIN, 0}};
            zmq::poll(&items[0], 1, std::chrono::milliseconds(timeout_ms));
            if (!(items[0].revents & ZMQ_POLLIN)) return false;
        }
        
        if (subscriber.recv(msg, ZMQ_DONTWAIT)) {
            buffer.resize(msg.size());
            memcpy(buffer.data(), msg.data(), msg.size());
            return true;
        }
        return false;
    }
    
    void start_publish_loop(std::function<void(zmq::socket_t&)> callback, int frequency_hz = 1000) {
        running = true;
        publish_thread = std::thread([this, callback, frequency_hz]() {
            const auto period = std::chrono::microseconds(1000000 / frequency_hz);
            auto next_time = std::chrono::steady_clock::now();
            
            while (running) {
                callback(publisher);
                next_time += period;
                std::this_thread::sleep_until(next_time);
            }
        });
    }
    
    void stop() {
        running = false;
        if (publish_thread.joinable()) publish_thread.join();
    }
    
private:
    zmq::context_t context;
    zmq::socket_t publisher{context, ZMQ_PUB};
    zmq::socket_t subscriber{context, ZMQ_SUB};
    std::atomic<bool> running;
    std::thread publish_thread;
};

#endif