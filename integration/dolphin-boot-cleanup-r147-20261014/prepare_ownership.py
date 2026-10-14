"""Private exact-method ownership overlay; no productive build or edits."""
from pathlib import Path
import hashlib
import json
import re
import audit_ownership as a

ROOT = Path(__file__).resolve().parent
TYPE = 'Lorg/dolphinemu/dolphinemu/features/netplay/NetplaySession;'
GETTER = '.method public final isLaunching()Z'
BOOT = '.method public final onBootGame(Ljava/lang/String;J)V'
SIGNATURES = [a.CONSUME, a.RELEASE, GETTER, BOOT]


def wrapped(original, result):
    nl = '\r\n' if '\r\n' in original else '\n'
    signature, rest = original.split(nl, 1)
    assert rest.count('    .locals 4') == 1 and 'monitor-' not in rest
    rest = rest.replace('    .locals 4', '    .locals 6', 1)
    start = rest.index(nl + nl) + len(nl + nl)
    body = rest[start:rest.rindex('.end method')]
    command = 'return-wide v0' if result == 'long' else 'return p0'
    assert body.count(command) == (1 if result == 'long' else 2)
    body = body.replace(command, 'goto :station_boot_return')
    prefix = ['    const-class v4, ' + TYPE, '', '    monitor-enter v4', '',
              '    :station_boot_lock_start']
    tail = ['    :station_boot_lock_end', '    .catchall {:station_boot_lock_start .. :station_boot_lock_end} :station_boot_lock_catch',
            '', '    :station_boot_return', '    monitor-exit v4', '', '    ' + command, '',
            '    :station_boot_lock_catch', '    move-exception v5', '', '    monitor-exit v4', '',
            '    throw v5', '.end method']
    return signature + nl + rest[:start] + nl.join(prefix) + nl + body + nl.join(tail)


def release_changed(original):
    nl = '\r\n' if '\r\n' in original else '\n'
    read = '    iget-wide v0, p0, ' + TYPE + '->bootSessionDataPointer:J'
    clear = '    iput-wide v2, p0, ' + TYPE + '->bootSessionDataPointer:J'
    assert original.count(read) == original.count(clear) == 1
    claim = '    invoke-virtual {p0}, ' + TYPE + '->consumeBootSessionData()J' + nl + nl + '    move-result-wide v0'
    return original.replace(read, claim, 1).replace(clear, '', 1)


def boot_changed(original):
    nl = '\r\n' if '\r\n' in original else '\n'
    write = '    iput-wide p2, p0, ' + TYPE + '->bootSessionDataPointer:J'
    assert original.count(write) == original.count('    .locals 1') == 1
    lines = [
        '    const-class v1, ' + TYPE,
        '', '    const-wide/16 v2, 0x0', '', '    const/4 v4, 0x0', '',
        '    monitor-enter v1', '', '    :station_boot_offer_start',
        '    iget-boolean v0, p0, ' + TYPE + '->isClosed:Z', '',
        '    iget-wide v5, p0, ' + TYPE + '->bootSessionDataPointer:J', '',
        '    if-nez v0, :station_boot_offer_closed', '',
        '    cmp-long v0, v5, p2', '', '    if-eqz v0, :station_boot_offer_same', '',
        '    move-wide v2, v5', '', '    :station_boot_offer_same', write, '',
        '    const/4 v4, 0x1', '', '    goto :station_boot_offer_end', '',
        '    :station_boot_offer_closed', '    cmp-long v0, v5, p2', '',
        '    if-eqz v0, :station_boot_offer_end', '', '    move-wide v2, p2', '',
        '    :station_boot_offer_end',
        '    .catchall {:station_boot_offer_start .. :station_boot_offer_end} :station_boot_offer_catch',
        '    monitor-exit v1', '', '    const-wide/16 v5, 0x0', '',
        '    cmp-long v0, v2, v5', '', '    if-eqz v0, :station_boot_offer_released', '',
        '    invoke-direct {p0, v2, v3}, ' + TYPE + '->nativeReleaseBootSessionData(J)V', '',
        '    :station_boot_offer_released', '    if-nez v4, :station_boot_offer_dispatch', '',
        '    return-void', '', '    :station_boot_offer_catch', '    move-exception v7', '',
        '    monitor-exit v1', '', '    throw v7', '', '    :station_boot_offer_dispatch'
    ]
    return original.replace('    .locals 1', '    .locals 8', 1).replace(write, nl.join(lines), 1)


def methods(text):
    signatures = re.findall(r'^\.method [^\r\n]+', text, re.M)
    assert len(set(signatures)) == len(signatures)
    return {signature: a.sha(a.method(text, signature).encode()) for signature in signatures}


def main():
    proof = json.loads((ROOT / 'evidence/baseline-race-proof.json').read_text(encoding='utf-8'))
    assert all(proof['results'].values())
    raw = a.DONOR.read_bytes()
    assert a.sha(raw) == a.DONOR_SHA
    text = raw.decode('utf-8')
    before = {signature: a.method(text, signature) for signature in SIGNATURES}
    proposed_methods = {a.CONSUME: wrapped(before[a.CONSUME], 'long'),
                        a.RELEASE: release_changed(before[a.RELEASE]),
                        GETTER: wrapped(before[GETTER], 'boolean'),
                        BOOT: boot_changed(before[BOOT])}
    proposed = text
    for signature in SIGNATURES:
        assert proposed.count(before[signature]) == 1
        proposed = proposed.replace(before[signature], proposed_methods[signature], 1)
    inverse = proposed
    for signature in reversed(SIGNATURES):
        assert inverse.count(proposed_methods[signature]) == 1
        inverse = inverse.replace(proposed_methods[signature], before[signature], 1)
    assert inverse.encode() == raw
    old_methods, new_methods = methods(text), methods(proposed)
    assert old_methods.keys() == new_methods.keys()
    assert {signature for signature in old_methods if old_methods[signature] != new_methods[signature]} == set(SIGNATURES)
    assert text[:text.index('# direct methods')] == proposed[:proposed.index('# direct methods')]
    old_tail = before[BOOT][before[BOOT].index('    invoke-static {p0, p1}, Lorg/emulationstation/frontend/netplay/StationDolphinSession;->onBootGame'):]
    assert proposed_methods[BOOT].endswith(old_tail)
    write_pattern = re.compile(r'^\s*(?:i|s)put-wide [^\r\n]*->bootSessionDataPointer:J', re.M)
    reads = re.compile(r'^\s*iget-wide [^\r\n]*->bootSessionDataPointer:J', re.M)
    for signature, body in proposed_methods.items():
        if signature == a.RELEASE:
            assert not write_pattern.search(body) and not reads.search(body)
        else:
            assert 'monitor-enter' in body and 'monitor-exit' in body
    destination = ROOT / 'smali/org/dolphinemu/dolphinemu/features/netplay/NetplaySession.smali'
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as stream:
        stream.write(proposed.encode())
    for signature, body in proposed_methods.items():
        name = signature.split(' ')[-1].split('(')[0]
        with (ROOT / 'evidence' / (name + '.proposed.smali.txt')).open('x', encoding='utf-8', newline='') as stream:
            stream.write(body)
    scope = {'schema': 'station.r147.dolphin.boot-ownership.scope.v1', 'partition': 'classes10.dex',
             'baselineDexSha256': a.DEX_SHA, 'classType': TYPE, 'baselineClassSha256': a.DONOR_SHA,
             'proposedClassSha256': a.sha(proposed.encode()), 'modifiedMethods': SIGNATURES,
             'baselineAllMethodSha256': old_methods, 'proposedAllMethodSha256': new_methods,
             'wholeClassSourceInversePassed': True, 'unrelatedMethodsAndFieldsPreserved': True,
             'newMethods': [], 'newFields': [], 'newClasses': [],
             'classLockHeldOnlyDuringFieldReadClaimOrOffer': True,
             'noNativeCallsOrStationCallbacksInsideOwnershipLock': True,
             'nativeReleasesOutsideOwnershipLock': True,
             'existingCloseBlockingThisMonitorPreserved': True,
             'incomingPolicy': ['After isClosed, incoming nonzero pointer is released outside lock and no launch hook is dispatched.',
                                'Accepted new pointer replaces only still-pending ownership; replaced nonzero pointer is released outside lock.',
                                'Same pointer still pending is not freed; original dispatch behavior remains.',
                                'Zero pointer is never sent to nativeRelease; null consume remains legal and native null-boot cleanup belongs to separate proven fix.',
                                'Producer must transfer each unique_ptr exactly once; stale redelivery after ownership transfer cannot be identified without a separate generation/lease and is not claimed fixed.'],
             'cpuJitControllerProfileRoomInputOrReadinessChanges': False,
             'sourceOnly': True, 'dexCompiled': False, 'apkCompiled': False, 'nativeCoreCompiled': False,
             'androidExecuted': False, 'phoneAccessed': False, 'serverAccessed': False}
    with (ROOT / 'evidence/ownership-scope.json').open('x', encoding='utf-8') as stream:
        json.dump(scope, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'privateOverlayPrepared': True, 'changedMethods': 4, 'newMethods': 0,
                      'newFields': 0, 'wholeClassInversePassed': True,
                      'proposedClassSha256': scope['proposedClassSha256'], 'dexCompiled': False}))


if __name__ == '__main__':
    main()
