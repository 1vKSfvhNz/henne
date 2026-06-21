#include "job_manager.hpp"
#include <random>
#include <sstream>
#include <iomanip>

JobManager::JobManager() {}

std::string JobManager::generate_job_id() {
    static std::random_device rd;
    static std::mt19937 gen(rd());
    static std::uniform_int_distribution<> dis(0, 999999);
    
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    
    std::stringstream ss;
    ss << "JOB_" << time_t << "_" << std::setw(6) << std::setfill('0') << dis(gen);
    return ss.str();
}

std::string JobManager::create_job(const std::string& zone, const std::string& motif) {
    std::lock_guard<std::mutex> lock(mtx);
    
    Job job;
    job.job_id = generate_job_id();
    job.zone_type = zone;
    job.motif_path = motif;
    job.start_time = std::chrono::system_clock::now();
    job.completed = false;
    job.quality_score = 0.0f;
    
    jobs[job.job_id] = job;
    job_queue.push(job.job_id);
    
    return job.job_id;
}

void JobManager::update_job_result(const std::string& job_id, const nlohmann::json& result) {
    std::lock_guard<std::mutex> lock(mtx);
    if (jobs.find(job_id) != jobs.end()) {
        jobs[job_id].result = result;
    }
}

void JobManager::complete_job(const std::string& job_id, float quality) {
    std::lock_guard<std::mutex> lock(mtx);
    if (jobs.find(job_id) != jobs.end()) {
        jobs[job_id].completed = true;
        jobs[job_id].quality_score = quality;
        job_history.push_back(job_id);
    }
}

Job JobManager::get_job(const std::string& job_id) const {
    std::lock_guard<std::mutex> lock(mtx);
    if (jobs.find(job_id) != jobs.end()) {
        return jobs.at(job_id);
    }
    return Job{};
}

std::vector<Job> JobManager::get_recent_jobs(int count) const {
    std::lock_guard<std::mutex> lock(mtx);
    std::vector<Job> recent;
    int start = std::max(0, static_cast<int>(job_history.size()) - count);
    for (int i = start; i < static_cast<int>(job_history.size()); ++i) {
        recent.push_back(jobs.at(job_history[i]));
    }
    return recent;
}

int JobManager::get_queue_size() const {
    std::lock_guard<std::mutex> lock(mtx);
    return static_cast<int>(job_queue.size());
}