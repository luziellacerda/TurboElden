"""Bound the SNES metadata proposal and verify pinned core source support.

This checks source/configuration, never downloads content or accesses a device.
The pending proposal is rejected by the opt-in final identity gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASELINE_SHA = "c0d75345922986c529137828e83b852612bb160870043654bd1b8d9821658ce7"
PENDING_ID = "bsnes-mercury-performance-79d7f9de-mt1-mp5-hle-pending-r138"


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(value).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, default=ROOT / "assets/station-online/engines.json")
    parser.add_argument("--require-final-id", action="store_true")
    args = parser.parse_args()
    baseline_raw = (ROOT / "evidence/engines-r137-baseline.json").read_bytes()
    need(digest(baseline_raw) == BASELINE_SHA, "R137 asset baseline changed")
    baseline = json.loads(baseline_raw)
    candidate = json.loads(args.candidate.read_bytes())
    checks = ["exact-r137-asset-baseline"]
    need(list(baseline) == list(candidate), "Top-level engine fields changed")
    need(len(baseline["engines"]) == len(candidate["engines"]), "Engine count changed")
    old_snes = [e for e in baseline["engines"] if e["platform"] == "snes"]
    new_snes = [e for e in candidate["engines"] if e["platform"] == "snes"]
    need(len(old_snes) == len(new_snes) == 1, "Exact single SNES engine required")
    before, after = old_snes[0], new_snes[0]
    need(list(before) == list(after), "SNES fields changed")
    need({key for key in before if before[key] != after[key]} == {"options", "engineId"},
         "Only SNES options and identity may change in metadata proposal")
    expected = before["options"]
    for old, new in (("bsnes_violate_accuracy = \"disabled\"", "bsnes_violate_accuracy = \"enabled\""),
                     ("bsnes_chip_hle = \"LLE\"", "bsnes_chip_hle = \"HLE\"")):
        need(expected.count(old) == 1, "Expected option absent or duplicated")
        expected = expected.replace(old, new)
    need(after["options"] == expected, "Other SNES options changed")
    need(after["engineId"] != before["engineId"], "LLE identity cannot identify HLE")
    if args.require_final_id:
        need("pending" not in after["engineId"].lower(), "Pending SNES identity cannot be promoted")
    else:
        need(after["engineId"] == PENDING_ID, "Unexpected proposal identity")
    projected = json.loads(json.dumps(candidate))
    for index, engine in enumerate(projected["engines"]):
        if engine["platform"] == "snes":
            projected["engines"][index] = before
    need(projected == baseline, "Other engines or top-level settings changed")
    checks += ["only-required-two-options-and-identity", "other-engines-settings-exact",
               "hle-gate-and-superfx100-preserved"]

    pins = json.loads((ROOT / "evidence/source-support-pins.json").read_bytes())
    texts = {}
    for logical, expected_hash in pins["sourceSha256"].items():
        raw = (args.source / logical).read_bytes()
        need(digest(raw) == expected_hash, "Pinned core source changed: " + logical)
        texts[logical] = raw.decode("utf-8")
    wrapper = texts["target-libretro/libretro.cpp"]
    need(re.search(r'static const char \* read_opt[^;]*\{\s*if\s*\(!strcmp\(get_var\("bsnes_violate_accuracy", "disabled"\), "enabled"\)\)\s*return get_var\(name, defval\);\s*else return defval;', wrapper),
         "HLE accuracy gate differs from audited source")
    need('read_opt("bsnes_chip_hle", "LLE"), "HLE"' in wrapper and
         "return SuperFamicom::Alt::DSP::HLE;" in wrapper,
         "Core does not select DSP HLE")
    markup = texts["sfc/cartridge/markup.cpp"]
    need("altImplementation(Alt::ForDSP)==Alt::DSP::HLE" in markup and
         "parse_markup_necdsp_hle(root);" in markup,
         "Cartridge parser does not select HLE")
    for chip in range(1, 5):
        need(f'"dsp{chip}.program.rom"' in markup and
             f"has_dsp{chip} = true;" in markup and
             f"&DSP{chip}::read" in markup and f"&DSP{chip}::write" in markup,
             f"Missing HLE implementation binding for DSP{chip}")
    heuristics = texts["ananke/heuristics/super-famicom.hpp"]
    need("name=dsp1b.program.rom size=0x1800" in heuristics and
         "name=dsp4.program.rom size=0x1800" in heuristics,
         "DSP dependency map changed")
    checks += ["pinned-existing-core-source", "hle-selection-requires-accuracy-gate",
               "dsp1-to-dsp4-hle-parser-bindings", "mario-kart-topgear-firmware-map"]
    print(json.dumps({"checksPassed": len(checks), "checks": checks,
                      "proposalAssetSha256": digest(args.candidate.read_bytes()),
                      "finalIdentityValidated": args.require_final_id,
                      "sourceSupportOnly": True, "androidGameplayValidated": False}, indent=2))


if __name__ == "__main__":
    main()
