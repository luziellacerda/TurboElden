// Diagnostic model with the exact production protocol, not an Android benchmark.
// Changes no app, core option, server binding or network setting.
#define main existing_protocol_probe_main
#include "../../psx-online/tests/protocol_probe.cpp"
#undef main
#include <queue>
#include <fstream>
#include <sstream>
std::vector<std::pair<std::uint64_t,std::uint64_t>> measured;
std::uint64_t proxyLatency(std::uint64_t now) {
 auto at=now%(measured.back().first+100);
 auto i=std::upper_bound(measured.begin(),measured.end(),at,[](auto n,const auto& r){return n<r.first;});
 if(i!=measured.begin())--i;return i->second/2;
}

struct Flight {
    std::uint64_t due, order;
    bool toHost;
    Bytes packet;
};
struct Later {
    bool operator()(const Flight& a, const Flight& b) const {
        return std::tie(a.due, a.order) > std::tie(b.due, b.order);
    }
};
struct OwnerClock {
    std::uint64_t next{}, done{};
    bool executing{};
    Lease lease{};
    unsigned runs{}, waits{};
};

void measure(unsigned delay, unsigned rttMs, unsigned workMs, unsigned phaseUs) {
    Pair pair(4096, delay);
    pair.init();
    OwnerClock host, guest;
    guest.next = phaseUs;
    std::priority_queue<Flight, std::vector<Flight>, Later> flights;
    std::uint64_t order = 0;
    std::uint64_t lastDue[2]{};
    unsigned beforeHost = 0, beforeGuest = 0;
    unsigned beforeHostWait = 0, beforeGuestWait = 0;
    const std::uint64_t duration = rttMs ? 5000000 : 30000000;
    const std::uint64_t warmup = rttMs ? 1000000 : 2000000;
    constexpr std::uint64_t period = 16667;
    auto finish = [&](Session& session, OwnerClock& owner, std::uint64_t now) {
        if (!owner.executing || owner.done > now) return;
        eq(session.ownerComplete(owner.lease), Result::Ok, "real protocol frame completed");
        owner.executing = false;
        ++owner.runs;
    };
    auto begin = [&](Session& session, OwnerClock& owner, unsigned slot, std::uint64_t now) {
        if (owner.executing || now < owner.next) return;
        owner.next = now + period;
        eq(session.ownerCheckpoint(), Result::Ok, "live native owner checkpoint");
        if (session.needsLocalSample())
            eq(session.ownerSampleLocal(slot == 1 ? 0x20 : 0x40), Result::Ok, "once-only original input");
        auto result = session.ownerBegin(owner.lease);
        if (result == Result::Wait) { ++owner.waits; return; }
        eq(result, Result::Ok, "native owner lease");
        owner.executing = true;
        owner.done = now + workMs * 1000;
    };
    for (std::uint64_t now = 0; now < duration; now += 100) {
        if (now == warmup) {
            beforeHost = host.runs; beforeGuest = guest.runs;
            beforeHostWait = host.waits; beforeGuestWait = guest.waits;
        }
        while (!flights.empty() && flights.top().due <= now) {
            auto f = flights.top(); flights.pop();
            pair.accept(f.toHost ? pair.h : pair.g, f.toHost ? 2 : 1, std::move(f.packet));
        }
        finish(pair.h, host, now); finish(pair.g, guest, now);
        begin(pair.h, host, 1, now); begin(pair.g, guest, 2, now);
        for (unsigned side = 0; side < 2; ++side) for (;;) {
            auto packet = (side ? pair.g : pair.h).takeOutgoing();
            if (packet.empty()) break;
            auto due=now+(rttMs ? rttMs*500 : proxyLatency(now));
            due=std::max(due,lastDue[side]);lastDue[side]=due;
            flights.push({due, order++, side == 1, std::move(packet)});
        }
        pair.clearEvents();
        check(!pair.h.status().failed && !pair.g.status().failed, "no failure or network loss");
        check(guest.runs <= host.runs, "guest never ahead of authoritative host");
    }
    std::cout << "{\"inputDelay\":" << delay << ",\"peerRttMs\":" << rttMs
              << ",\"coreWorkMs\":" << workMs << ",\"guestPhaseUs\":" << phaseUs
              << ",\"hostFps\":" << (host.runs - beforeHost) / double((duration-warmup)/1000000)
              << ",\"guestFps\":" << (guest.runs - beforeGuest) / double((duration-warmup)/1000000)
              << ",\"hostWaits\":" << host.waits - beforeHostWait
              << ",\"guestWaits\":" << guest.waits - beforeGuestWait
              << ",\"packetLoss\":0,\"emulatorRun\":false}\n";
}

int main(int argc,char** argv) {
    try {
        if(argc==2){std::ifstream f(argv[1]);std::uint64_t at,rtt;while(f>>at>>rtt)measured.emplace_back(at,rtt);check(measured.size()>100,"timing-only proxy supplied");}
        if(!measured.empty()) for(unsigned delay:{4u,6u,8u}) for(unsigned work:{3u,9u,13u}) for(unsigned phase:{4000u,12000u}) measure(delay,0,work,phase);
        for (unsigned delay : {4u, 6u, 8u})
            for (unsigned rtt : {10u, 40u, 60u, 100u})
                for (unsigned work : {3u, 9u, 13u})
                    for (unsigned phase : {4000u, 12000u})
                        measure(delay, rtt, work, phase);
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
