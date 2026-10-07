"""Run the R67 suite and recovery tests against the exact R71 composition.

Includes the R71 roster fixture when present. Production code is obtained from
build_candidate.verified_sources(), never from a baseline-only source list.
Raw compiler/runtime logs and temporary files stay on E:. A sanitized receipt
is written to this snapshot's evidence/local-tests.json. No DEX/APK is built,
no device is accessed, and these checks do not validate Android appearance.
"""
from pathlib import Path
from collections import Counter
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
from build_candidate import (SNAPSHOT, R67, DEFAULT_WORK, CLIENT_DEX_SHA256,
                             require, sha, verified_sources, verified_navigation_sources)
from navigation_source_guards import expected_session, expected_presence
from patch_navigation_manifest import patch_manifest

REPOSITORY = SNAPSHOT.parent.parent
RECOVERY = SNAPSHOT.parent / 'station-online-recovery-r67-20261007'
JAVA = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin\java.exe')
ANDROID = Path(r'G:\Android\Sdk\platforms\android-34\android.jar')
JSON_JAR = Path(r'E:\ESTUDO APK\work\turbostations-reconstruction-20261002\tools\json-20250517.jar')
R67_TEST_IDENTITIES = {
    'recipes/run_local_tests.py': '8cd5f5ecfb42a42aed1599d1781754500612dc5ca84ae8d291fd1a2d68de9186',
    'evidence/local-tests-final.json': '10498a1bd77fa4b5b183506d0d2f5cf529dc61989981600fd5d3f7da6d72a2b7',
    'tests/MemoryCompile.java': '3d0a10bcc0f775c034b9215d0df329b8d9f754ca12222e928b21a04641135ccd',
    'evidence/java-memory-tests.json': '991694e9cc8d78579408877058db0d8bbfd4acefa40552a97548026b4fb7167e',
}
RECOVERY_IDENTITIES = {
    'JAVA-SOURCE-MANIFEST.json': '12a260c9900f9bcdfb964743e820747a9cd39b0ae71e609e1de6a2e8428024bb',
    'tests/StationRecoveryVectorsTest.java': 'c8ce6b8173cb5ea3a02843792ba35cb840745c2290b8256803e04e79c93bba84',
    'tests/StationRecoveryProofTest.java': '72635eeaa487016c7d6d09c4a377bbe8699c6705de89932aacb75c38f565e926',
    'tests/contract-vectors.json': 'b7efac34a5b04f78560c1749270a56fad640d8de5924c5f4e4abf62662dc0779',
}
NETPLAY_PATH = 'netplay-src/org/emulationstation/frontend/netplay/'
ACTIVITY = NETPLAY_PATH + 'StationRoomsActivity.java'
CORE_CLASSES = (
    'StationOnlineClient', 'StationOnlineGame', 'StationLaunchPolicy',
    'StationRoomCreation', 'StationRoomStartState', 'StationRoomState',
    'StationSessionChannel', 'StationRetroLaunch', 'StationRetroActivity',
    'StationGameSession', 'StationHostConnector', 'StationRelayTunnel',
    'StationRelayTls', 'StationPresence', 'StationInvitationCode',
    'StationRecoveryTunnel', 'StationRecoveryWire',
)
CRITICAL_METHODS = (
    'onCreate', 'onSaveInstanceState', 'onStart', 'onStop', 'onDestroy', 'cancelAll', 'launch',
    'launchFailure', 'exitRooms', 'command', 'joinConfirmed', 'createRoom',
    'action', 'joinCode',
)
EXTRA_TESTS = (
    ('StationTaskNavigationTest', None),
    ('StationGameSessionLifecycleTest', None),
    ('StationRoomRosterTest', None),
    ('StationRoomStartProtocolTest', None),
    ('StationRecoveryStateWireTest', None),
    ('StationRecoveryVectorsHostTest', 32),
)


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode('utf8')).hexdigest()


def java_tokens(source):
    # Strings/characters are consumed before comment markers and braces. These
    # Java 8 sources contain no text blocks; whitespace/comments are immaterial.
    pattern = r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\r\n]*|/\*[\s\S]*?\*/|[A-Za-z_$][\w$]*|\S'
    return [match.group(0) for match in re.finditer(pattern, source)
            if not match.group(0).startswith(('//', '/*'))]


def matching(tokens, start, opening, closing):
    require(tokens[start] == opening, 'Invalid Java token boundary')
    depth = 0
    for index in range(start, len(tokens)):
        if tokens[index] == opening:
            depth += 1
        elif tokens[index] == closing:
            depth -= 1
            if depth == 0:
                return index
    raise ValueError('Unbalanced Java delimiter during source inspection')


def methods(tokens, name):
    """Extract outer-class method tokens, including every overload and body."""
    depth = 0
    found = {}
    for index, token in enumerate(tokens):
        if token == '{':
            depth += 1
        elif token == '}':
            depth -= 1
        elif depth == 1 and token == name and tokens[index + 1:index + 2] == ['(']:
            end_parameters = matching(tokens, index + 1, '(', ')')
            body = end_parameters + 1
            while body < len(tokens) and tokens[body] not in ('{', ';', '='):
                body += 1
            if body < len(tokens) and tokens[body] == '{':
                end_body = matching(tokens, body, '{', '}')
                signature = ''.join(tokens[index:body])
                require(signature not in found, 'Ambiguous method signature: ' + name)
                found[signature] = tokens[index:end_body + 1]
    return found


def calls(tokens, prefix):
    found = []
    for index in range(len(tokens) - len(prefix)):
        opening = index + len(prefix)
        if tokens[index:opening] == prefix and tokens[opening] == '(':
            end = matching(tokens, opening, '(', ')')
            found.append(tuple(tokens[index:end + 1]))
    return found


def contains_tokens(tokens, snippet):
    expected = java_tokens(snippet)
    return any(tokens[i:i + len(expected)] == expected for i in range(len(tokens) - len(expected) + 1))


def replace_one_sequence(tokens, before, after):
    old, new = java_tokens(before), java_tokens(after)
    matches = [i for i in range(len(tokens) - len(old) + 1) if tokens[i:i + len(old)] == old]
    if len(matches) != 1:
        return None
    index = matches[0]
    return tokens[:index] + new + tokens[index + len(old):]


def recovery_sources(baseline):
    """The immutable incoming candidate is the preservation baseline for v2."""
    for path, expected in RECOVERY_IDENTITIES.items():
        require(sha(RECOVERY / path) == expected, 'Incoming recovery identity changed: ' + path)
    manifest = json.loads((RECOVERY / 'JAVA-SOURCE-MANIFEST.json').read_text('utf8'))
    require(manifest['baseline'] == {name: sha(path) for name, path in baseline.items()},
            'Recovery candidate was not based on the exact restored R67 sources')
    result = dict(baseline)
    overrides = {path.relative_to(RECOVERY).as_posix(): path
                 for path in (RECOVERY / 'netplay-src').rglob('*.java')}
    require(len(overrides) == 9, 'Expected seven modified and two new recovery Java sources')
    result.update(overrides)
    require(manifest['files'] == {name: sha(path) for name, path in result.items()},
            'Incoming 195-source recovery composition differs from its manifest')
    return result


def integration_guards(baseline, sources):
    """Static preservation/binding checks; deliberately no visual assertions."""
    guards = []
    for name in CORE_CLASSES:
        if name == 'StationRoomStartState':
            continue
        path = NETPLAY_PATH + name + '.java'
        before, after = sha(baseline[path]), sha(sources[path])
        expected = None
        if name == 'StationGameSession':expected = expected_session(baseline[path].read_text('utf8'))
        elif name == 'StationPresence':expected = expected_presence(baseline[path].read_text('utf8'))
        preserved = java_tokens(expected) == java_tokens(sources[path].read_text('utf8')) if expected is not None else before == after
        guards.append({'check': 'core-source:' + name, 'passed': preserved,
                       'baselineSHA256': before, 'actualSHA256': after,
                       'prescribedNavigationChange': expected is not None})
    start_path = NETPLAY_PATH + 'StationRoomStartState.java'
    original_start = java_tokens(baseline[start_path].read_text('utf8'))
    actual_start = java_tokens(sources[start_path].read_text('utf8'))
    original_reason = methods(original_start, 'reason')
    expected_reason = {signature: replace_one_sequence(body,
        'has(snapshot.optJSONArray("transports"),"relay-wss-v1")',
        'has(snapshot.optJSONArray("transports"),transport(snapshot))')
        for signature, body in original_reason.items()}
    expected_transport = ('transport(JSONObject snapshot){JSONObject room=snapshot==null?null:snapshot.optJSONObject("room");'
        'return room!=null&&"station-stream.v2".equals(room.optString("recoveryProtocol"))?"relay-wss-v2":"relay-wss-v1";}')
    guards.append({'check': 'start-authority-and-readiness-preserved-with-selected-transport',
                   'passed': len(expected_reason) == 1 and None not in expected_reason.values()
                             and expected_reason == methods(actual_start, 'reason')
                             and methods(original_start, 'has') == methods(actual_start, 'has')
                             and list(methods(actual_start, 'transport').values()) == [java_tokens(expected_transport)]})
    old = java_tokens(baseline[ACTIVITY].read_text('utf8'))
    current = java_tokens(sources[ACTIVITY].read_text('utf8'))
    for name in CRITICAL_METHODS:
        before, after = methods(old, name), methods(current, name)
        expected = before
        if name == 'onCreate':
            expected = {signature: replace_one_sequence(body,'super.onCreate(saved);','super.onCreate(saved);StationTaskNavigation.arrived(this);') for signature, body in before.items()}
        elif name == 'onStart':
            expected = {signature: replace_one_sequence(body,'active=true;connect();','active=true;if(returningFromGame)StationTaskNavigation.gameReturned(this);connect();') for signature, body in before.items()}
        guards.append({'check': 'critical-method:' + name,
                       'passed': bool(before) and expected == after,
                       'baselineOverloads': len(before), 'actualOverloads': len(after),
                       'baselineTokenSHA256': canonical_hash(before),
                       'actualTokenSHA256': canonical_hash(after)})
    # These two lifecycle changes are deliberate R71 presentation integration.
    # Match the complete incoming recovery method after one prescribed insertion,
    # retaining authority/generation gates, cancellation and heartbeat logic.
    for name, before_snippet, after_snippet in (
        ('deliver', 'if(active&&generation==epoch)paint(snapshot);',
         'if(active&&generation==epoch){roster.observe(snapshot);paint(snapshot);applyPendingNavigation(snapshot);}'),
        ('connect', 'state.reset();', 'state.reset();roster.reset();'),
    ):
        before, after = methods(old, name), methods(current, name)
        expected = {signature: replace_one_sequence(body, before_snippet, after_snippet)
                    for signature, body in before.items()}
        guards.append({'check': 'prescribed-roster-integration:' + name,
                       'passed': len(before) == len(after) == 1 and None not in expected.values() and expected == after,
                       'baselineTokenSHA256': canonical_hash(before),
                       'expectedTokenSHA256': canonical_hash(expected), 'actualTokenSHA256': canonical_hash(after)})
    old_calls = calls(old, ['client', '.', 'call'])
    current_calls = calls(current, ['client', '.', 'call'])
    start = 'StationOnlineClient.command("start")'
    old_start = [call for call in old_calls if contains_tokens(list(call), start)]
    new_start = [call for call in current_calls if contains_tokens(list(call), start)]
    old_other = [call for call in old_calls if call not in old_start]
    new_other = [call for call in current_calls if call not in new_start]
    guards.append({'check': 'all-other-activity-client-call-payloads',
                   'passed': bool(old_other) and Counter(old_other) == Counter(new_other),
                   'baselineCount': len(old_other), 'actualCount': len(new_other),
                   'baselineTokenSHA256': canonical_hash(sorted(old_other)),
                   'actualTokenSHA256': canonical_hash(sorted(new_other))})
    old_payload = 'client.call(StationOnlineClient.command("start").put("roomId",room().getString("roomId")).put("transport","station-stream.v2".equals(room().optString("recoveryProtocol"))?"relay-wss-v2":"relay-wss-v1"),false,cancel)'
    new_payload = 'client.call(StationOnlineClient.command("start").put("roomId",latest.getJSONObject("room").getString("roomId")).put("transport",StationRoomStartState.transport(latest)),false,cancel)'
    guards.append({'check': 'start-schema-transport-and-single-snapshot-room',
                   'passed': old_start == [tuple(java_tokens(old_payload))]
                             and new_start == [tuple(java_tokens(new_payload))],
                   'baselineTokenSHA256': canonical_hash(old_start),
                   'actualTokenSHA256': canonical_hash(new_start)})
    start_action = ('action(cancel->{JSONObject latest=state.get();'
                    'String changed=StationRoomStartState.reason(latest);'
                    'if(!changed.isEmpty())throw new StationOnlineGame.Unavailable(changed);'
                    'if(!confirmedRoom.equals(roomConfirmationKey(latest)))'
                    'throw new StationOnlineGame.Unavailable("A sala mudou. Confira os participantes antes de iniciar.");'
                    'return ' + new_payload + ';})')
    start_actions = [call for call in calls(current, ['action']) if contains_tokens(list(call), start)]
    guards.append({'check': 'start-rechecks-authority-readiness-and-confirmed-room-before-send',
                   'passed': start_actions == [tuple(java_tokens(start_action))],
                   'expectedTokenSHA256': canonical_hash(java_tokens(start_action)),
                   'actualTokenSHA256': canonical_hash(start_actions)})
    room_key = ('roomConfirmationKey(JSONObject snapshot){JSONObject room=snapshot==null?null:snapshot.optJSONObject("room");'
                'return room==null?"":snapshot.optString("instance")+"/"+room.optString("roomId")+"/"+room.optString("itemId");}')
    keys = methods(current, 'roomConfirmationKey')
    guards.append({'check': 'confirmation-bound-to-instance-room-and-game',
                   'passed': list(keys.values()) == [java_tokens(room_key)]})
    snippets = {
        'ready-command-preserved': 'command("ready","value",!contains(rd,self))',
        'signed-membership-roster-binding': 'roster.rows(snapshot)',
        'participant-name-binding': 'text(column,member.name,16,white)',
        'nickname-resolved-by-id': 'roster.resolveName(snapshot,id)',
        'snapshot-observation': 'roster.observe(snapshot)',
        'connection-resets-roster': 'roster.reset()',
        'confirmation-roster-binding': 'renderParticipants(confirmationPlayers,snapshot)',
        'confirmation-captures-room-binding': 'final String confirmedRoom=roomConfirmationKey(snapshot);',
        'confirmation-dismisses-after-room-or-game-change': 'if(!roomConfirmationKey(snapshot).equals(confirmationPlayers.getTag())){codeDialog.dismiss();',
        'confirmation-checks-selected-transport': 'contains(transports,StationRoomStartState.transport(snapshot))',
        'recovery-launch-policy-kept': 'StationLaunchPolicy.eligible(mine,self.equals(mine.optString("hostId")))',
        'recovery-return-reports-lost-native-state': 'StationOnlineClient.command("recovery-failed").put("roomId",lost.getString("roomId")).put("generation",lost.getLong("generation"))',
        'recovery-ticket-carries-metadata-and-generation': 'game.fields(ticketRequest).put("generation",room.getLong("generation"))',
        'recovery-binder-retains-room-metadata': 'StationGameSession.create(this,room)',
    }
    for name, snippet in snippets.items():
        passed = contains_tokens(current, snippet)
        if name == 'ready-command-preserved':
            passed = passed and contains_tokens(old, snippet)
        guards.append({'check': name, 'passed': passed})
    return guards


def legacy_suite():
    for path, expected in R67_TEST_IDENTITIES.items():
        require(sha(R67 / path) == expected, 'Original R67 test identity changed: ' + path)
    recipe = R67 / 'recipes/run_local_tests.py'
    spec = importlib.util.spec_from_file_location('r71_legacy_host_suite', recipe)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(recipe.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', default=DEFAULT_WORK,
                        help='R71 production workspace to bind, if already built; must be on E:')
    args = parser.parse_args()
    work = Path(args.workspace).resolve()
    require(work.drive.upper() == 'E:', 'Tests and private logs must stay on E:')
    require(not sys.flags.optimize, 'Run tests without -O')
    baseline, overlay, sources, manifest_path = verified_sources()
    recovery = recovery_sources(baseline)
    source_hashes = {name: sha(path) for name, path in sorted(sources.items())}
    manifest_hash = sha(manifest_path)
    legacy = legacy_suite()
    suite = list(legacy.SUITE)
    original = json.loads((R67 / 'evidence/java-memory-tests.json').read_text('utf8'))
    frozen_tests = json.loads((R67 / 'evidence/local-tests-final.json').read_text('utf8'))
    classes = [name for _, name, _ in suite]
    require(original['testClasses'] == classes, 'Frozen R67 test class order differs')
    expected_passes = legacy.pass_lines(original['stdout'])
    require(len(expected_passes) == len(suite) and sum(count or 0 for _, _, count in suite) == 449,
            'Original 449-check suite or relay diagnostics changed')
    test_sources = [path for path, _, _ in suite] + [legacy.R55 / 'StationApiTest.java']
    for path in test_sources:
        relative = path.relative_to(REPOSITORY).as_posix()
        require(sha(path) == frozen_tests['testSourceHashes'][relative], 'Frozen test source changed: ' + relative)
    require(NETPLAY_PATH + 'StationRoomRoster.java' in sources, 'Roster helper is absent from production')
    roster_included = True
    for name, _ in EXTRA_TESTS:
        test = SNAPSHOT / 'tests' / (name + '.java')
        require(test.is_file(), 'Required R71 fixture missing: ' + name)
        test_sources.append(test)
        classes.append('org.emulationstation.frontend.netplay.' + name)
    test_sources += [RECOVERY / 'tests/StationRecoveryVectorsTest.java',
                     RECOVERY / 'tests/StationRecoveryProofTest.java']
    vectors_fixture = RECOVERY / 'tests/contract-vectors.json'
    test_hashes = {path.relative_to(REPOSITORY).as_posix(): sha(path) for path in test_sources}
    dependencies = {'androidJar': sha(ANDROID), 'jsonJar': sha(JSON_JAR)}
    require(dependencies == {
        'androidJar': '6cea1df3efb77103ac3e2beb9bf4718964b0e0869ab16d39d29d5cbae1c147ad',
        'jsonJar': '3ea61b2a06e31edf1c91134fe9106b0ebb16628be169f3db75bc7a2b06b45796',
    }, 'External test dependency identity differs')
    build_path = work / 'evidence/build.json'
    build = json.loads(build_path.read_text('utf8')) if build_path.is_file() else None
    if build is not None:
        require(build.get('base') == 'R70' and build.get('compiled'), 'R71 production build receipt required')
        require(build['sourceHashes'] == source_hashes, 'Tests do not match the actual R71 production DEX sources')
        require(build['overlayManifestSHA256'] == manifest_hash, 'Tests do not match the production overlay manifest')
        require(build['baseClientDexSHA256'] == CLIENT_DEX_SHA256 and not build['clientDexUnchanged'], 'Navigation DEX28 ancestry differs')
        require(build['navigationGuards'] == verified_navigation_sources(baseline,overlay,sources), 'Production client change escaped navigation guard')
        for module in ('client', 'rooms'):
            require(sha(work / 'java/build' / (module + '-dex/classes.dex')) == build[module + 'DexSHA256'],
                    'Production DEX artifact differs: ' + module)
    guards = integration_guards(recovery, sources)
    verified_navigation_sources(baseline,overlay,sources)
    import zipfile
    from build_candidate import BASE_APK
    with zipfile.ZipFile(BASE_APK) as archive:
        manifest_bytes=archive.read('AndroidManifest.xml')
    patched,manifest_receipt=patch_manifest(manifest_bytes)
    expected_manifest=json.loads((SNAPSHOT/'manifest/frontend-task-policy.json').read_text('utf8'))
    guards.append({'check':'manifest-exact-one-typed-attribute','passed':manifest_receipt==expected_manifest})
    manifest_names={a['value'] for tag,attrs in __import__('patch_navigation_manifest').attributes(manifest_bytes) if tag=='activity' for a in attrs if a['resource']==0x01010003}
    policy=sources['client/src/java/org/emulationstation/frontend/auth/StationTaskPolicy.java'].read_text('utf8')
    local_games=re.findall(r'"([^"]+)"',policy.split('LOCAL_GAMES={',1)[1].split('};',1)[0])
    guards.append({'check':'local-game-resume-whitelist-exists-in-R70-manifest','passed':len(local_games)==14 and set(local_games)<=manifest_names})
    navigation=sources['client/src/java/org/emulationstation/frontend/auth/StationTaskNavigation.java'].read_text('utf8')
    guards.append({'check':'navigation-never-removes-tasks-or-kills-processes','passed':not any(token in navigation for token in ('finishAndRemoveTask','killProcess','FLAG_ACTIVITY_CLEAR_TASK','FLAG_ACTIVITY_CLEAR_TOP','System.exit'))})
    rooms=sources[ACTIVITY].read_text('utf8')
    guards.append({'check':'incoming-peer-keeps-draft-recipient-binding','passed':'openConversation(peer,roster.resolveName(snapshot,peer));' in rooms})
    guards.append({'check':'incoming-item-keeps-room-and-refreshes-card','passed':'StationTaskPolicy.canSelectItem(true,snapshot.optJSONObject("room")!=null,launching,returningFromGame)' in rooms and 'selectedItem=item;prepared=null;roomLayout(false);loadHero();' in rooms})
    helper = R67 / 'tests/MemoryCompile.java'
    all_sources = [sources[name] for name in sorted(sources)] + test_sources
    require(JAVA.is_file(), 'Required host JDK is missing')
    # Pre-build testing must not create the production destination, whose build
    # recipe intentionally requires a nonexistent directory.
    scratch_parent = work / 'tests' if work.is_dir() else work.with_name(work.name + '-tests')
    scratch_parent.mkdir(exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix='java-memory-', dir=scratch_parent))
    require(scratch.resolve().is_relative_to(scratch_parent.resolve()), 'Scratch directory escaped the E: test workspace')
    temp = scratch / 'temp'
    temp.mkdir()
    env = dict(os.environ, TEMP=str(temp), TMP=str(temp))
    classpath = os.pathsep.join(map(str, (JSON_JAR, ANDROID)))
    command = [str(JAVA), '-Djava.io.tmpdir=' + str(temp),
               '-Dstation.recovery.vectors=' + str(vectors_fixture), str(helper), classpath, *classes]
    started = datetime.datetime.now(datetime.timezone.utc)
    try:
        process = subprocess.run(command, input='\n'.join(map(str, all_sources)) + '\n',
                                 capture_output=True, text=True, encoding='utf8', errors='replace',
                                 env=env, cwd=scratch, timeout=240)
        stdout, stderr, code = process.stdout, process.stderr, process.returncode
    except subprocess.TimeoutExpired as error:
        def decode(value):
            return value.decode('utf8', 'replace') if isinstance(value, bytes) else value or ''
        stdout, stderr, code = decode(error.stdout), decode(error.stderr), -1
    (scratch / 'stdout.log').write_text(stdout, 'utf8')
    (scratch / 'stderr.log').write_text(stderr, 'utf8')
    actual_passes = legacy.pass_lines(stdout)
    compiled = re.search(r'^success=true sources=(\d+) classes=(\d+) memoryBytes=(\d+)$', stdout, re.M)
    roster_match = re.search(r'^StationRoomRosterTest: (\d+) checks passed$', stdout, re.M)
    roster_checks = int(roster_match.group(1)) if roster_match else None
    roster_passed = bool(roster_match and roster_checks > 0) if roster_included else None
    extras = []
    for name, expected in EXTRA_TESTS:
        match = re.search(r'^' + name + r': (\d+) checks passed$', stdout, re.M)
        count = int(match.group(1)) if match else None
        extras.append({'class': 'org.emulationstation.frontend.netplay.' + name,
                       'checks': count, 'passed': count is not None and count > 0
                       and (expected is None or count == expected)})
    vector_result = None
    if len(actual_passes) == len(expected_passes) + 1:
        try:
            vector_result = json.loads(actual_passes[-1])
        except ValueError:
            pass
    vectors_passed = (isinstance(vector_result, dict) and vector_result.get('passed') is True
                      and vector_result.get('checks') == 32)
    no_classes = not any(scratch.rglob('*.class'))
    source_stable = ({name: sha(path) for name, path in sorted(sources.items())} == source_hashes
                     and sha(manifest_path) == manifest_hash
                     and {path.relative_to(REPOSITORY).as_posix(): sha(path) for path in test_sources} == test_hashes
                     and all(sha(RECOVERY / path) == expected for path, expected in RECOVERY_IDENTITIES.items()))
    baseline_passed = actual_passes[:len(expected_passes)] == expected_passes
    success = (code == 0 and compiled is not None and int(compiled.group(1)) == len(all_sources)
               and baseline_passed and all(item['passed'] for item in extras) and vectors_passed
               and all(guard['passed'] for guard in guards) and no_classes and source_stable)
    binding = {
        'verifiedComposition': True,
        'mode': 'production-dex' if build is not None else 'pre-build-composition',
        'sameSourcesAsProductionDex': build is not None,
        'overlayManifestSHA256': manifest_hash,
        'productionSourceMapSHA256': canonical_hash(source_hashes),
        'sourceMapHashEncoding': 'UTF-8 JSON sorted keys, separators comma/colon, no final newline',
        'sourceHashes': source_hashes,
        'sourceInputsUnchangedDuringTests': source_stable,
    }
    if build is not None:
        binding.update(javaDexBuildReceiptSHA256=sha(build_path),
                       clientDexSHA256=build['clientDexSHA256'], roomsDexSHA256=build['roomsDexSHA256'])
    # Only fixed suite PASS lines, numeric compiler totals and the numeric roster
    # result enter Git. Raw errors/diagnostics remain in the private E: logs.
    safe_stdout = ([compiled.group(0)] if compiled else [])
    safe_stdout += [line for line in actual_passes if line in expected_passes]
    if roster_match:
        safe_stdout.append(roster_match.group(0))
    for item in extras[1:]:
        if item['passed']:
            safe_stdout.append(item['class'].rsplit('.', 1)[-1] + ': ' + str(item['checks']) + ' checks passed')
    receipt = {
        'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'startedAt': started.isoformat(),
        'success': success,
        'scope': 'Host JVM: synthetic authority, roster, v1/v2 start policy, recovery wire/rings, public RSA vectors and legacy loopback TCP; no production requests or Android execution',
        'productionSourceCount': len(sources), 'testSourceCount': len(test_sources), 'sourceCount': len(all_sources),
        'testClassCount': len(classes), 'testClasses': classes,
        'baselineCountedChecks': 449 if baseline_passed else None,
        'relayDiagnosticsPassed': expected_passes[7] in actual_passes,
        'rosterTestIncluded': roster_included, 'rosterChecks': roster_checks, 'rosterPassed': roster_passed,
        'countedChecks': 449 + sum(item['checks'] or 0 for item in extras) if success else None,
        'additionalTestResults': extras, 'recoveryPublicVectorsPassed': vectors_passed,
        'recoveryFixtureSHA256': sha(vectors_fixture), 'recoveryTestIdentities': RECOVERY_IDENTITIES,
        'recoverySourceCommit': '4d30401a80658dd56666ef10f48d9556b3fdd9e9',
        'recoveryTransportInteropExecuted': False,
        'testResults': [{'class': class_name, 'expectedChecks': count,
                         'passed': expected_passes[index] in actual_passes,
                         'output': expected_passes[index] if expected_passes[index] in actual_passes else None}
                        for index, (_, class_name, count) in enumerate(suite)],
        'integrationGuards': guards, 'integrationGuardCount': len(guards),
        'compilation': {'release': 17, 'classesInMemory': int(compiled.group(2)) if compiled else None,
                        'memoryBytes': int(compiled.group(3)) if compiled else None},
        'sourceBinding': binding, 'testSourceHashes': test_hashes, 'r67TestIdentities': R67_TEST_IDENTITIES,
        'recipeSHA256': sha(__file__), 'compositionRecipeSHA256': sha(Path(__file__).with_name('build_candidate.py')),
        'memoryCompilerSHA256': sha(helper), 'inputs': dependencies,
        'javaRuntime': 'Eclipse Adoptium JDK 17.0.20.101-hotspot', 'javaExecutableSHA256': sha(JAVA),
        'stdout': '\n'.join(safe_stdout), 'rawDiagnosticsKeptOnlyInPrivateWorkspace': True,
        'returnCode': code, 'diskClassFiles': not no_classes,
        'dexBuilt': False, 'apkBuilt': False, 'installed': False, 'androidExecuted': False,
        'visualAppearanceVerified': False, 'productionModified': False,
    }
    destination = SNAPSHOT / 'evidence/local-tests.json'
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n', 'utf8')
    failures = [guard['check'] for guard in guards if not guard['passed']]
    require(success, 'Host suite/integration guards failed; see evidence/local-tests.json; guards: ' + ', '.join(failures))
    print('PASS: 449 existing checks plus relay diagnostics; added checks: ' + str(sum(item['checks'] for item in extras))
          + '; source guards: ' + str(len(guards)) + '; binding: ' + binding['mode'])
    print('Receipt: ' + destination.relative_to(REPOSITORY).as_posix())


if __name__ == '__main__':
    main()
