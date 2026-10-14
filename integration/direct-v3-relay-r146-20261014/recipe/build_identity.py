"""Renew only route DEX35 bindings; original engines and policies stay exact."""
from pathlib import Path
import argparse,copy,importlib.util,json,os,re,subprocess,sys,zipfile
sys.dont_write_bytecode=True
from common import *
DEPENDENCIES = {
    "integration/online-lifecycle-review-r135/recipe/build_runtime_identity.py": "f1a1d8e3bd161bb6751801efc5a314e61b403f670822085dc92127dc63fe98da",
    "integration/psx-online/recipe/build_entry.py": "08f5409cb5c9eb7cbc4c8ab370d0a1d7184156a6668bb63b29eb212cfd92f058",
    "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py": "de118216baf9e6b6bf133a95e4ab30c6b4d83f779c070304b641b6c1cac6c66d",
}


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    previous_path = list(sys.path)
    try:
        sys.path.insert(0, str(path.parent))
        spec.loader.exec_module(result)
    finally:
        sys.path[:] = previous_path
    return result


def retained_builder():
    for name, expected in DEPENDENCIES.items():
        need(sha(REPO / name) == expected, "Retained identity implementation changed: " + name)
    result = module(REPO / next(iter(DEPENDENCIES)), "r146_route_inherited")
    result.verify_dependencies()
    return result


def extract_fingerprint(raw):
    docs = []
    for match in re.finditer(br'\{"[A-Za-z][A-Za-z0-9_]*":', raw):
        end = raw.find(b"\0", match.start())
        if end < 0:
            continue
        try:
            value = json.loads(raw[match.start():end].decode("ascii"))
        except (ValueError, UnicodeError):
            continue
        if isinstance(value, dict) and "baseApkSha256" in value and "payloadSha256" in value:
            docs.append(value)
    need(len(docs) == 1, "Exactly one embedded wrapper identity required")
    value = docs[0]
    need(canonical(value) in raw and digest(canonical(value)).encode("ascii") in raw,
         "Canonical wrapper manifest and fingerprint differ")
    return value


def transforms_for(previous, pins):
    old = previous["psx"]["productiveTransforms"]
    extra = {ROOT.name + "/" + name: checksum for name, checksum in pins.items()}
    need(not set(old).intersection(extra), "R146 source chain must append without overwriting history")
    return {**old, **extra}


def validate_marker_bindings(original, previous, payload, pins, markers, files):
    inherited = retained_builder()
    transforms = transforms_for(previous, pins)
    need(set(markers) == set(WRAPPERS), "Exactly three renewed identity wrappers required")
    for kind, (library, parent_hash) in WRAPPERS.items():
        raw = Path(files["lib/arm64-v8a/" + library]).read_bytes()
        actual = extract_fingerprint(raw)
        wanted = copy.deepcopy(previous[kind])
        wanted.update(baseApkSha256=BASE, payloadSha256=payload, productiveTransforms=transforms)
        if kind != "psx":
            wanted.update(parentFingerprintSha256=digest(canonical(previous[kind])), parentRuntimeSha256=parent_hash,
                          psxRuntimeSha256=markers["psx"]["runtimeSha256"])
        marker = markers[kind]
        need(marker.get("runtimeLibrary") == library and marker.get("runtimeSha256") == digest(raw) != parent_hash and
             marker.get("runtimeBytes") == len(raw) and marker.get("fingerprintSha256") == digest(canonical(actual)) and
             actual == wanted and inherited.policy(actual) == inherited.policy(previous[kind]),
             "Owner implementation, dependencies, controllers, options or canonical binding differs: " + kind)
        wrapper_contract(original.read("lib/arm64-v8a/" + library), raw, kind)
    return inherited.expected_engines(json.loads(original.read("assets/station-online/engines.json")), markers)


def validate_dex_receipt(receipt, directory, commit, pins):
    route = module(ROOT / 'recipe/route_scope.py', 'r146_exact_route_scope')
    plan = route.reviewed_plan()
    need(plan['modifiedClasses'] == sorted({route.TLS, route.CHANNEL}) and plan['unchangedClassCount'] == 606 and
         plan['newMethods'] == {route.TLS: [route.NEW_CREATE]} and
         plan['modifiedMethods'] == {route.TLS: [route.ENDPOINT], route.CHANNEL: [route.CHANNEL_CTOR]},
         'Only endpoint, dedicated factory and one Channel factory call are authorized')
    need(receipt.get('schema') == 'station.r146.direct-v3-relay.dex.v1' and receipt.get('passed') is True and
         receipt.get('sourceCommit') == commit and receipt.get('sourceFiles') == pins and
         receipt.get('baselineSourceCommit') == BASE_SOURCE and receipt.get('baselineApkSha256') == BASE and
         receipt.get('baselineApkBytes') == BASE_BYTES and
         receipt.get('scopeDeclarationSha256') == sha(ROOT / 'evidence/route-scope.json') and
         receipt.get('productionMethodStrategy') == 'actual-donor-smali-with-exact-route-method-overlay' and
         set(receipt.get('payloads', {})) == set(receipt.get('scopes', {})) == PARTITIONS and
         receipt.get('preservedDexSha256') == plan['preservedDexSha256'] and
         set(receipt['preservedDexSha256']) == ROOT_DEX - PARTITIONS and
         receipt.get('inversePassed') is receipt.get('inverseWholeClassPassed') is receipt.get('postAssemblyInversePassed') is True and
         receipt.get('unrelatedMethodsPreserved') is receipt.get('legacyRelayAndApiAuthPreserved') is True and
         receipt.get('ticketProofPathProtocolReadyAckAndExitPreserved') is True and
         receipt.get('nativeEnginesProfilesHleMultitapAndGameplayPreserved') is True and
         receipt.get('newMethods') == plan['newMethods'] and receipt.get('newFields') == receipt.get('newClasses') == [] and
         receipt.get('apkAssembledOrSigned') is receipt.get('phoneAccessed') is receipt.get('liveServerCalled') is False,
         'Qualified actual route DEX assembly, full inverse and exact 39 retained DEX proofs required')
    tests = read(ROOT / 'evidence/host-test-receipt.json')
    need(receipt.get('hostTestReceiptSha256') == sha(ROOT / 'evidence/host-test-receipt.json') and
         tests.get('schema') == 'station.r146.direct-v3-route.host-tests.v1' and tests.get('passed') is True and
         tests.get('scopeDeclarationSha256') == receipt['scopeDeclarationSha256'] and
         tests.get('actualWebSocketHttpsHostnameIdentificationPreserved') is True and
         len(tests.get('negativeGuards', [])) == 5 and tests.get('hostProbe', {}).get('checks', 0) >= 20 and
         tests.get('javaTlsSourceSha256') == sha(ROOT / 'java/org/emulationstation/frontend/netplay/StationRelayTls.java') and
         tests.get('hostProbeSourceSha256') == sha(ROOT / 'tests/StationRelayTlsRouteProbe.java'),
         'Matching meaningful host TLS and inverse test receipt required')
    path = Path(directory) / PARTITION
    payload, scope = receipt['payloads'][PARTITION], receipt['scopes'][PARTITION]
    need(path.is_file() and not path.is_symlink() and Path(payload.get('path', '')).resolve() == path.resolve() and
         payload.get('bytes') == path.stat().st_size and payload.get('sha256') == sha(path) != DEX_BASE[PARTITION],
         'Exact assembled actual scoped DEX required')
    changed = set(plan['modifiedClasses'])
    before, after, unchanged = (scope.get(key, {}) for key in
                               ('baselineClassSha256', 'outputClassSha256', 'unchangedClassSha256'))
    expected = {**plan['baselineClassSha256'], **plan['proposedClassSha256']}
    need(scope.get('baselineDexSha256') == DEX_BASE[PARTITION] and scope.get('outputDexSha256') == sha(path) and
         scope.get('originalClassCount') == scope.get('finalClassCount') == 608 and scope.get('unchangedClasses') == 606 and
         scope.get('modifiedClasses') == plan['modifiedClasses'] and scope.get('modifiedMethods') == plan['modifiedMethods'] and
         scope.get('newMethods') == plan['newMethods'] and
         scope.get('newFields') == scope.get('newClasses') == scope.get('removedClasses') ==
         scope.get('removedMethods') == scope.get('addedClasses') == [] and
         scope.get('methodBaselineSha256') == scope.get('methodInverseSha256') == plan['baselineMethodSha256'] and
         scope.get('methodOutputSha256') == plan['proposedMethodSha256'] and
         scope.get('inverseClassSha256') == {kind: plan['baselineClassSha256'][kind] for kind in changed} and
         before == plan['baselineClassSha256'] and after == expected and len(before) == len(after) == 608 and
         set(before) == set(after) and set(unchanged) == set(before) - changed and len(unchanged) == 606 and
         {kind: before[kind] for kind in unchanged} == {kind: after[kind] for kind in unchanged} == unchanged and
         {kind for kind in before if before[kind] != after[kind]} == changed and
         all(scope.get(flag) is True for flag in ('inverseWholeClassPassed', 'postassemblyInversePassed',
             'unrelatedClassesByteIdentical', 'unrelatedMethodsPreserved', 'staticInitializersPreserved',
             'onlyReviewedRouteMethodsChanged')),
         'Whole two-class inverse and exact added-method/method-map allowlist required')
    return receipt, {PARTITION: path}


def expected_payload(previous, dex_paths):
    old = previous['psx']['payloadSha256']
    need(len(old) == 345 and old.get(CAROUSEL) == CAROUSEL_SHA and old.get(PARTITION) == DEX_BASE[PARTITION],
         'Exact complete R145 inherited payload required')
    result = {**old, PARTITION: sha(dex_paths[PARTITION])}
    need(set(dex_paths) == PARTITIONS and len(result) == 345 and
         {name for name in old if old[name] != result[name]} == {PARTITION},
         'Only the approved route DEX hash may change in the complete owner payload')
    return result


def build(a):
    need(a.base.stat().st_size == BASE_BYTES and sha(a.base) == BASE, "Exact signed R145 donor required")
    pins = verify_commit(a.source_commit)
    dex, dex_paths = validate_dex_receipt(read(a.dex_receipt), a.dex_dir, a.source_commit, pins)
    parent_proof = verify_parent_proof(a.parent_proof)
    with zipfile.ZipFile(a.base) as archive:
        previous = fingerprints(archive)
        need(entry_sha(archive, "lib/arm64-v8a/libstation_retroarch.so") == RETRO and
             all(entry_sha(archive, name) == checksum for name, checksum in DEX_BASE.items()) and
             entry_sha(archive, CAROUSEL) == CAROUSEL_SHA, "Actual R145 runtime and route donor identity required")
        original = json.loads(archive.read("assets/station-online/engines.json"))
        for name, checksum in previous["psx"]["payloadSha256"].items():
            need(entry_sha(archive, name) == checksum, "Inherited payload differs: " + name)
        need({name: entry_sha(archive, name) for name in ROOT_DEX - PARTITIONS} == dex["preservedDexSha256"],
             "All 39 unrelated DEX partitions must remain exact")
        need(elf_contract(archive.read(CAROUSEL))["soname"] == ["libturbo_carousel.so"],
             "Original carousel SONAME/alignment required")
    payload = expected_payload(previous, dex_paths)
    transforms = transforms_for(previous, pins)
    inherited = retained_builder()
    for name in ("StationPsxEntry.cpp", "StationPsxOwner.cpp", "StationPsxOwner.hpp", "StationPsxProtocol.cpp",
                 "StationPsxProtocol.hpp", "StationPsxSha256.cpp", "PsxPinnedOptions.h"):
        need(sha(inherited.PSX / "native" / name) == previous["psx"]["productiveTransforms"].get("native/" + name),
             "Retained PSX productive source changed: " + name)
    native_tools = inherited.native_tools(a.ndk)
    out = isolated(a.out)
    out.mkdir(parents=True)
    markers = {}
    psx = copy.deepcopy(previous["psx"])
    psx.update(baseApkSha256=BASE, payloadSha256=payload, productiveTransforms=transforms)
    need(inherited.policy(psx) == inherited.policy(previous["psx"]), "Original PSX owner policy changed")
    raw = canonical(psx)
    (out / "psx.fingerprint.json").write_bytes(raw + b"\n")
    identity_source = out / "StationPsxIdentity.cpp"
    identity_source.write_text(
        'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeIdentity(){return "' + digest(raw) + '";}\n' +
        'extern "C" __attribute__((visibility("default"))) const char* StationPsxRuntimeManifest(){return ' + json.dumps(raw.decode("ascii")) + ';}\n',
        encoding="ascii")
    native_out = out / "native"
    subprocess.run([sys.executable, "-B", str(inherited.PSX / "recipe/build_entry.py"), "--ndk", str(a.ndk),
                    "--owner", str(inherited.PSX / "native"), "--protocol", str(inherited.PSX / "native"),
                    "--pinned-options", str(inherited.PSX / "native"), "--identity-source", str(identity_source), "--out", str(native_out)],
                   check=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    psx_binary = native_out / WRAPPERS["psx"][0]
    need(raw in psx_binary.read_bytes(), "Canonical PSX identity embedding failed")
    markers["psx"] = dict(runtimeLibrary=psx_binary.name, runtimeSha256=sha(psx_binary),
                          runtimeBytes=psx_binary.stat().st_size, fingerprintSha256=digest(raw))
    primitive = module(REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py", "r146_route_marker")
    for kind in ("n64", "dolphin"):
        value = copy.deepcopy(previous[kind])
        library, parent_runtime = WRAPPERS[kind]
        value.update(baseApkSha256=BASE, payloadSha256=payload, productiveTransforms=transforms,
                     parentFingerprintSha256=digest(canonical(previous[kind])), parentRuntimeSha256=parent_runtime,
                     psxRuntimeSha256=markers["psx"]["runtimeSha256"])
        need(inherited.policy(value) == inherited.policy(previous[kind]), "Independent owner policy changed: " + kind)
        (out / (library + ".fingerprint.json")).write_bytes(canonical(value) + b"\n")
        api = "StationMupenRuntime" if kind == "n64" else "StationDolphinRuntime"
        markers[kind] = primitive.marker(value, library, api, a.ndk, out)
    files = {"lib/arm64-v8a/" + library: (out / "native" / library if kind == "psx" else out / library)
             for kind, (library, _) in WRAPPERS.items()}
    with zipfile.ZipFile(a.base) as archive:
        updated, selected = validate_marker_bindings(archive, previous, payload, pins, markers, files)
    retro = [row for row in original["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}]
    need(len(original["engines"]) == len(updated["engines"]) == 13 and len(retro) == 9 and
         [row for row in updated["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}] == retro,
         "All nine RetroArch descriptors and their eight active IDs must stay exact")
    (out / "engines.json").write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    need(inherited.native_tools(a.ndk) == native_tools and verify_commit(a.source_commit) == pins and
         read(a.dex_receipt) == dex and verify_parent_proof(a.parent_proof) == parent_proof and
         all(sha(path) == payload[name] for name, path in dex_paths.items()) and payload[CAROUSEL] == CAROUSEL_SHA,
         "Frozen route sources, receipts, payloads or native tools changed during marker build")
    receipt = dict(schema="station.r146.direct-v3-relay.identity.v1", passed=True, compiled=True, sourceCommit=a.source_commit,
        sourceFiles=pins, nativeToolFiles=native_tools, retainedIdentityDependencies=DEPENDENCIES, baselineApkSha256=BASE,
        changedDexSha256={name: sha(path) for name, path in dex_paths.items()}, carouselSha256=CAROUSEL_SHA, payloadSha256=payload,
        markers=markers, engines=selected, enginesAssetSha256=sha(out / "engines.json"),
        preservedRetroArchSha256=RETRO, preservedRetroArchDescriptors=retro, preservedDexSha256=dex["preservedDexSha256"],
        dexBuildReceiptSha256=sha(a.dex_receipt), parentFinalProofSha256=sha(a.parent_proof),
        scopeDeclarationSha256=sha(ROOT / "evidence/route-scope.json"),
        inheritedPayloadCount=345, finalPayloadCount=345, changedPayloadEntries=sorted(CHANGED_PAYLOAD), **state_fields())
    (out / "runtime-identity.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('base','dex-dir','dex-receipt','ndk','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--parent-proof',type=Path,default=PARENT_PROOF_PATH)
    parser.add_argument('--source-commit',required=True)
    result=build(parser.parse_args())
    print(json.dumps({'passed':True,'revision':'R146','renewedIndependentIds':len(result['engines']),'preservedRetroArchDescriptors':9}))
