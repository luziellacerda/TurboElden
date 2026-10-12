"""Exercise the actual v3 profile generator with isolated HLE/LLE fixtures.

The fixture game IDs are synthetic and are never registration inputs.
This does not publish profiles or verify gameplay/binaries.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
GENERATOR_SHA = "4c50ac36bb18532c3d128abbee14e7a59fa2d42d62a296319bdb23c9e5d2ae6b"


def need(value, message):
    if not value:
        raise ValueError(message)


def canonical(controller, devices, options):
    return json.dumps(dict(schemaVersion=1, controllerProfile=controller,
                           devices=devices, coreOptions=options),
                      ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def configured(engine):
    value = copy.deepcopy(engine)
    value["maximumPlayers"] = 5
    value["requireExplicitEngineModes"] = True
    value["controllerProfiles"] = []
    for controller, maximum, devices in (("standard-2p-v1", 2, [1, 1]),
                                         ("snes-multitap-port2-v1", 5, [1, 257, 1, 1, 1])):
        value["controllerProfiles"].append(dict(controllerProfile=controller,
            maximumPlayers=maximum, configuration=json.loads(canonical(controller, devices, value["options"]))))
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generator", type=Path, required=True)
    args = parser.parse_args()
    need(hashlib.sha256(args.generator.read_bytes()).hexdigest() == GENERATOR_SHA,
         "Actual audited v3 server profile generator required")
    spec = importlib.util.spec_from_file_location("station_r138_profiles_under_test", args.generator)
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    before = configured(next(e for e in json.loads((ROOT / "evidence/engines-r137-baseline.json").read_bytes())["engines"] if e["platform"] == "snes"))
    after = configured(next(e for e in json.loads((ROOT / "assets/station-online/engines.json").read_bytes())["engines"] if e["platform"] == "snes"))
    manifest = dict(schemaVersion=1, engines=[before, after])
    generator.validate_manifest(manifest)
    identities = (before["engineId"], after["engineId"])
    items, old_modes, new_modes = [], [], []
    for ordinal, (suffix, controller, maximum, counts) in enumerate((
        ("dsp1", "standard-2p-v1", 2, [2]),
        ("dsp4", "snes-multitap-port2-v1", 4, [2, 3, 4])), 1):
        item = dict(itemId="fixture-" + suffix, contentSha256=str(ordinal) * 64,
                    platform="snes", catalogVisible=True, artifact=dict(launchPath="fixture.sfc"),
                    metadata=dict(players="2"))
        items.append(item)
        mode = dict(itemId=item["itemId"], contentSha256=item["contentSha256"], platform="snes",
                    profileId="fixture-" + suffix + "-lle", controllerProfile=controller,
                    mode="fixture-local", modeTitle="Isolated fixture", maximumPlayers=maximum,
                    allowedPlayerCounts=counts, approved=True, instructions=["Isolated fixture only."],
                    sources=[], engineIds=[identities[0]])
        old_modes.append(mode)
        new_modes.append({**mode, "profileId": "fixture-" + suffix + "-hle-r138", "engineIds": [identities[1]]})
    old_profiles = generator.prepare(items, [], dict(schemaVersion=1, engines=[before]),
                                     dict(schemaVersion=1, modes=old_modes))
    need(len(old_profiles) == 2, "Fixture LLE profiles missing")
    output = generator.prepare(items, old_profiles, manifest,
                               dict(schemaVersion=1, modes=old_modes + new_modes))
    need(output[:len(old_profiles)] == old_profiles and len(output) == 4,
         "Existing profiles not preserved or HLE bindings missing")
    added = output[len(old_profiles):]
    configs = []
    for profile in added:
        mode = next(m for m in new_modes if m["itemId"] == profile["itemId"])
        devices = [1, 1] if mode["maximumPlayers"] == 2 else [1, 257, 1, 1, 1]
        configuration = canonical(mode["controllerProfile"], devices, after["options"])
        need(profile["profileSha256"] == hashlib.sha256(configuration).hexdigest(),
             "Server canonical HLE profile differs from Java canonical contract")
        original = next(p for p in old_profiles if p["itemId"] == profile["itemId"])
        need(profile["profileSha256"] != original["profileSha256"] and
             profile["engineId"] != original["engineId"], "LLE/HLE identities mixed")
        need(profile["allowedPlayerCounts"] == original["allowedPlayerCounts"] and
             profile["controllerProfile"] == original["controllerProfile"] and
             profile["mode"] == original["mode"], "Game mode/control/count changed")
        configs.append(dict(controllerProfile=mode["controllerProfile"],
                            profileSha256=profile["profileSha256"]))
    without_modes = generator.prepare(items, [], dict(schemaVersion=1, engines=[after]),
                                      dict(schemaVersion=1, modes=old_modes))
    need(without_modes == [], "HLE must not receive unscoped automatic approval")
    duplicate = [*old_modes, {**old_modes[0], "engineIds": [identities[1]]}]
    try:
        generator.validate_modes(dict(schemaVersion=1, modes=duplicate))
    except ValueError:
        pass
    else:
        raise ValueError("Duplicate profile ID should require a new scoped mode identity")
    print(json.dumps(dict(checksPassed=6, generatorSha256=GENERATOR_SHA,
                         oldProfilesPreserved=2, fixtureHleProfilesAdded=2,
                         configurations=configs, fixtureOnly=True, serverPublished=False,
                         androidGameplayValidated=False), indent=2))


if __name__ == "__main__":
    main()
