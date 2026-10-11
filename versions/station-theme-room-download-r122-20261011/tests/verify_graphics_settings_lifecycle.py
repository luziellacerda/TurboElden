"""Execute the production settings-close routines with the real touch gesture.

Only JNI/GuiStore clock and close callbacks are stubbed. This proves gesture
reset ownership; it does not assert Android visual, input-device or thermal QA.
Generated native sources/binaries stay in the ignored evidence/led-isolated.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/led-isolated"
OUT.mkdir(parents=True, exist_ok=True)
SETTINGS = ROOT / "native/d0/native_settings.h"
GESTURE = ROOT / "native/d0/station_theme_switch_state.h"
source = SETTINGS.read_text(encoding="utf-8")


def function(name):
    start = source.index("static void " + name + "(")
    opening = source.index("{", start)
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise AssertionError("Incomplete production function " + name)


request = function("requestSettingsClose")
closed = function("settingsClosedHook")
# Execute the reset/owner-assignment prefix from the production owner branch;
# label construction/layout itself is outside this isolated lifecycle probe.
owner_match = re.search(
    r"if\(settingsBackOwner!=p\)\{settingsEffectsGesture=\{\};settingsBackOwner=p;",
    source,
)
assert owner_match, "Missing production owner-change gesture reset"
owner_prefix = owner_match.group(0)

program = r'''
#include <cassert>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include "../../native/d0/station_theme_palette.h"
#include "../../native/d0/station_theme_switch_state.h"
using B=unsigned char;
using V=void(*)(void*);
template<class T>T& at(void* p,unsigned offset){return *reinterpret_cast<T*>(static_cast<B*>(p)+offset);}
static unsigned stubTick=12345,originalCalls,logs,checks;
static unsigned tick(){return stubTick;}
static void originalClose(void* p){originalCalls++;at<B>(p,0x2050)=0;}
template<class T>T fn(unsigned address){
 if(address==0x39e240)return reinterpret_cast<T>(&tick);
 if(address==0x21dd24)return reinterpret_cast<T>(&originalClose);
 throw std::logic_error("Unexpected production callback");
}
static void log(const char*){logs++;}
static bool handledBack;
static unsigned lastBackTick;
static StationThemeToggleGesture themeSwitchGesture,settingsEffectsGesture;
static void* settingsBackOwner;
'''
program += request + "\n" + closed + "\n"
program += "static void productionOwnerReset(void* p){" + owner_prefix + "}}\n"
program += r'''
static void check(bool value){checks++;if(!value){std::fprintf(stderr,"Failed lifecycle check %u\n",checks);std::abort();}}
static const StationThemeRect effects={1280*.053f,720*.789f,1280*.229f,720*.070f};
static constexpr float x=1280*.15f,y=720*.82f;
static void down(unsigned long finger){
 check(settingsEffectsGesture.touch(0,finger,x,y,effects)==0);
 check(settingsEffectsGesture.pressed&&settingsEffectsGesture.finger==finger);
}
static void verifyFreshTap(unsigned long finger){
 down(finger);
 check(settingsEffectsGesture.touch(2,finger,x,y,effects)==1);
 check(!settingsEffectsGesture.pressed);
 check(settingsEffectsGesture.touch(0,finger+1,0,0,effects)==-1);
}
static void pressTheme(){
 check(themeSwitchGesture.touch(0,999,x,y,effects)==0);
 check(themeSwitchGesture.pressed);
}
int main(){
 alignas(8) B first[0x2300]={},second[0x2300]={};
 // Reproduce DOWN -> human Back -> close/reopen before UP. A new pointer ID
 // must be admitted; it must not be silently consumed by the previous gesture.
 for(unsigned long finger=10;finger<210;finger++){
  at<B>(first,0x2050)=1;at<B>(first,0x1ac)=0;handledBack=false;
  down(finger);pressTheme();
  requestSettingsClose(first);
  check(!settingsEffectsGesture.pressed&&!themeSwitchGesture.pressed);
  check(handledBack&&lastBackTick==stubTick&&at<B>(first,0x1ac)==1);
  unsigned before=originalCalls;settingsClosedHook(first);
  check(originalCalls==before+1&&at<B>(first,0x2050)==0);
  at<B>(first,0x2050)=1;verifyFreshTap(finger+1000);
 }
 // The original close callback can also arrive independently of requestClose.
 at<B>(first,0x2050)=1;down(321);pressTheme();
 unsigned before=originalCalls;settingsClosedHook(first);
 check(originalCalls==before+1);
 check(!settingsEffectsGesture.pressed&&!themeSwitchGesture.pressed);
 at<B>(first,0x2050)=1;verifyFreshTap(654);
 // An already-closed settings window must still retire any held gesture,
 // without requesting another native animation or changing Back bookkeeping.
 at<B>(first,0x2050)=0;at<B>(first,0x1ac)=0;handledBack=false;lastBackTick=0;
 down(700);pressTheme();requestSettingsClose(first);
 check(!settingsEffectsGesture.pressed&&!themeSwitchGesture.pressed);
 check(!handledBack&&lastBackTick==0&&at<B>(first,0x1ac)==0);
 verifyFreshTap(701);
 // Execute the actual new-owner reset prefix, retaining same-owner gestures.
 settingsBackOwner=first;down(800);productionOwnerReset(second);
 check(settingsBackOwner==second&&!settingsEffectsGesture.pressed);
 verifyFreshTap(801);
 down(802);productionOwnerReset(second);
 check(settingsEffectsGesture.pressed&&settingsEffectsGesture.finger==802);
 check(settingsEffectsGesture.touch(2,802,x,y,effects)==1);
 check(!settingsEffectsGesture.pressed&&logs>0);
 std::printf("PASS %u executed graphics-settings gesture lifecycle checks\n",checks);
}
'''
probe = OUT / "graphics_settings_lifecycle.cpp"
binary = OUT / "graphics_settings_lifecycle.exe"
probe.write_text(program, encoding="utf-8")
subprocess.run(
    [r"C:\Program Files\LLVM\bin\clang++.exe", "-std=c++17", "-O2", "-Wall", "-Wextra",
     str(probe), "-o", str(binary)], check=True, capture_output=True, text=True,
)
result = subprocess.run([str(binary)], check=True, capture_output=True, text=True).stdout.strip()
assert result.startswith("PASS ")
record = {
    "version": "R117",
    "passed": True,
    "utc": datetime.now(timezone.utc).isoformat(),
    "result": result,
    "productionFunctions": ["requestSettingsClose", "settingsClosedHook"],
    "productionFragment": "settingsBackOwner changed: gesture reset and owner assignment",
    "gesture": "StationThemeToggleGesture included from production header",
    "scenarios": ["200 close-before-UP/reopen/new-pointer trials", "original close alone",
                  "already-closed window", "owner change", "same owner retains current gesture"],
    "sourceSHA256": {
        "native/d0/native_settings.h": hashlib.sha256(SETTINGS.read_bytes()).hexdigest(),
        "native/d0/station_theme_switch_state.h": hashlib.sha256(GESTURE.read_bytes()).hexdigest(),
    },
    "scope": "host regression with only clock/GuiStore callbacks stubbed; no Android visual, thermal or gameplay proof",
    "physicalValidation": False,
}
(ROOT / "evidence/graphics-settings-lifecycle-r117.json").write_text(
    json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
)
print(result)
