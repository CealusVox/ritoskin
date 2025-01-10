#ifndef THREADPOOL_H
#define THREADPOOL_H

#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <functional>
#include <future>
#include <atomic>

class ThreadPool {
public:
    explicit ThreadPool(size_t threads);
    ~ThreadPool();

    // Add new work item to the pool
    template<class F, class... Args>
    auto enqueue(F&& f, Args&&... args)
        -> std::future<typename std::invoke_result_t<F, Args...>>;

    // Get the number of remaining tasks
    size_t get_task_count();

private:
    // Workers
    std::vector<std::thread> workers;
    // Task queue
    std::queue<std::function<void()>> tasks;

    // Synchronization
    std::mutex queue_mutex;
    std::condition_variable condition;
    std::atomic<bool> stop;
};

inline ThreadPool::ThreadPool(size_t threads) : stop(false) {
    for(size_t i = 0; i < threads; ++i) {
        workers.emplace_back([this]() {
            for(;;) {
                std::function<void()> task;

                {
                    std::unique_lock<std::mutex> lock(this->queue_mutex);
                    this->condition.wait(lock, [this]() { return this->stop.load() || !this->tasks.empty(); });

                    if(this->stop.load() && this->tasks.empty())
                        return;

                    task = std::move(this->tasks.front());
                    this->tasks.pop();
                }

                task();
            }
        });
    }
}

inline ThreadPool::~ThreadPool() {
    stop.store(true);
    condition.notify_all();

    for(std::thread &worker : workers) {
        worker.join();
    }
}

template<class F, class... Args>
auto ThreadPool::enqueue(F&& f, Args&&... args)
    -> std::future<typename std::invoke_result_t<F, Args...>> {
    using return_type = typename std::invoke_result_t<F, Args...>;

    auto task = std::make_shared<std::packaged_task<return_type()>>(
                    std::bind(std::forward<F>(f), std::forward<Args>(args)...)
                );

    std::future<return_type> result = task->get_future();
    {
        std::lock_guard<std::mutex> lock(queue_mutex);

        if(stop.load())
            throw std::runtime_error("enqueue on stopped ThreadPool");

        tasks.emplace([task]() {
            (*task)();
        });
    }

    condition.notify_one();
    return result;
}

inline size_t ThreadPool::get_task_count() {
    std::lock_guard<std::mutex> lock(queue_mutex);
    return tasks.size();
}

#endif // THREADPOOL_H
