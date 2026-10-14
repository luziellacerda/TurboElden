"""Exact R145 donor -> R146 direct v3 route; no APK/phone/network operations."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BASE_APK = '275f31b34145eb77c457b1a9c09bbff4034cc28a990b74121b0b1fd4573c5df0'
BASE_BYTES = 2715057167
BASE_SOURCE = '25d10b2322d2e5687c9dfacc71a826c3955fad5d'
BASE_DEX = '5f36d5d9b2786a2877616bedffa227f83503621ec4e7eeb24b73a19264e4f089'
PARTITION = 'classes35.dex'
CLASS_COUNT = 608
SCOPE_NAME = 'direct-v3-relay-r146-20261014'
BUILD_NAMESPACE = Path('E:/StationDirectV3RelayR146-20261014')
NETPLAY = 'Lorg/emulationstation/frontend/netplay/'
TLS = NETPLAY + 'StationRelayTls;'
CHANNEL = NETPLAY + 'StationMultiplayerSession$Channel;'
CHANGED = {TLS, CHANNEL}
ENDPOINT = '.method static multiplayerEndpoint()Ljava/net/URI;'
LEGACY_ENDPOINT = '.method static endpoint()Ljava/net/URI;'
CREATE = '.method static create()Ljavax/net/ssl/SSLSocketFactory;'
NEW_CREATE = '.method static createMultiplayer()Ljavax/net/ssl/SSLSocketFactory;'
CHANNEL_CTOR = '.method constructor <init>(Lorg/emulationstation/frontend/netplay/StationMultiplayerSession;Lorg/json/JSONObject;I)V'
LEGACY_PIN = '13f9dcbb7a9687c2f88ff73de5621cfab849d0ec02191dcdd1ee8a6275dacba7'
DIRECT_PIN = 'bcd134d59fcdbb35e0343c86d31a666cc95cf158d70b27aceceefd19158d072f'
DIRECT_URI = 'wss://downloads-station.lzgames.com.br/v1/station/online/multiplayer/relay'
OLD_CALL = 'Lorg/emulationstation/frontend/netplay/StationRelayTls;->create()Ljavax/net/ssl/SSLSocketFactory;'
NEW_CALL = 'Lorg/emulationstation/frontend/netplay/StationRelayTls;->createMultiplayer()Ljavax/net/ssl/SSLSocketFactory;'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def class_path(directory, kind):
    return Path(directory) / (kind[1:-1] + '.smali')


def class_maps(directory):
    result = {}
    root = Path(directory)
    for path in sorted(root.rglob('*.smali')):
        need(not path.is_symlink(), 'Symbolic smali refused')
        kind = 'L' + path.relative_to(root).as_posix()[:-6] + ';'
        need(kind not in result, 'Duplicate class')
        result[kind] = digest(path.read_bytes())
    return result


def span(text, signature):
    newline = '\r\n' if '\r\n' in text else '\n'
    needle = signature + newline
    need(text.count(needle) == 1, 'Unique exact method required: ' + signature)
    start = text.index(needle)
    end = text.index('.end method', start) + len('.end method')
    return start, end


def body(raw, signature):
    text = raw.decode('utf-8')
    start, end = span(text, signature)
    return text[start:end].encode('utf-8')


def method_hashes(raw):
    text = raw.decode('utf-8')
    signatures = re.findall(r'^\.method [^\r\n]+', text, re.M)
    need(len(signatures) == len(set(signatures)), 'Duplicate method descriptor')
    return {signature: digest(body(raw, signature)) for signature in signatures}


def new_endpoint(newline):
    # Fixed reviewed URI, no userinfo/query/fragment. No runtime preference or
    # fallback to a host using the wrong trust pin is introduced.
    lines = [ENDPOINT, '    .locals 2',
             '    .annotation system Ldalvik/annotation/Throws;',
             '        value = {', '            Ljava/lang/Exception;',
             '        }', '    .end annotation', '',
             '    .line 15', '    new-instance v0, Ljava/net/URI;', '',
             '    const-string v1, "' + DIRECT_URI + '"', '',
             '    invoke-direct {v0, v1}, Ljava/net/URI;-><init>(Ljava/lang/String;)V', '',
             '    return-object v0', '.end method']
    return newline.join(lines)


def proposed_class(kind, baseline):
    text = baseline.decode('utf-8')
    newline = '\r\n' if '\r\n' in text else '\n'
    if kind == TLS:
        need(NEW_CREATE not in text, 'New factory already exists')
        start, end = span(text, ENDPOINT)
        text = text[:start] + new_endpoint(newline) + text[end:]
        original_factory = body(baseline, CREATE).decode('utf-8')
        need(original_factory.count(LEGACY_PIN) == 1 and DIRECT_PIN not in original_factory,
             'Exact legacy pin in the unchanged create() required')
        factory = original_factory.replace(CREATE, NEW_CREATE, 1).replace(LEGACY_PIN, DIRECT_PIN, 1)
        # DEX direct methods decode in name/prototype order. Insert the new
        # createMultiplayer before endpoint, retaining all original gaps.
        start, _ = span(text, LEGACY_ENDPOINT)
        text = text[:start] + factory + newline + newline + text[start:]
    elif kind == CHANNEL:
        start, end = span(text, CHANNEL_CTOR)
        ctor = text[start:end]
        need(ctor.count(OLD_CALL) == 1 and NEW_CALL not in text,
             'Exactly one legacy factory call in Channel constructor required')
        text = text[:start] + ctor.replace(OLD_CALL, NEW_CALL, 1) + text[end:]
    else:
        raise ValueError('Unreviewed class')
    result = text.encode('utf-8')
    need(inverse_class(kind, result, baseline) == baseline, 'Whole class inverse failed')
    return result


def inverse_class(kind, proposed, baseline):
    text = proposed.decode('utf-8')
    original = baseline.decode('utf-8')
    newline = '\r\n' if '\r\n' in text else '\n'
    if kind == TLS:
        factory = body(proposed, NEW_CREATE).decode('utf-8')
        expected = body(baseline, CREATE).decode('utf-8').replace(CREATE, NEW_CREATE, 1).replace(LEGACY_PIN, DIRECT_PIN, 1)
        need(factory == expected, 'Dedicated factory must equal legacy factory except name/pin')
        start, end = span(text, NEW_CREATE)
        need(text[end:end + len(newline) * 2] == newline * 2, 'Unexpected added factory separator')
        text = text[:start] + text[end + len(newline) * 2:]
        start, end = span(text, ENDPOINT)
        need(text[start:end] == new_endpoint(newline), 'Direct URI method differs from reviewed body')
        left, right = span(original, ENDPOINT)
        text = text[:start] + original[left:right] + text[end:]
    elif kind == CHANNEL:
        start, end = span(text, CHANNEL_CTOR)
        ctor = text[start:end]
        need(ctor.count(NEW_CALL) == 1 and OLD_CALL not in ctor, 'Exactly one direct factory call required')
        text = text[:start] + ctor.replace(NEW_CALL, OLD_CALL, 1) + text[end:]
    else:
        raise ValueError('Unreviewed inverse class')
    return text.encode('utf-8')


def reviewed_plan():
    plan = read(ROOT / 'evidence/route-scope.json')
    need(plan['schema'] == 'station.r146.direct-v3-relay.scope.v1' and
         plan['baselineApkSha256'] == BASE_APK and plan['baselineApkBytes'] == BASE_BYTES and
         plan['baselineSourceCommit'] == BASE_SOURCE and plan['baselineDexSha256'] == BASE_DEX and
         plan['partition'] == PARTITION and plan['classCount'] == CLASS_COUNT and
         set(plan['modifiedClasses']) == CHANGED and plan['newFields'] == [] and plan['newClasses'] == [] and
         plan['newMethods'] == {TLS: [NEW_CREATE]} and plan['directUri'] == DIRECT_URI and
         plan['directSpkiSha256'] == DIRECT_PIN and plan['sourceWholeClassInversePassed'] is True,
         'Closed exact route scope required')
    need(plan['modifiedMethods'] == {TLS: [ENDPOINT], CHANNEL: [CHANNEL_CTOR]}, 'Exact route method allowlist required')
    need(len(plan['baselineClassSha256']) == CLASS_COUNT and len(plan['preservedDexSha256']) == 39,
         '608 donor class pins and 39 preserved DEX pins required')
    for kind in CHANGED:
        baseline = (ROOT / 'evidence/baseline-classes' / (kind[1:-1] + '.smali.txt')).read_bytes()
        proposed = class_path(ROOT / 'evidence/proposed-smali', kind).read_bytes()
        need(digest(baseline) == plan['baselineClassSha256'][kind] and
             digest(proposed) == plan['proposedClassSha256'][kind] and
             proposed == proposed_class(kind, baseline), 'Frozen route source differs: ' + kind)
        before, after = method_hashes(baseline), method_hashes(proposed)
        expected_new = {NEW_CREATE} if kind == TLS else set()
        need(set(after) - set(before) == expected_new and not set(before) - set(after), 'Method set changed')
        allowed = set(plan['modifiedMethods'][kind])
        need(all(after[signature] == checksum for signature, checksum in before.items() if signature not in allowed),
             'Unrelated methods changed inside modified class')
        need(before == plan['baselineMethodSha256'][kind] and after == plan['proposedMethodSha256'][kind],
             'Method pins differ')
    return plan


def verify_projection(directory, plan):
    actual = class_maps(directory)
    expected = dict(plan['baselineClassSha256'])
    expected.update(plan['proposedClassSha256'])
    need(actual == expected, 'Compiled projection changed outside the exact two reviewed classes')
    inverse, inverse_methods = {}, {}
    for kind in CHANGED:
        baseline = (ROOT / 'evidence/baseline-classes' / (kind[1:-1] + '.smali.txt')).read_bytes()
        compiled = class_path(directory, kind).read_bytes()
        recovered = inverse_class(kind, compiled, baseline)
        need(recovered == baseline, 'Postassembly whole class inverse failed')
        inverse[kind] = digest(recovered)
        inverse_methods[kind] = method_hashes(recovered)
    return actual, inverse, inverse_methods
