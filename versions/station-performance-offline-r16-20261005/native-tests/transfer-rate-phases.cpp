#include <cassert>
#include <cmath>
#include <iostream>
#include <map>
#include <string>
#include "../client/src/native/station_transfer_rate.hpp"

struct Progress { bool active = true; int64_t received = 0, total = -1; };
struct Job { Progress progress; int result = 0; std::string message = "Baixando"; double networkBytesPerSecond = 0; };

int main() {
    int checks = 0;
    const auto check = [&](bool value) { assert(value); ++checks; };
    station::TransferRate rate;
    check(rate.observe(0, 10000000, 1000) == 0);
    check(rate.observe(100000, 10000000, 1100) == 0);
    check(std::abs(rate.observe(2000000, 10000000, 1500) - 4000000.0) < 1);
    check(std::abs(rate.observe(4000000, 10000000, 2000) - 4000000.0) < 1);
    check(rate.observe(0, 10000000, 2100) == 0);
    check(std::abs(rate.observe(1000000, 10000000, 3100) - 1000000.0) < 1);
    check(rate.observe(2000000, 20000000, 3200) == 0);
    check(rate.observe(3000000, 20000000, 3000) == 0);
    check(std::abs(rate.observe(4000000, 20000000, 4000) - 1000000.0) < 1);
    // Any regression resets, even while the clock remains above the first timestamp.
    check(rate.observe(4500000, 20000000, 3500) == 0);
    check(std::abs(rate.observe(5000000, 20000000, 4000) - 1000000.0) < 1);
    check(std::abs(rate.observe(5000000, 20000000, 4500) - 500000.0) < 1);

    using Phase = station::TransferPhase;
    check(station::transferPhase(true, 0, "Baixando") == Phase::Downloading);
    check(station::transferPhase(true, 0, "Preparando") == Phase::Preparing);
    check(station::transferPhase(true, 0, "Conferindo arquivo já baixado") == Phase::Preparing);
    check(station::transferPhase(true, 0, "Verificando integridade") == Phase::Preparing);
    check(station::transferPhase(true, 0, "Aguardando autorização") == Phase::Waiting);
    check(station::transferPhase(false, 1, "Instalado") == Phase::Unknown);
    check(station::transferPhase(true, 3, "Baixando") == Phase::Unknown);
    check(station::transferPhase(true, 0, nullptr) == Phase::Unknown);

    std::map<std::string, Job> jobs;
    jobs["active"].progress = {true, 500, 1000};
    jobs["active"].networkBytesPerSecond = 42;
    jobs["old"].progress = {false, 500, 1000};
    jobs["old"].result = 1;
    std::string selected;
    check(station::exactActiveJob(jobs, selected, 500, 1000) == &jobs.at("active"));
    check(station::exactActiveJob(jobs, selected, 501, 1000) == nullptr);
    check(station::exactActiveJob(jobs, selected, 500, 1001) == nullptr);
    jobs["second"].progress = {true, 500, 1000};
    jobs["second"].message = "Preparando";
    check(station::exactActiveJob(jobs, selected, 500, 1000) == nullptr);
    selected = "active";
    check(station::exactActiveJob(jobs, selected, 500, 1000) == &jobs.at("active"));
    selected = "second";
    const Job* preparing = station::exactActiveJob(jobs, selected, 500, 1000);
    check(preparing == &jobs.at("second"));
    check(station::transferPhase(preparing->progress.active, preparing->result, preparing->message.c_str()) == Phase::Preparing);
    selected = "old";
    check(station::exactActiveJob(jobs, selected, 500, 1000) == nullptr);
    selected = "absent";
    check(station::exactActiveJob(jobs, selected, 500, 1000) == nullptr);
    selected = "active";
    check(station::exactActiveJob(jobs, selected, 501, 1000) == nullptr);
    jobs["active"].result = 3;
    check(station::exactActiveJob(jobs, selected, 500, 1000) == nullptr);
    jobs.clear(); selected.clear();
    check(station::exactActiveJob(jobs, selected, 500, 1000) == nullptr);
    std::cout << "PASS " << checks << " native transfer rate, phase and exact job checks\n";
}
