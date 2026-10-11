"""Isolated C++ proof for the real cover planner and prioritize body.

No Android, decoder, network, timer, queue worker or gameplay is exercised.
Generated source/executable remain outside the repository snapshot.
"""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess


def raw(path):
    return Path("\\\\?\\" + str(path.resolve())).read_bytes()


def text(path):
    return raw(path).decode("utf-8").replace("\r\n", "\n")


def definition(source, name):
    match = re.search(r"API void " + re.escape(name) + r"\([^\n]*?\)\{", source)
    assert match, name
    begin = source.index("{", match.start())
    end, depth = begin + 1, 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[match.start():end]


def run(arguments):
    result = subprocess.run([str(x) for x in arguments], capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--clang", type=Path, default=Path(r"C:\Program Files\LLVM\bin\clang++.exe"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    base = root.parent / "station-theme-room-download-r122-20261011"
    args.work.mkdir(parents=True, exist_ok=True)
    source = text(root / "frontend/station_frontend.cpp")
    baseline = text(base / "frontend/station_frontend.cpp")
    old_state = "std::vector<size_t> coverPlan;int64_t nextCoverSweep"
    new_state = "std::vector<size_t> coverPlan;size_t coverPlanBudget=9;int64_t nextCoverSweep"
    assert source.count(new_state) == 1
    current_body = definition(source, "StationCatalog_prioritize")
    baseline_body = definition(baseline, "StationCatalog_prioritize")
    normalized = source.replace(new_state, old_state).replace(current_body, baseline_body)
    normalized = normalized.replace("std::atomic<int> carouselStyle{0}; // Separate UI-only field; existing graphics snapshot stays identical.\n", "")
    start = normalized.index("API int StationCarousel_style()")
    end = normalized.index("API uint64_t StationGraphics_snapshot()", start)
    normalized = normalized[:start] + normalized[end:]
    assert normalized == baseline, "Unrelated frontend queue/reveal/cache/lifecycle change"
    guards = 1
    (args.work / "station_cover_plan.hpp").write_bytes(raw(root / "frontend/station_cover_plan.hpp"))
    # Compare the default-budget result against the exact R122 implementation.
    old_header = text(base / "frontend/station_cover_plan.hpp").replace("namespace station {", "namespace baseline {")
    (args.work / "baseline_cover_plan.hpp").write_text(old_header, encoding="utf-8")
    fixture = r'''
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
#include "station_cover_plan.hpp"
#include "baseline_cover_plan.hpp"
struct Item { std::string folder,platform; };
struct Catalog { std::vector<Item> items;std::vector<size_t> priorities; };
struct State { Catalog*owner=nullptr;std::vector<size_t> coverPlan;size_t coverPlanBudget=9;int64_t nextCoverSweep=71; } state;
static std::atomic<int> carouselStyle{0};
static std::atomic<uint64_t> graphicsState{127};
static unsigned resets=0,queues=0;
bool owned(Catalog*c){return c&&c==state.owner;}
void resetWarmWindow(Catalog*){++resets;}
void queueCovers(Catalog*){++queues;}
#define API
ACTUAL_PRIORITIZE
static unsigned long long checks=0,cases=0;
void check(bool ok){assert(ok);++checks;}
uint32_t rng=0x7319u;
uint32_t randomValue(){rng=rng*1664525u+1013904223u;return rng;}
std::vector<size_t> oracle(const std::vector<Item>&items,const std::vector<size_t>&priorities,size_t budget){
 budget=std::min<size_t>(13,budget);std::vector<size_t> result;
 for(size_t i:priorities)if(i<items.size()&&result.size()<budget&&std::find(result.begin(),result.end(),i)==result.end())result.push_back(i);
 if(result.empty())return result;size_t anchor=result[0];
 for(size_t step=1;step<=items.size()&&result.size()<budget;++step){size_t i=(anchor+step)%items.size();
  if(items[i].folder==items[anchor].folder&&items[i].platform==items[anchor].platform&&std::find(result.begin(),result.end(),i)==result.end())result.push_back(i);}
 return result;
}
void transition(Catalog&catalog,const std::vector<size_t>&indices,int style,uint64_t mask){
 ++cases;carouselStyle=style;graphicsState=mask;
 const size_t budget=style==2&&(mask&16u)?13:9;
 const std::vector<size_t> expected(indices.begin(),indices.begin()+std::min<size_t>(indices.size(),budget));
 const bool rebuild=expected!=catalog.priorities||budget!=state.coverPlanBudget;
 const unsigned beforeResets=resets,beforeQueues=queues;
 state.nextCoverSweep=71;
 StationCatalog_prioritize(&catalog,indices);
 check(catalog.priorities==expected);check(state.coverPlanBudget==budget);
 check(state.coverPlan==oracle(catalog.items,expected,budget));
 check(resets==beforeResets+(rebuild?1:0));check(queues==beforeQueues+1);
 check(state.nextCoverSweep==(rebuild?0:71));
}
int main(){
 // Empty/short/large catalogues, duplicate/out-of-range priorities, folder/platform boundaries,
 // all seven budgets, and default-call compatibility with the exact R122 header.
 for(size_t n=0;n<=180;++n)for(unsigned round=0;round<25;++round){
  ++cases;std::vector<Item> items;for(size_t i=0;i<n;++i)items.push_back({std::to_string(randomValue()%4),std::to_string(randomValue()%3)});
  std::vector<size_t> priorities;const unsigned count=randomValue()%35;
  for(unsigned p=0;p<count;++p)priorities.push_back(randomValue()%(n+5));
  check(station::coverPlan(items,priorities)==baseline::coverPlan(items,priorities));
  check(station::coverPlan(items,priorities,9)==baseline::coverPlan(items,priorities));
  for(size_t budget:std::vector<size_t>{0,1,8,9,10,13,99}){
   auto result=station::coverPlan(items,priorities,budget);check(result==oracle(items,priorities,budget));
   check(result.size()<=std::min<size_t>(budget,13));
  }
 }
 Catalog c;for(unsigned i=0;i<40;++i)c.items.push_back({"folder","system"});state.owner=&c;
 std::vector<size_t> input;for(unsigned i=0;i<16;++i)input.push_back(i);
 // Same indices across styles/masks/revisions: rebuild only on effective budget or indices.
 for(unsigned repetition=0;repetition<40;++repetition)for(int style:{0,1,2})for(uint64_t mask=0;mask<64;++mask){
  transition(c,input,style,mask|(uint64_t(repetition)<<8));
  transition(c,input,style,mask|(uint64_t(repetition+1)<<8));
 }
 // Same short indices even though the visible priority vector remains byte-identical.
 for(std::vector<size_t> small:std::vector<std::vector<size_t>>{{0},{0,1,2},{0,1,2,3,4,5,6,7,8},{}}){
  transition(c,small,0,16);transition(c,small,2,16);transition(c,small,2,0);transition(c,small,1,16);
 }
 // Ownership remains strict; no queue/reset/planner writes for another/null catalogue.
 Catalog other;const auto beforePlan=state.coverPlan;const auto beforeBudget=state.coverPlanBudget;
 const auto beforeResets=resets,beforeQueues=queues;
 StationCatalog_prioritize(&other,input);StationCatalog_prioritize(nullptr,input);
 check(other.priorities.empty());check(state.coverPlan==beforePlan);check(state.coverPlanBudget==beforeBudget);
 check(resets==beforeResets);check(queues==beforeQueues);
 std::cout<<cases<<" "<<checks;
}
'''.replace("ACTUAL_PRIORITIZE", current_body)
    (args.work / "cover-plan.cpp").write_text(fixture, encoding="utf-8")
    run([args.clang, "-std=c++17", "-O2", args.work / "cover-plan.cpp", "-o", args.work / "cover-plan.exe"])
    cases, checks = map(int, run([args.work / "cover-plan.exe"]).split())
    receipt = {
        "version": "R123", "utc": datetime.now(timezone.utc).isoformat(), "passed": True,
        "scope": "Isolated actual C++ planner/prioritize body; no Android/GPU/network/gameplay/thermal measurement",
        "checks": {"cases": cases, "actualCppChecks": checks, "frontendPreservationGuards": guards},
        "budget": {"default": 9, "sideWithEffectiveCellEffects": 13, "maximum": 13,
                   "rebuildOnBudgetChangeWithIdenticalPriorities": True},
        "preserved": ["single cover queue", "retry/backoff", "warm reveal timing", "warm cache window", "lifecycle", "ownership"],
        "sources": {str(path.relative_to(root)).replace("\\", "/"): hashlib.sha256(raw(path)).hexdigest()
                    for path in [root / "frontend/station_frontend.cpp", root / "frontend/station_cover_plan.hpp", Path(__file__).resolve()]}
    }
    (root / "evidence/side-cover-plan-r123.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt["checks"]))


if __name__ == "__main__":
    main()
