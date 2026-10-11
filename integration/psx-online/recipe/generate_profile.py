"""Generate the PSX variant's explicit policy from its actual compiled core.

The existing normal core stays byte-identical. This policy affects only an
explicit, authenticated online launch. It is not a server activation receipt.
"""
from pathlib import Path
import argparse, hashlib, json
from extract_core_defaults import extract, CORE_SHA256

ROOT = Path(__file__).resolve().parents[1]
OWNER_SHA256 = "62ad07ba8e62e3227d488f9075eb15167c2e95b721c43e480e2535b4319467f6"
OVERRIDES = {
    "pcsx_rearmed_bios": "HLE",
    "pcsx_rearmed_drc_thread": "disabled",
    "pcsx_rearmed_gpu_thread_rendering": "disabled",
    "pcsx_rearmed_spu_thread": "disabled",
    "pcsx_rearmed_frameskip_type": "disabled",
    "pcsx_rearmed_multitap": "disabled",
    "pcsx_rearmed_analog_combo": "disabled",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("core", type=Path)
    args = parser.parse_args()
    table = extract(args.core.read_bytes())
    for key, value in OVERRIDES.items():
        if value not in table["options"][key]["values"]:
            raise ValueError("PSX_OVERRIDE_VALUE:" + key)
    overrides = "".join(k+"="+v+"\n" for k,v in sorted(OVERRIDES.items()))
    policy = (
        "backend=psx-player-station-v1\nwire=PXL1\n"
        "ownerSha256=" + OWNER_SHA256 + "\n"
        "coreSha256=" + CORE_SHA256 + "\n"
        "compiledDefaultsSha256=" + table["compiledDefaultsSha256"] + "\n"
        "optionsPolicy=compiled-defaults+explicit-overrides-v1\n"
        "inputPolicy=standard-two-ports-v1\n"
        "synchronization=host-authoritative-lockstep-v1\n"
        "inputDelayFrames=4\n"
        "statePolicy=owner-thread-snapshot-v1\n"
        "saves=session-only-fresh\n"
        "humanExitOnly=true\n" + overrides
    )
    result = {
        "schemaVersion":1, "backend":"psx-player-station-v1",
        "coreLibrary":"libpcsx_rearmed_libretro_android.so",
        "coreSha256":CORE_SHA256, "ownerLibrary":"libmain.so",
        "ownerSha256":OWNER_SHA256,
        "compiledDefaultsSha256":table["compiledDefaultsSha256"],
        "compiledDefaults":{k:v["default"] for k,v in table["options"].items()},
        "overrides":OVERRIDES, "options":policy,
        "optionsSha256":hashlib.sha256(policy.encode()).hexdigest(),
        "controllerProfile":"standard-2p-v1", "devices":[1,1],
        "inputDelayFrames":4,
        "maximumPlayers":2, "allowedPlayerCounts":[2],
        "launchReady":False, "productionActivated":False,
        "physicalGameplayValidated":False,
        "limits":[
            "HLE BIOS is explicit; only games individually approved for this policy may start.",
            "No multitap, analog-pad or light-gun profile is enabled by this policy.",
            "A transport receipt is separate from a real emulated frame commit.",
            "This file alone does not enable a route, register an engine, or validate gameplay."
        ]
    }
    out=ROOT/"profile.json"
    out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    header=ROOT/"native"/"PsxPinnedOptions.h"
    header.parent.mkdir(parents=True,exist_ok=True)
    rows=["/* Generated from the exact normal core's compiled option table. */",
          "#pragma once", "#include <cstddef>", "#include <cstring>",
          "namespace station_psx {", "struct PinnedOption { const char* key; const char* value; };",
          "inline constexpr PinnedOption compiled_defaults[] = {"]
    q=lambda value: json.dumps(value,ensure_ascii=True)
    rows.extend("    {"+q(k)+", "+q(v["default"])+"}," for k,v in sorted(table["options"].items()))
    rows += ["};", "inline constexpr PinnedOption option_overrides[] = {"]
    rows.extend("    {"+q(k)+", "+q(v)+"}," for k,v in sorted(OVERRIDES.items()))
    rows += ["};", "inline constexpr const char* compiled_defaults_sha256 = "+q(table["compiledDefaultsSha256"])+";",
             "inline constexpr const char* canonical_options = "+q(policy)+";",
             "inline constexpr const char* options_sha256 = "+q(result["optionsSha256"])+";",
             "template<std::size_t N> inline const char* lookup(const PinnedOption (&rows)[N], const char* key) {",
             "    if (!key) return nullptr;", "    for (const auto& row : rows) if (std::strcmp(row.key, key)==0) return row.value;",
             "    return nullptr;", "}", "inline const char* pinned_option(const char* key) {",
             "    const char* value=lookup(option_overrides,key);", "    return value ? value : lookup(compiled_defaults,key);",
             "}", "} // namespace station_psx", ""]
    header.write_text("\n".join(rows),encoding="utf-8")
    java=ROOT/"java"/"org"/"emulationstation"/"frontend"/"netplay"/"StationPsxPolicy.java"
    java.parent.mkdir(parents=True,exist_ok=True)
    java.write_text("package org.emulationstation.frontend.netplay;\n"
        "/* Generated with the same exact compiled options as the native owner. */\n"
        "final class StationPsxPolicy {\n"
        "    static final String OPTIONS="+q(policy)+";\n"
        "    static final String OPTIONS_SHA="+q(result["optionsSha256"])+";\n"
        "    private StationPsxPolicy(){}\n}\n",encoding="utf-8")
    print(json.dumps({"compiledOptions":table["optionCount"],"optionsSha256":result["optionsSha256"],"routeEnabled":False}))

if __name__ == "__main__":
    main()
