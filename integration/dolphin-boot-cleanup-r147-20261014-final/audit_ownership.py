"""Execute exact donor ownership instructions under a bounded two-thread schedule.

This deliberately small Dalvik ownership interpreter rejects unknown opcodes.
Native release is an allocation ledger, not actual JNI or undefined C++ access.
No source, APK, core, phone or server mutation.
"""
from pathlib import Path
import hashlib
import json
import re
import threading
import zipfile

ROOT = Path(__file__).resolve().parent
DONOR = ROOT.parent / 'r146-audit-private/actual-r144-smali-final/org/dolphinemu/dolphinemu/features/netplay/NetplaySession.smali'
DONOR_SHA = '7dcbc2c67298d18e7ffe5b4839e73ca6967a0318e4628269598bef9a45ec2315'
DEX_SHA = '09ed47c40c4a6f5194bcb9ace23f85392b99c19c84cd654e61716de37b32e01c'
APK = Path('F:/TurboStations-Backup-Completo-20261011/desenvolvimento/TurboStations-Premium-R145-azul-ceu-faixas-20261013.apk')
CONSUME = '.method public final consumeBootSessionData()J'
RELEASE = '.method public final releaseNativeResources()V'
BOOT_FIELD = 'bootSessionDataPointer'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def method(text, signature):
    newline = '\r\n' if '\r\n' in text else '\n'
    needle = signature + newline
    assert text.count(needle) == 1
    start = text.index(needle)
    return text[start:text.index('.end method', start) + len('.end method')]


def instructions(body):
    rows, labels = [], {}
    for raw in body.splitlines()[1:-1]:
        row = raw.strip()
        if not row or row.startswith(('.', '#')):
            continue
        if row.startswith(':'):
            assert row not in labels
            labels[row] = len(rows)
        else:
            rows.append(row)
    return rows, labels


class Ledger:
    def __init__(self):
        self.frees = {}
        self.lock = threading.Lock()
        self.use_after_release = False

    def release(self, pointer):
        assert pointer != 0
        with self.lock:
            self.frees[pointer] = self.frees.get(pointer, 0) + 1

    def run_netplay_unique_owner(self, pointer):
        assert pointer != 0
        with self.lock:
            self.use_after_release = self.frees.get(pointer, 0) > 0
        # The real RunNetPlay takes unique_ptr<BootSessionData>; its destructor
        # owns the address a second time. Record, never execute actual UB.
        self.release(pointer)


class Session:
    def __init__(self, pointer, ledger):
        self.fields = {BOOT_FIELD: pointer, 'netPlayClientPointer': 0,
                       'netPlayServerPointer': 0, 'netPlayUICallbacksPointer': 0}
        self.ledger = ledger


def execute(body, session, read_hook=None):
    rows, labels = instructions(body)
    registers = {'p0': session}
    result, pc, steps = None, 0, 0
    while pc < len(rows):
        row = rows[pc]
        pc += 1
        steps += 1
        assert steps <= 256, 'Bounded exact instruction execution'
        if row.startswith('iget-wide '):
            match = re.fullmatch(r'iget-wide ([vp]\d+), p0, L[^;]+;->([A-Za-z]+):J', row)
            assert match, row
            reg, field = match.groups()
            registers[reg] = session.fields[field]
            if read_hook is not None and field == BOOT_FIELD:
                read_hook(registers[reg])
        elif row.startswith('iput-wide '):
            match = re.fullmatch(r'iput-wide ([vp]\d+), p0, L[^;]+;->([A-Za-z]+):J', row)
            assert match, row
            reg, field = match.groups()
            session.fields[field] = registers[reg]
        elif row.startswith('const-wide/16 '):
            reg, value = row[len('const-wide/16 '):].split(', ')
            registers[reg] = int(value, 16)
        elif row.startswith('cmp-long '):
            dest, left, right = row[len('cmp-long '):].split(', ')
            registers[dest] = (registers[left] > registers[right]) - (registers[left] < registers[right])
        elif row.startswith(('if-eqz ', 'if-nez ')):
            command, args = row.split(' ', 1)
            reg, label = args.split(', ')
            if (registers[reg] == 0) == (command == 'if-eqz'):
                pc = labels[label]
        elif row.startswith('invoke-static {p0}, ') and row.endswith('StationDolphinSession;->allowClose(Ljava/lang/Object;)Z'):
            # Exact productive hook preserved; test authorized human close.
            result = True
        elif row.startswith('move-result '):
            registers[row[len('move-result '):]] = result
        elif row.startswith('invoke-direct '):
            match = re.fullmatch(r'invoke-direct \{p0, ([vp]\d+), ([vp]\d+)\}, L[^;]+;->(nativeRelease[A-Za-z]+)\(J\)V', row)
            assert match, row
            first, _, native = match.groups()
            pointer = registers[first]
            assert native == 'nativeReleaseBootSessionData' or pointer == 0, 'Other resources intentionally absent'
            session.ledger.release(pointer)
        elif row.startswith('return-wide '):
            return registers[row[len('return-wide '):]]
        elif row == 'return-void':
            return None
        else:
            raise AssertionError('Unknown productive instruction, refused: ' + row)
    raise AssertionError('Missing exact return')


def main():
    raw = DONOR.read_bytes()
    assert sha(raw) == DONOR_SHA
    with zipfile.ZipFile(APK) as archive:
        assert sha(archive.read('classes10.dex')) == DEX_SHA
    text = raw.decode('utf-8')
    consume, release = method(text, CONSUME), method(text, RELEASE)
    assert 'monitor-enter' not in consume + release and 'declared-synchronized' not in consume + release
    pointer = 0x1010
    ledger, observed, proceed, failures = Ledger(), threading.Event(), threading.Event(), []
    session = Session(pointer, ledger)
    returned = []

    def hold_after_read(value):
        assert value == pointer
        observed.set()
        assert proceed.wait(2), 'Bounded consumer read barrier'

    def consumer():
        try:
            returned.append(execute(consume, session, hold_after_read))
            ledger.run_netplay_unique_owner(returned[-1])
        except BaseException as exception:
            failures.append(type(exception).__name__)

    worker = threading.Thread(target=consumer, name='NativeEmulation-source-instructions')
    worker.start()
    assert observed.wait(2), 'Consumer must read original pointer'
    execute(release, session)
    released_before_consumer = ledger.frees.get(pointer) == 1
    proceed.set()
    worker.join(2)
    assert not worker.is_alive() and not failures
    assert returned == [pointer] and ledger.use_after_release and ledger.frees[pointer] == 2
    # Baseline also permits two consumers to return the same pointer. Explicit
    # producer unique_ptr ownership does not make this Java transfer atomic.
    second_ledger = Ledger()
    second = Session(pointer, second_ledger)
    barrier = threading.Barrier(2)
    claims = []
    consumers = [threading.Thread(target=lambda: claims.append(execute(consume, second, lambda _: barrier.wait(2)))) for _ in range(2)]
    for thread in consumers:
        thread.start()
    for thread in consumers:
        thread.join(2)
        assert not thread.is_alive()
    assert claims == [pointer, pointer]
    output = ROOT / 'evidence'
    output.mkdir(exist_ok=True)
    with (output / 'baseline-NetplaySession.smali.txt').open('xb') as stream:
        stream.write(raw)
    for name, body in [('consumeBootSessionData', consume), ('releaseNativeResources', release)]:
        with (output / (name + '.extracted.smali.txt')).open('x', encoding='utf-8', newline='') as stream:
            stream.write(body)
    record = {'schema': 'station.r147.dolphin.boot-ownership.source-instruction-probe.v1',
              'actualDexSha256': DEX_SHA, 'actualClassSha256': DONOR_SHA,
              'actualWholeMethodSha256': {CONSUME: sha(consume.encode()), RELEASE: sha(release.encode())},
              'interpreterSourceSha256': sha(Path(__file__).read_bytes()),
              'unknownOpcodesRefused': True, 'productiveMethodInstructionsEdited': False,
              'authorizedHumanAllowCloseHook': True, 'exactInstructionBarriersUsed': True,
              'results': {'consumerReturnedReleasedPointer': returned == [pointer] and ledger.use_after_release,
                          'releaseCompletedBeforeConsumerHandoff': released_before_consumer,
                          'sameAddressHadTwoNativeOwners': ledger.frees[pointer] == 2,
                          'twoConsumersReturnedSameAddress': claims == [pointer, pointer]},
              'proven': 'Actual read-clear transfer and authorized release are not atomic; valid two-thread instruction interleaving returns an already-released pointer to RunNetPlay unique_ptr ownership.',
              'limits': ['Exact Dalvik ownership instruction interpreter and allocation ledger, not ART or JNI execution.',
                         'No actual undefined C++ use/free attempted.',
                         'Does not establish that a reported phone failure used this interleaving.'],
              'sourceModified': False, 'apkCompiled': False, 'coreCompiled': False,
              'phoneAccessed': False, 'serverAccessed': False}
    with (output / 'baseline-race-proof.json').open('x', encoding='utf-8') as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'raceProven': True, 'sourceExtractedInstructions': True,
                      'consumerReturnedReleasedPointer': True, 'sameAddressTwoOwners': True,
                      'twoConsumersSamePointer': True, 'actualAndroidExecuted': False}))


if __name__ == '__main__':
    main()
