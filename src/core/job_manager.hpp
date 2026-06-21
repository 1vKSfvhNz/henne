#ifndef JOB_MANAGER_HPP
#define JOB_MANAGER_HPP

#include <string>
#include <queue>
#include <mutex>
#include <chrono>
#include <nlohmann/json.hpp>

struct Job {
    std::string job_id;
    std::string zone_type;
    std::string motif_path;
    std::chrono::system_clock::time_point start_time;
    nlohmann::json result;
    float quality_score;
    bool completed;
};

class JobManager {
public:
    JobManager();
    
    std::string create_job(const std::string& zone, const std::string& motif);
    void update_job_result(const std::string& job_id, const nlohmann::json& result);
    void complete_job(const std::string& job_id, float quality);
    
    Job get_job(const std::string& job_id) const;
    std::vector<Job> get_recent_jobs(int count = 100) const;
    
    int get_queue_size() const;
    
private:
    mutable std::mutex mtx;
    std::queue<std::string> job_queue;
    std::unordered_map<std::string, Job> jobs;
    std::vector<std::string> job_history;
    
    std::string generate_job_id();
};

#endif