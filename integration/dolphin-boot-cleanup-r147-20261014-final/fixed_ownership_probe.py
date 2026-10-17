"""Run exact proposed ownership instructions and preserved close instructions.

Only JNI, Station callbacks and cancellation are fixture boundaries. Ownership
read/write/branch/monitor instructions are extracted from the actual smali.
"""
from pathlib import Path
import hashlib
import json
import re
import threading
import audit_ownership as a
import prepare_ownership as p

ROOT = Path(__file__).resolve().parent
CLASS_MONITOR = threading.RLock()
CLOSE = '.method public final declared-synchronized closeBlocking()V'
FINALIZE = '.method public final finalize()V'
TYPE = p.TYPE


class Environment:
    def __init__(self):
        self.frees, self.hooks = {}, []
        self.ledger_lock = threading.Lock()
        self.allow_close = True
        self.client_callback = None
        self.deferred = None
        self.callback_blocked = None
        self.closed_callbacks = 0

    def outside(self):
        assert not CLASS_MONITOR._is_owned(), 'No JNI or Station callback under ownership monitor'

    def release(self, kind, pointer):
        self.outside()
        assert pointer != 0, 'Never release a null pointer'
        with self.ledger_lock:
            key = (kind, pointer)
            self.frees[key] = self.frees.get(key, 0) + 1
        if kind == 'Client' and self.client_callback is not None:
            self.deferred = threading.Thread(target=self.client_callback, name='native-client-callback-fixture')
            self.deferred.start()
            self.deferred.join(0.25)
            self.callback_blocked = self.deferred.is_alive()

    def boot_hook(self, path):
        self.outside()
        self.hooks.append(path)
        return True  # Existing productive Station owner consumes its callback.


class Session:
    def __init__(self, environment, pointer=0):
        self.environment = environment
        self.instance_monitor = threading.RLock()
        self.fields = {'bootSessionDataPointer': pointer, 'isClosed': False,
                       'netPlayClientPointer': 0, 'netPlayServerPointer': 0,
                       'netPlayUICallbacksPointer': 0, 'sessionScope': object(), 'onClosed': object()}


class VM:
    def __init__(self, proposed, baseline):
        self.programs = {signature: a.method(proposed, signature) for signature in p.SIGNATURES}
        self.programs.update({signature: a.method(baseline, signature) for signature in [CLOSE, FINALIZE]})
        self.before_monitor = None
        self.after_boot_read = None

    def execute(self, signature, session, path='fixture.iso', pointer=0):
        rows, labels = a.instructions(self.programs[signature])
        registers = {'p0': session, 'p1': path, 'p2': pointer}
        result, pc, steps = None, 0, 0
        while pc < len(rows):
            row = rows[pc]
            pc += 1
            steps += 1
            assert steps <= 512, 'Bounded exact method execution'
            if row.startswith(('iget-wide ', 'iget-boolean ', 'iget-object ')):
                match = re.fullmatch(r'iget-(wide|boolean|object) ([vp]\d+), p0, L[^;]+;->([A-Za-z]+):[^ ]+', row)
                assert match, row
                _, reg, field = match.groups()
                registers[reg] = session.fields[field]
                if self.after_boot_read is not None and field == 'bootSessionDataPointer':
                    self.after_boot_read(signature, registers[reg])
            elif row.startswith(('iput-wide ', 'iput-boolean ')):
                match = re.fullmatch(r'iput-(wide|boolean) ([vp]\d+), p0, L[^;]+;->([A-Za-z]+):[^ ]+', row)
                assert match, row
                _, reg, field = match.groups()
                session.fields[field] = registers[reg]
            elif row.startswith(('const-wide/16 ', 'const/4 ')):
                reg, value = row.split(' ', 1)[1].split(', ')
                registers[reg] = int(value, 16)
            elif row.startswith('const-class '):
                reg, kind = row[len('const-class '):].split(', ')
                assert kind == TYPE
                registers[reg] = CLASS_MONITOR
            elif row.startswith('move-wide '):
                dest, source = row[len('move-wide '):].split(', ')
                registers[dest] = registers[source]
            elif row.startswith('cmp-long '):
                dest, left, right = row[len('cmp-long '):].split(', ')
                registers[dest] = (registers[left] > registers[right]) - (registers[left] < registers[right])
            elif row.startswith(('if-eqz ', 'if-nez ')):
                command, args = row.split(' ', 1)
                reg, label = args.split(', ')
                if (registers[reg] == 0) == (command == 'if-eqz'):
                    pc = labels[label]
            elif row.startswith('goto '):
                pc = labels[row[len('goto '):]]
            elif row.startswith(('monitor-enter ', 'monitor-exit ')):
                command, reg = row.split(' ')
                lock = session.instance_monitor if reg == 'p0' else registers[reg]
                if command == 'monitor-enter':
                    if self.before_monitor is not None:
                        self.before_monitor(signature)
                    assert lock.acquire(timeout=2), 'Bounded monitor acquisition'
                else:
                    lock.release()
            elif row.startswith('invoke-static {p0}, ') and row.endswith('StationDolphinSession;->allowClose(Ljava/lang/Object;)Z'):
                session.environment.outside()
                result = session.environment.allow_close
            elif row.startswith('invoke-static {p0, p1}, ') and row.endswith('StationDolphinSession;->onBootGame(Ljava/lang/Object;Ljava/lang/String;)Z'):
                result = session.environment.boot_hook(path)
            elif row.startswith('invoke-static {v0, v1}, ') and 'JobKt;->cancel(' in row:
                session.environment.outside()
            elif row.startswith(('move-result ', 'move-result-wide ')):
                registers[row.split(' ', 1)[1]] = result
            elif row == 'invoke-virtual {p1}, Ljava/lang/Object;->getClass()Ljava/lang/Class;':
                assert path is not None, 'Original path null check preserved'
                result = str
            elif row.startswith('invoke-virtual {p0}, ') and row.endswith('->consumeBootSessionData()J'):
                result = self.execute(a.CONSUME, session)
            elif row.startswith('invoke-virtual {p0}, ') and row.endswith('->releaseNativeResources()V'):
                result = self.execute(a.RELEASE, session)
            elif row.startswith('invoke-virtual {v0, p0}, ') and '->invoke(Ljava/lang/Object;)' in row:
                session.environment.outside()
                session.environment.closed_callbacks += 1
            elif row.startswith('invoke-direct '):
                match = re.fullmatch(r'invoke-direct \{p0, ([vp]\d+), ([vp]\d+)\}, L[^;]+;->nativeRelease([A-Za-z]+)\(J\)V', row)
                assert match, row
                first, _, kind = match.groups()
                session.environment.release(kind, registers[first])
            elif row.startswith(('return-wide ', 'return ')):
                return registers[row.split(' ', 1)[1]]
            elif row == 'return-void':
                return None
            else:
                raise AssertionError('Unknown reached instruction, refused: ' + row)
        raise AssertionError('No exact return')


def join(thread):
    thread.join(2)
    assert not thread.is_alive(), 'Bounded worker completion'


def main():
    baseline = (ROOT / 'evidence/baseline-NetplaySession.smali.txt').read_bytes().decode('utf-8')
    proposed_path = ROOT / 'smali/org/dolphinemu/dolphinemu/features/netplay/NetplaySession.smali'
    proposed = proposed_path.read_bytes().decode('utf-8')
    scope = json.loads((ROOT / 'evidence/ownership-scope.json').read_text(encoding='utf-8'))
    assert a.sha(proposed.encode()) == scope['proposedClassSha256']
    assert '.field public volatile isClosed:Z' in baseline
    vm = VM(proposed, baseline)
    results = {}
    env, session = Environment(), None
    session = Session(env)
    vm.execute(p.BOOT, session, pointer=0x1010)
    assert vm.execute(p.GETTER, session) == 1
    assert vm.execute(a.CONSUME, session) == 0x1010
    assert vm.execute(a.CONSUME, session) == 0
    vm.execute(a.RELEASE, session)
    assert not env.frees and env.hooks == ['fixture.iso']
    results['successfulHandoffExactlyOnceAndOriginalDispatchPreserved'] = True
    env, session = Environment(), None
    session = Session(env, 0x1010)
    vm.execute(CLOSE, session)
    assert session.fields['isClosed'] and vm.execute(a.CONSUME, session) == 0
    vm.execute(CLOSE, session); vm.execute(a.RELEASE, session); vm.execute(FINALIZE, session)
    assert env.frees == {('BootSessionData', 0x1010): 1} and env.closed_callbacks == 1
    results['cancelRepeatedCloseReleaseFinalizeDisposeExactlyOnce'] = True
    env, session = Environment(), None
    session = Session(env, 0x1010)
    read, proceed, release_attempted = threading.Event(), threading.Event(), threading.Event()
    returned, errors = [], []
    def read_hook(signature, value):
        if signature == a.CONSUME and threading.current_thread().name == 'consumer':
            assert value == 0x1010
            read.set(); assert proceed.wait(2)
    def entering(signature):
        if threading.current_thread().name == 'release':
            release_attempted.set()
    vm.after_boot_read, vm.before_monitor = read_hook, entering
    def task(signature, output=None):
        try:
            value = vm.execute(signature, session)
            if output is not None: output.append(value)
        except BaseException as error: errors.append(type(error).__name__)
    consumer = threading.Thread(target=lambda: task(a.CONSUME, returned), name='consumer')
    releaser = threading.Thread(target=lambda: task(a.RELEASE), name='release')
    consumer.start(); assert read.wait(2); releaser.start(); assert release_attempted.wait(2)
    assert not env.frees
    proceed.set(); join(consumer); join(releaser)
    assert not errors and returned == [0x1010] and not env.frees
    results['consumeVersusCancelHasOneOwnerNoPrematureDelete'] = True
    vm.after_boot_read = vm.before_monitor = None
    env, session = Environment(), None
    session = Session(env, 0x1010)
    barrier = threading.Barrier(2)
    claims = []
    def take():
        barrier.wait(2); claims.append(vm.execute(a.CONSUME, session))
    threads = [threading.Thread(target=take) for _ in range(2)]
    for thread in threads: thread.start()
    for thread in threads: join(thread)
    assert sorted(claims) == [0, 0x1010]
    results['twoConcurrentConsumersOnlyOneNonzeroHandoff'] = True
    env, session = Environment(), None
    session = Session(env)
    vm.execute(CLOSE, session); vm.execute(p.BOOT, session, pointer=0x2020)
    vm.execute(a.RELEASE, session)
    assert env.frees == {('BootSessionData', 0x2020): 1} and not env.hooks and vm.execute(a.CONSUME, session) == 0
    results['lateDeliveryAfterVolatileClosedDisposedWithoutDispatch'] = True
    env, session = Environment(), None
    session = Session(env)
    vm.execute(p.BOOT, session, pointer=0x1010); vm.execute(p.BOOT, session, pointer=0x2020)
    vm.execute(p.BOOT, session, pointer=0x2020)
    assert env.frees == {('BootSessionData', 0x1010): 1} and vm.execute(a.CONSUME, session) == 0x2020
    vm.execute(a.RELEASE, session)
    assert env.hooks == ['fixture.iso'] * 3 and ('BootSessionData', 0x2020) not in env.frees
    results['replacementPendingDisposedOnceSamePendingNotDeletedDispatchPreserved'] = True
    env, session = Environment(), None
    session = Session(env, 0x1010)
    vm.execute(p.BOOT, session, pointer=0)
    assert env.frees == {('BootSessionData', 0x1010): 1} and vm.execute(a.CONSUME, session) == 0
    results['zeroOfferNeverDeletedOriginalNullDispatchPreserved'] = True
    env, session = Environment(), None
    session = Session(env, 0x1010)
    session.fields['netPlayClientPointer'] = 0x3030
    env.client_callback = lambda: vm.execute(p.BOOT, session, pointer=0x2020)
    vm.execute(CLOSE, session)
    assert env.deferred is not None; join(env.deferred)
    assert not env.callback_blocked and env.frees == {('BootSessionData', 0x1010): 1,
                                                     ('Client', 0x3030): 1, ('BootSessionData', 0x2020): 1}
    results['nativeClientJoinCallbackCompletesWhileCloseHoldsThis'] = True
    # Negative regression: placing the same JNI callback behind the instance
    # monitor blocks it while the unchanged close holds this and joins client.
    env, session = Environment(), None
    session = Session(env)
    session.fields['netPlayClientPointer'] = 0x3030
    def wrong_this_callback():
        with session.instance_monitor:
            vm.execute(p.BOOT, session, pointer=0x2020)
    env.client_callback = wrong_this_callback
    vm.execute(CLOSE, session)
    assert env.callback_blocked; join(env.deferred)
    results['negativeThisMonitorWouldBlockNativeJoinCallback'] = True
    # Human authority hook continues to run before release/close; no bypass.
    env, session = Environment(), None
    session = Session(env, 0x1010); env.allow_close = False
    vm.execute(a.RELEASE, session); vm.execute(CLOSE, session)
    assert not session.fields['isClosed'] and session.fields['bootSessionDataPointer'] == 0x1010 and not env.frees
    results['existingHumanCloseAuthorityGuardPreserved'] = True
    results['allNativeReleasesAndStationCallbacksOutsideOwnershipMonitor'] = True
    record = {'schema': 'station.r147.dolphin.boot-ownership.patched-instruction-probe.v1',
              'passed': all(results.values()), 'results': results,
              'actualBaselineClassSha256': a.DONOR_SHA, 'proposedClassSha256': scope['proposedClassSha256'],
              'sourceScopeSha256': a.sha((ROOT / 'evidence/ownership-scope.json').read_bytes()),
              'probeSourceSha256': a.sha(Path(__file__).read_bytes()), 'exactSourceInstructionsExtracted': True,
              'unknownReachedOpcodesRefused': True, 'wholeClassSourceInversePassed': True,
              'isClosedFieldVolatileVerified': True, 'instanceCloseMonitorUnchanged': True,
              'newCoupling': 'Short NetplaySession.class ownership monitor serializes only boot-pointer field operations across NetplaySession instances; no JNI/callback/join under it.',
              'boundaries': ['Native releases counted in a ledger.', 'Station onBootGame hook accepts the existing owner.',
                             'NativeReleaseClient models the verified destructor joining a callback thread.',
                             'No actual ART/JNI/native core/gameplay executed; exception catchall paths statically preserved but not fault-injected.'],
              'apkCompiled': False, 'nativeCoreCompiled': False, 'phoneAccessed': False, 'serverAccessed': False}
    with (ROOT / 'evidence/patched-ownership-proof.json').open('x', encoding='utf-8') as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps({'passed': True, 'checks': len(results), 'exactProposedInstructionsExecuted': True,
                      'jniOrCallbackInsideOwnershipLock': False, 'compiledProductiveCode': False}))


if __name__ == '__main__':
    main()
