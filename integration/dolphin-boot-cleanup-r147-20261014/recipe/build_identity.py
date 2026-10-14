"""Bind qualified R147 DEX10 and rebuilt Dolphin motor, preserving other policies."""
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
    result = module(REPO / next(iter(DEPENDENCIES)), "r147_route_inherited")
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


def validate_dex_receipt(receipt, directory, commit, pins):
    builder = module(ROOT / 'recipe/build_dex.py', 'r147_dex_contract')
    plan = builder.reviewed_plan()
    kind = builder.TYPE
    need(receipt.get('schema') == 'station.r147.dolphin.boot-ownership.dex.v1' and receipt.get('passed') is True and
         receipt.get('sourceCommit') == commit and receipt.get('sourceFiles') == pins and
         receipt.get('baselineApkSha256') == BASE and receipt.get('baselineApkBytes') == BASE_BYTES and
         receipt.get('baselineSourceCommit') == BASE_SOURCE and
         receipt.get('scopeDeclarationSha256') == sha(ROOT / 'evidence/dex10-scope.json') and
         receipt.get('productionMethodStrategy') == 'donor-smali-only' and
         set(receipt.get('payloads', {})) == set(receipt.get('scopes', {})) == PARTITIONS and
         receipt.get('preservedDexSha256') == plan['preservedDexSha256'] and
         set(receipt['preservedDexSha256']) == ROOT_DEX - PARTITIONS and
         receipt.get('inversePassed') is receipt.get('inverseWholeClassPassed') is receipt.get('postAssemblyInversePassed') is True and
         receipt.get('unrelatedMethodsPreserved') is True and
         receipt.get('newMethods') == receipt.get('newFields') == receipt.get('newClasses') == [] and
         receipt.get('r146RouteVisualControlsInputsProfilesAndReadinessPreserved') is True and
         receipt.get('ownershipClassMonitorSitesAdded') == 3 and receipt.get('newPerFrameJniCalls') == 0 and
         receipt.get('newSchedulersOrThreads') == 0 and receipt.get('nativeOrCallbackInsideOwnershipMonitor') is False and
         receipt.get('sourceProofSha256') == plan['sourceProofSha256'] and
         receipt.get('apkAssembledOrSigned') is receipt.get('nativeCoreCompiledByThisRecipe') is False and
         receipt.get('phoneAccessed') is receipt.get('serverAccessed') is False,
         'Qualified actual one-class DEX10 ownership repair and exact 39 retained DEX proofs required')
    path = Path(directory) / PARTITION
    payload, scope = receipt['payloads'][PARTITION], receipt['scopes'][PARTITION]
    need(path.is_file() and not path.is_symlink() and Path(payload.get('path', '')).resolve() == path.resolve() and
         payload.get('bytes') == path.stat().st_size and payload.get('sha256') == sha(path) != DEX_BASE[PARTITION],
         'Exact assembled ownership DEX required')
    before, after, unchanged = (scope.get(key, {}) for key in
                               ('baselineClassSha256', 'outputClassSha256', 'unchangedClassSha256'))
    expected = {**plan['baselineClassSha256'], **plan['proposedCanonicalClassSha256']}
    need(scope.get('baselineDexSha256') == DEX_BASE[PARTITION] and scope.get('outputDexSha256') == sha(path) and
         scope.get('originalClassCount') == scope.get('finalClassCount') == 4991 and scope.get('unchangedClasses') == 4990 and
         scope.get('modifiedClasses') == [kind] and scope.get('modifiedMethods') == {kind: builder.METHODS} and
         scope.get('originalModifiedClassMethodCount') == scope.get('finalModifiedClassMethodCount') == 63 and
         scope.get('unchangedModifiedClassMethods') == 59 and scope.get('unchangedModifiedClassFields') == 40 and
         scope.get('newMethods') == scope.get('newFields') == scope.get('newClasses') ==
         scope.get('removedClasses') == scope.get('removedMethods') == scope.get('addedClasses') == [] and
         scope.get('methodBaselineSha256') == scope.get('methodInverseSha256') == plan['baselineMethodSha256'] and
         scope.get('methodOutputSha256') == plan['canonicalMethodSha256'] and
         scope.get('inverseClassSha256') == {kind: plan['baselineClassSha256'][kind]} and
         before == plan['baselineClassSha256'] and after == expected and len(before) == len(after) == 4991 and
         set(before) == set(after) and set(unchanged) == set(before) - {kind} and len(unchanged) == 4990 and
         {key: before[key] for key in unchanged} == {key: after[key] for key in unchanged} == unchanged and
         {key for key in before if before[key] != after[key]} == {kind} and
         all(scope.get(flag) is True for flag in ('inverseWholeClassPassed', 'postassemblyInversePassed',
             'unrelatedClassesByteIdentical', 'unrelatedMethodsPreserved', 'staticInitializersPreserved',
             'onlyReviewedOwnershipMethodsChanged', 'canonicalInstructionBranchAndTryProofPassed')),
         'Complete one-class inverse, canonical instruction proof and all 59 unrelated methods required')
    return receipt, {PARTITION: path}


def validate_native_receipt(receipt, path, commit, pins):
    builder = module(ROOT / 'recipe/build_native.py', 'r147_native_contract')
    native_pins = builder.source_map()
    need(set(native_pins) == {'native/Source/Android/jni/MainAndroid.cpp', 'recipe/build_native.py',
         'recipe/StationDolphinMainAndroidOverride.cmake', 'evidence/native-scope.json'} and
         all(pins.get(name) == checksum for name, checksum in native_pins.items()),
         'Four native productive inputs must share the combined frozen source closure')
    declaration = read(ROOT / 'evidence/native-scope.json')
    need(declaration.get('schema') == 'station.r147.dolphin.boot-cleanup.native-scope.v1' and
         declaration.get('baselineCoreSha256') == CORE_SHA and declaration.get('baselineUnstrippedCoreSha256') == CORE_UNSTRIPPED_SHA and
         declaration.get('privateInputReceiptSha256') == PRIVATE_NATIVE_CLOSURES and
         declaration.get('modifiedFiles') == ['Source/Android/jni/MainAndroid.cpp'] and
         declaration.get('productiveAddedLines') == 1 and declaration.get('productiveRemovedLines') == 0 and
         declaration.get('sourceInverseWholeFilePassed') is True and
         declaration.get('fullBaselineByteReproductionMandatory') is True and
         declaration.get('allFourHooksMustRemainByteExact') is True,
         'Exact one-line native plan and full original-stage qualification required')
    need(receipt.get('schema') == 'station.r147.dolphin.boot-cleanup.native.v1' and
         receipt.get('passed') is receipt.get('compiled') is True and receipt.get('sourceCommit') == commit and
         receipt.get('sourceSha256') == native_pins and receipt.get('completeFrozenSourceFiles') == pins and
         receipt.get('actualDonorApkSha256') == BASE and receipt.get('baselineNativeSha256') == CORE_SHA and
         receipt.get('baselineReproduced') == {'dolphinCore': True, 'allFourHooks': True} and
         receipt.get('sourceScopeDeclarationSha256') == sha(ROOT / 'evidence/native-scope.json') and
         receipt.get('originalSourceTreeClosureSha256') == PRIVATE_NATIVE_CLOSURES['sourceClosure'] and
         receipt.get('originalBuildClosureSha256') == PRIVATE_NATIVE_CLOSURES['buildClosure'] and
         receipt.get('originalGraphClosureSha256') == PRIVATE_NATIVE_CLOSURES['graphClosure'] and
         receipt.get('inverseWholeFilePassed') is receipt.get('originalSourceStageExactlyPreserved') is True and
         receipt.get('normalRunAndSurfaceAndStopFunctionsPreserved') is True and
         receipt.get('onlyNativeChange') == 'One boot-flag clear in null BootSessionData early return' and
         receipt.get('cpuJitCacheOptionsControllersProfilesNetworkChanged') is receipt.get('frontendChanged') is
         receipt.get('dexChanged') is False and receipt.get('exportedSymbolsExactlyPreserved') is
         receipt.get('dependenciesExactlyPreserved') is receipt.get('sonameExactlyPreserved') is True and
         receipt.get('nativeLoadAlignment') == 16384 and receipt.get('sourceDateEpoch') == 1790576668 and
         receipt.get('fullTargetsBuilt') is True and receipt.get('archivedObjectsReused') is False and
         receipt.get('androidExecuted') is receipt.get('physicalGameplayVerified') is False and
         set(receipt.get('baselinePayloads', {})) == set(receipt.get('payloads', {})) == set(NATIVE_BASE) and
         len(receipt.get('baselineGeneratedInputSha256', {})) == len(receipt.get('generatedInputSha256', {})) == 94 and
         receipt.get('unchangedGeneratedInputs') == 93 and
         receipt.get('originalPackagingAssetsRedirected') is receipt.get('inTreeScmrevAbsencePreserved') is True and
         len(receipt.get('nativeSourceInputSha256', {})) == declaration['fullOriginalStageFiles'] and
         len(receipt.get('buildDependencyInputSha256', {})) == declaration['actualHeaderAndRuntimePins'],
         'Actual full baseline reproduction and productive core receipt required; source-only proof is insufficient')
    before_inputs, after_inputs = receipt['baselineGeneratedInputSha256'], receipt['generatedInputSha256']
    delta = receipt.get('approvedGeneratedObjectDelta', {})
    need(set(before_inputs) == set(after_inputs) and
         set(delta) == {'originalRelativePath', 'productiveRelativePath', 'baselineSha256', 'productiveSha256', 'compiledSourceSha256'} and
         {key for key in before_inputs if before_inputs[key] != after_inputs[key]} == {delta.get('originalRelativePath')} and
         str(delta['originalRelativePath']).endswith('MainAndroid.cpp.o') and
         delta['baselineSha256'] == before_inputs[delta['originalRelativePath']] and
         delta['productiveSha256'] == after_inputs[delta['originalRelativePath']] and
         delta['compiledSourceSha256'] == native_pins['native/Source/Android/jni/MainAndroid.cpp'] and
         Path(delta['productiveRelativePath']).suffix == '.o',
         'Only the full-built MainAndroid object may differ among the 94 generated inputs')
    for name, original_sha in NATIVE_BASE.items():
        old, new = receipt['baselinePayloads'][name], receipt['payloads'][name]
        need(old.get('sha256') == original_sha and sha(old['path']) == original_sha and
             Path(old['path']).stat().st_size == old['bytes'], 'Exact fully rebuilt baseline payload required: ' + name)
        need(sha(new['path']) == new['sha256'] and Path(new['path']).stat().st_size == new['bytes'] and
             builder.elf(Path(new['path']).read_bytes()) == new['elf'] == old['elf'] and
             elf_contract(Path(new['path']).read_bytes()) == elf_contract(Path(old['path']).read_bytes()),
             'Built native payload API, dependencies, SONAME, alignment or actual bytes changed: ' + name)
        if name != CORE_LIBRARY:
            need(new['sha256'] == original_sha, 'All four hooks must remain byte exact')
    payload = receipt['payloads'][CORE_LIBRARY]
    need(Path(payload['path']).resolve() == Path(path).resolve() and payload['sha256'] == sha(path) != CORE_SHA and
         receipt['outputNativeSha256'] == payload['sha256'] and
         receipt['baselinePayloads'][CORE_LIBRARY]['unstrippedSha256'] == CORE_UNSTRIPPED_SHA,
         'New actual Dolphin core and full unstripped original baseline must be qualified')
    return receipt


def expected_payload(previous, dex_paths):
    old = previous['psx']['payloadSha256']
    need(len(old) == 345 and CORE not in old and old.get(PARTITION) == DEX_BASE[PARTITION] and
         old.get(CAROUSEL) == CAROUSEL_SHA, 'Exact complete R146 inherited payload required')
    result = {**old, PARTITION: sha(dex_paths[PARTITION])}
    need(set(dex_paths) == PARTITIONS and len(result) == 345 and
         {name for name in old if old[name] != result[name]} == CHANGED_PAYLOAD,
         'Only DEX10 may change in the inherited 345-entry owner payload; core has separate existing bindings')
    return result


def project_linked_refs(previous, kind, payload, core_sha):
    """Exact patch of current duplicated payload/core references; no policy omission."""
    result = copy.deepcopy(previous)
    need(CORE not in payload and len(payload) == 345 and re.fullmatch('[0-9a-f]{64}', core_sha) and core_sha != CORE_SHA,
         'Preserved 345-entry payload shape and separately qualified new Dolphin core hash required')
    need(previous['preservedPayloadSha256'][PARTITION] == DEX_BASE[PARTITION],
         'Existing DEX10 reference must match the actual R146 donor')
    result['preservedPayloadSha256'][PARTITION] = payload[PARTITION]
    if kind in {'n64', 'dolphin'}:
        need(previous['compiledBackendSha256'][CORE_LIBRARY] == CORE_SHA,
             'Existing shared Dolphin binary reference must match the actual donor')
        result['compiledBackendSha256'][CORE_LIBRARY] = core_sha
    if kind == 'dolphin':
        need(previous['coreSha256'] == CORE_SHA, 'Original Dolphin owner core binding differs')
        result['coreSha256'] = core_sha
    inverse = copy.deepcopy(result)
    inverse['preservedPayloadSha256'][PARTITION] = previous['preservedPayloadSha256'][PARTITION]
    if kind in {'n64', 'dolphin'}:
        inverse['compiledBackendSha256'][CORE_LIBRARY] = previous['compiledBackendSha256'][CORE_LIBRARY]
    if kind == 'dolphin':
        inverse['coreSha256'] = previous['coreSha256']
    need(inverse == previous and (kind == 'psx' or result['nativeBuild'] == previous['nativeBuild']),
         'All unrequested owner policy and historical build provenance must remain exact')
    return result


def transforms_for(previous, pins, native_receipt_path, native_receipt):
    old = previous['psx']['productiveTransforms']
    extra = {ROOT.name + '/' + name: checksum for name, checksum in pins.items()}
    extra.update({ROOT.name + '/qualified-native-receipt.json': sha(native_receipt_path),
                  ROOT.name + '/qualified-dolphin-core.so': native_receipt['outputNativeSha256'],
                  ROOT.name + '/qualified-native-source-map.json': digest(canonical(native_receipt['sourceSha256']))})
    need(not set(old).intersection(extra), 'R147 qualification must append without rewriting historical source provenance')
    return {**old, **extra}


def expected_engines(original, markers, core_sha):
    inherited = retained_builder()
    updated, selected = inherited.expected_engines(original, markers)
    need(core_sha != CORE_SHA and re.fullmatch('[0-9a-f]{64}', core_sha), 'Actual qualified new Dolphin core hash required')
    for before, after in zip(original['engines'], updated['engines']):
        platform = after['platform']
        if platform in {'gamecube', 'wii'}:
            need(before['library'] == CORE_LIBRARY and before['coreSha256'] == CORE_SHA,
                 'Actual existing Dolphin engine descriptor required')
            after['coreSha256'] = core_sha
            permitted = {'engineId', 'runtimeSha256', 'coreSha256'}
        elif platform in {'psx', 'n64'}:
            permitted = {'engineId', 'runtimeSha256'}
        else:
            need(after == before, 'All nine RetroArch descriptors must stay exact')
            continue
        need({key: value for key, value in before.items() if key not in permitted} ==
             {key: value for key, value in after.items() if key not in permitted},
             'Options, controls, profiles, extensions or unrequested engine policy changed')
    return updated, [row for row in updated['engines'] if row['platform'] in {'psx', 'n64', 'gamecube', 'wii'}]


def validate_marker_bindings(original, previous, payload, pins, markers, files, native_receipt_path, native_receipt):
    inherited = retained_builder()
    transforms = transforms_for(previous, pins, native_receipt_path, native_receipt)
    need(set(markers) == set(WRAPPERS), 'Exactly three renewed identity wrappers required')
    core_sha = native_receipt['outputNativeSha256']
    for kind, (library, parent_hash) in WRAPPERS.items():
        raw = Path(files['lib/arm64-v8a/' + library]).read_bytes()
        actual = extract_fingerprint(raw)
        wanted = project_linked_refs(previous[kind], kind, payload, core_sha)
        wanted.update(baseApkSha256=BASE, payloadSha256=payload, productiveTransforms=transforms)
        if kind != 'psx':
            wanted.update(parentFingerprintSha256=digest(canonical(previous[kind])), parentRuntimeSha256=parent_hash,
                          psxRuntimeSha256=markers['psx']['runtimeSha256'])
        marker = markers[kind]
        need(actual == wanted and inherited.policy(actual) == inherited.policy(project_linked_refs(previous[kind], kind, payload, core_sha)) and
             marker.get('runtimeLibrary') == library and marker.get('runtimeSha256') == digest(raw) != parent_hash and
             marker.get('runtimeBytes') == len(raw) and marker.get('fingerprintSha256') == digest(canonical(actual)),
             'Exact linked-reference patch and canonical owner identity required: ' + kind)
        wrapper_contract(original.read('lib/arm64-v8a/' + library), raw, kind)
    return expected_engines(json.loads(original.read('assets/station-online/engines.json')), markers, core_sha)


def build(a):
    need(a.base.stat().st_size == BASE_BYTES and sha(a.base) == BASE, "Exact signed R146 donor required")
    pins = verify_commit(a.source_commit)
    dex, dex_paths = validate_dex_receipt(read(a.dex_receipt), a.dex_dir, a.source_commit, pins)
    parent_proof = verify_parent_proof(a.parent_proof)
    native_receipt = validate_native_receipt(read(a.native_receipt), a.native, a.source_commit, pins)
    with zipfile.ZipFile(a.base) as archive:
        previous = fingerprints(archive)
        need(entry_sha(archive, "lib/arm64-v8a/libstation_retroarch.so") == RETRO and
             all(entry_sha(archive, name) == checksum for name, checksum in DEX_BASE.items()) and
             entry_sha(archive, CAROUSEL) == CAROUSEL_SHA, "Actual R146 runtime and route donor identity required")
        original = json.loads(archive.read("assets/station-online/engines.json"))
        for name, checksum in previous["psx"]["payloadSha256"].items():
            need(entry_sha(archive, name) == checksum, "Inherited payload differs: " + name)
        need({name: entry_sha(archive, name) for name in ROOT_DEX - PARTITIONS} == dex["preservedDexSha256"],
             "All 39 unrelated DEX partitions must remain exact")
        need(elf_contract(archive.read(CAROUSEL))["soname"] == ["libturbo_carousel.so"],
             "Original carousel SONAME/alignment required")
    payload = expected_payload(previous, dex_paths)
    transforms = transforms_for(previous, pins, a.native_receipt, native_receipt)
    inherited = retained_builder()
    for name in ("StationPsxEntry.cpp", "StationPsxOwner.cpp", "StationPsxOwner.hpp", "StationPsxProtocol.cpp",
                 "StationPsxProtocol.hpp", "StationPsxSha256.cpp", "PsxPinnedOptions.h"):
        need(sha(inherited.PSX / "native" / name) == previous["psx"]["productiveTransforms"].get("native/" + name),
             "Retained PSX productive source changed: " + name)
    native_tools = inherited.native_tools(a.ndk)
    out = isolated(a.out)
    out.mkdir(parents=True)
    markers = {}
    core_sha = native_receipt['outputNativeSha256']
    psx = project_linked_refs(previous["psx"], "psx", payload, core_sha)
    psx.update(baseApkSha256=BASE, payloadSha256=payload, productiveTransforms=transforms)
    need(inherited.policy(psx) == inherited.policy(project_linked_refs(previous["psx"], "psx", payload, core_sha)), "Original PSX owner policy changed")
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
    primitive = module(REPO / "versions/station-dolphin-online-r126-20261011/recipe/build_runtime_identity.py", "r147_route_marker")
    for kind in ("n64", "dolphin"):
        value = project_linked_refs(previous[kind], kind, payload, core_sha)
        library, parent_runtime = WRAPPERS[kind]
        value.update(baseApkSha256=BASE, payloadSha256=payload, productiveTransforms=transforms,
                     parentFingerprintSha256=digest(canonical(previous[kind])), parentRuntimeSha256=parent_runtime,
                     psxRuntimeSha256=markers["psx"]["runtimeSha256"])
        need(inherited.policy(value) == inherited.policy(project_linked_refs(previous[kind], kind, payload, core_sha)), "Independent owner policy changed: " + kind)
        (out / (library + ".fingerprint.json")).write_bytes(canonical(value) + b"\n")
        api = "StationMupenRuntime" if kind == "n64" else "StationDolphinRuntime"
        markers[kind] = primitive.marker(value, library, api, a.ndk, out)
    files = {"lib/arm64-v8a/" + library: (out / "native" / library if kind == "psx" else out / library)
             for kind, (library, _) in WRAPPERS.items()}
    with zipfile.ZipFile(a.base) as archive:
        updated, selected = validate_marker_bindings(archive, previous, payload, pins, markers, files, a.native_receipt, native_receipt)
    retro = [row for row in original["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}]
    need(len(original["engines"]) == len(updated["engines"]) == 13 and len(retro) == 9 and
         [row for row in updated["engines"] if row["platform"] not in {"psx", "n64", "gamecube", "wii"}] == retro,
         "All nine RetroArch descriptors and their eight active IDs must stay exact")
    (out / "engines.json").write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    need(inherited.native_tools(a.ndk) == native_tools and verify_commit(a.source_commit) == pins and
         read(a.dex_receipt) == dex and read(a.native_receipt) == native_receipt and verify_parent_proof(a.parent_proof) == parent_proof and
         all(sha(path) == payload[name] for name, path in dex_paths.items()) and payload[CAROUSEL] == CAROUSEL_SHA and
         sha(a.native) == core_sha == native_receipt['outputNativeSha256'],
         "Frozen route sources, receipts, payloads or native tools changed during marker build")
    receipt = dict(schema="station.r147.dolphin-boot-cleanup.identity.v1", passed=True, compiled=True, sourceCommit=a.source_commit,
        sourceFiles=pins, nativeToolFiles=native_tools, retainedIdentityDependencies=DEPENDENCIES, baselineApkSha256=BASE,
        changedDexSha256={name: sha(path) for name, path in dex_paths.items()}, carouselSha256=CAROUSEL_SHA, payloadSha256=payload,
        markers=markers, engines=selected, enginesAssetSha256=sha(out / "engines.json"),
        preservedRetroArchSha256=RETRO, preservedRetroArchDescriptors=retro, preservedDexSha256=dex["preservedDexSha256"],
        dexBuildReceiptSha256=sha(a.dex_receipt), parentFinalProofSha256=sha(a.parent_proof),
        scopeDeclarationSha256=sha(ROOT / "evidence/dex10-scope.json"),
        nativeScopeDeclarationSha256=sha(ROOT / "evidence/native-scope.json"),
        nativeBuildReceiptSha256=sha(a.native_receipt), changedDolphinCoreSha256=sha(a.native),
        inheritedPayloadCount=345, finalPayloadCount=345, changedPayloadEntries=sorted(CHANGED_PAYLOAD),
        changedApkProductiveEntries=sorted(CHANGED_APK_PAYLOAD), **state_fields())
    (out / "runtime-identity.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('base','dex-dir','dex-receipt','native','native-receipt','ndk','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--parent-proof',type=Path,default=PARENT_PROOF_PATH)
    parser.add_argument('--source-commit',required=True)
    result=build(parser.parse_args())
    print(json.dumps({'passed':True,'revision':'R147','renewedIndependentIds':len(result['engines']),'preservedRetroArchDescriptors':9}))
