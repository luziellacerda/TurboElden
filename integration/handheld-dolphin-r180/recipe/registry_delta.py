"""Exact descriptor delta. Existing native cores are never rebuilt here."""
import copy
import hashlib
import json
import re

CORE = 'lib/arm64-v8a/libgpsp_station_online.so'
OVERLAY = 'assets/station-online/overlays/station-local/gba.cfg'
OPTIONS = 'gpsp_serial = "auto"\ngpsp_rtc_time_source = "deterministic"\n'
CONTROLLER = 'gba-gpsp-netpacket-v1'
UPSTREAM = '5819380c2ffb0900219d700a382ee68c464ebb99'

def need(value, message):
    if not value:
        raise ValueError(message)

def validate_core_options(header, options):
    for line in options.splitlines():
        match = re.fullmatch(r'([a-z0-9_]+) = "([^"\\]+)"', line)
        need(match is not None, 'Canonical gpSP option')
        key, value = match.groups()
        block = re.search(r'(?ms)^   \{\n      "' + re.escape(key) + r'",(.*?)(?=^   \{|^\};)', header)
        need(block is not None, 'gpSP option absent from pinned upstream: ' + key)
        allowed = re.findall(r'\{\s*"([^"\\]+)"\s*,', block.group(1))
        need(value in allowed, 'Invalid value for pinned gpSP option: ' + key)

def core_input(task, source):
    proof = json.loads((task / 'gpsp/build-receipt.json').read_text())
    binary = task / 'gpsp/lib/arm64-v8a/libgpsp_station_online.so'
    need(proof['passed'] and proof['commit'] == UPSTREAM
         and hashlib.sha256(binary.read_bytes()).hexdigest() == proof['sha256']
         and hashlib.sha256((source / 'build_gpsp.py').read_bytes()).hexdigest() == proof['scriptSha256'],
         'Reviewed pinned gpSP binary and recipe')
    java = source.parent / 'java/org/emulationstation/frontend/netplay/StationGbaLinkPolicy.java'
    need('OPTIONS = ' + json.dumps(OPTIONS) + ';' in java.read_text(), 'Exact Java and manifest GBA options')
    validate_core_options((task / "inputs/gpsp-core-options.h").read_text(), OPTIONS)
    return binary, proof

def restore_dolphin_identity(identity):
    need(identity.get('gamecubePadBufferOverride') ==
         {'layer':4, 'section':'NetPlay', 'key':'BufferSize', 'value':8}, 'Exact eight-frame donor identity')
    gc = identity['platformOptions']['gamecube']
    need(gc.count('padBuffer=8\n') == 1 and identity['platformOptions']['wii'].count('padBuffer=5\n') == 1,
         'Pinned GC8 and Wii5 policy')
    identity['platformOptions']['gamecube'] = gc.replace('padBuffer=8\n', 'padBuffer=5\n')
    del identity['gamecubePadBufferOverride']

def append_gba(registry, core_sha256, runtime_sha256):
    need(len(registry['engines']) == 13 and all(e['platform'] != 'gba' for e in registry['engines']),
         'Thirteen exact donor engines without an existing GBA online owner')
    row = dict(engineId='gpsp-5819380c-gba-netpacket-v1-' + core_sha256[:12], platform='gba',
               backend='retroarch', library='libgpsp_station_online.so',
               extensions=['gba'], overlay='station-local/gba.cfg', options=OPTIONS,
               launchReady=True, license='GPL-2.0', sourceDirectory='gpsp-' + UPSTREAM,
               recoveryProtocol='station-stream.v3', maximumPlayers=5,
               status='implemented-candidate-peer-gameplay-pending',
               contentIdentityByExtension={'default':'launch-file-v1'},
               coreSha256=core_sha256, runtimeSha256=runtime_sha256,
               runtimeLibrary='libstation_retroarch.so',
               controllerProfiles=[CONTROLLER], requireExplicitEngineModes=True)
    registry['engines'].append(row)
    policies = registry.get('platformPolicies', [])
    need(all(p['platform'] != 'gba' for p in policies), 'No duplicate local GBA policy')
    policies.append(dict(platform='gba', maximumPlayers=5, automaticRoomIntegrationReady=True, reason=''))
    registry['platformPolicies'] = policies
    return row

def assert_preserved(before, after):
    need(len(after['engines']) == len(before['engines']) + 1, 'One new core only')
    for old, new in zip(before['engines'], after['engines']):
        expected = copy.deepcopy(old)
        if old['platform'] in ['psx', 'n64', 'gamecube', 'wii']:
            expected['engineId'] = new['engineId']
            expected['runtimeSha256'] = new['runtimeSha256']
        if old['platform'] == 'gamecube':
            need(expected['options'].count('padBuffer=8\n') == 1, 'Exact GameCube donor options')
            expected['options'] = expected['options'].replace('padBuffer=8\n', 'padBuffer=5\n')
        need(expected == new, 'Unrequested engine change: ' + old['platform'])
