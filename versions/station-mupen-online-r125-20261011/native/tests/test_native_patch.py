"""Pinned source generation checks. These are not emulator/gameplay tests."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("native_patch", ROOT / "apply_native_patch.py")
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path, required=True)
    args = parser.parse_args()
    source = args.upstream.resolve()
    original = {name: (source / name).read_bytes() for name in patch.PINS}
    outputs = patch.generate(source)
    checks = 0
    def check(condition: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not condition: raise AssertionError(label)
    check(outputs == patch.generate(source), "generation must be deterministic")
    for name, raw in original.items():
        check((source / name).read_bytes() == raw, "offline tree unchanged: " + name)
        check(hashlib.sha256(raw).hexdigest() == patch.PINS[name], "upstream pin: " + name)
    main_c = outputs[next(iter(patch.PINS))].decode()
    net_c = outputs[list(patch.PINS)[1]].decode()
    exports = outputs[list(patch.PINS)[4]].decode()
    makefile = outputs[list(patch.PINS)[3]].decode()
    check("\n    $(SRCDIR)/main/netplay.c" in makefile, "original netplay source remains in build list")
    check("\n+" not in makefile, "no diff prefix in emitted makefile")
    check('void main_advance_one(void)\n{\n    if (station_mupen_enabled()) return;' in main_c, "Station cannot unilaterally advance a frame")
    check('m64p_error main_reset(int do_hard_reset)\n{\n    if (station_mupen_enabled()) return M64ERR_INVALID_STATE;' in main_c, "Station cannot unilaterally reset its state")
    check('if (station_mupen_enabled() && !station_mupen_cancelled()) return;' in main_c, "STOP requires explicit Quit authorization")
    check(main_c.index("station_mupen_gate(netplay_station_pump)") < main_c.index("netplay_check_sync(&g_dev.r4300.cp0)"), "VI gate before sync tick")
    check("if (station_mupen_gate(netplay_station_pump)) run_device(&g_dev);" in main_c, "initial emulator-thread gate")
    check("station_mupen_emulator_end();" in main_c, "end acknowledged before return")
    check("if (station_mupen_executing())" in net_c, "no closing sockets under EXECUTE")
    check('station_mupen_registration(player, &plugin, &rawdata)' in net_c, "register offer pinned before input plugin startup")
    registration = net_c[net_c.index('uint8_t netplay_register_player('):net_c.index('int netplay_lag()')]
    check(registration.index('station_mupen_registration') < registration.index('output_data[2] = plugin'), "pinned offer reaches actual registration bytes")
    check('if (station_mupen_executing())\n    {\n        return M64ERR_INVALID_STATE;' in net_c, "closing an active pipe cannot grant implicit Quit")
    check("if (!station_mupen_enabled()) main_core_state_set(M64CORE_EMU_STATE, M64EMU_STOPPED);" in net_c, "only original mode has timeout STOP")
    check("no busy-spin, worker thread, 10s timeout or STOP" in net_c, "cooperative input wait")
    check("MSG_DONTWAIT | MSG_NOSIGNAL" in net_c, "cancellable TCP sends")
    check("if (n <= 0) { station_mupen_fail(); return 0; }" in net_c, "EOF/error cannot become infinite read")
    check("station_mupen_set_roster(station_mask, station_slot, station_slot >= 0)" in net_c, "connected derived from registration")
    check("(current_status & 0x1)) station_mupen_fail();" in net_c, "real desync is sticky failure")
    check("l_cin_compats = NULL; /* stack-owned" in net_c, "stack-owned input pointer detached")
    for symbol in ("StationMupenConfigure", "StationMupenControl", "StationMupenStatus", "StationMupenStalled", "StationMupenRequestQuit"):
        check(symbol + ";" in exports, "JNA export: " + symbol)
    with tempfile.TemporaryDirectory(dir=ROOT / ".validation") as temporary:
        bad = Path(temporary)
        for name, raw in original.items():
            path = bad / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
        target = bad / next(iter(patch.PINS)); target.write_bytes(target.read_bytes() + b"\n")
        rejected = False
        try: patch.generate(bad)
        except ValueError: rejected = True
        check(rejected, "different upstream must fail before writing")
    print(json.dumps({"checks": checks, "deterministic": True, "offlineUnchanged": True, "gameplay": False}))

if __name__ == "__main__": main()
