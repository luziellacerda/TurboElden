"""Meaningful no-network TLS route tests and exact donor projection guards."""
from pathlib import Path
import argparse
import ast
import importlib.util
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('route_scope', ROOT / 'recipe/route_scope.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
NETPLAY = Path('org/emulationstation/frontend/netplay')
TOOLS = {'java': '1977f302375adbb920d41dac65c7e22eb9c2ed8e1e8d6258964154ff16f14406',
         'javac': '9c71eee841aeebb723bfc2cceca7d72c6c1988fb679402f4123aa4d0e86aa549'}


def run(command):
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=90)
    r.need(result.returncode == 0, 'Host probe failed: ' + result.stderr[-2200:])
    return result.stdout.strip(), result.stderr.strip()


def rejected(action, label):
    try:
        action()
    except ValueError:
        return label
    raise AssertionError('Negative guard accepted: ' + label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jdk-bin', type=Path, required=True)
    parser.add_argument('--donor-smali', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    r.need(not args.out.exists() and ROOT not in args.out.resolve().parents, 'Fresh host-test output outside preparation required')
    plan = r.reviewed_plan()
    r.need(r.class_maps(args.donor_smali) == plan['baselineClassSha256'], 'Exact actual R145 donor class map required')
    for name in ('java', 'javac'):
        r.need(r.sha(args.jdk_bin / (name + '.exe')) == TOOLS[name], 'Pinned host JDK required')
    for path in (ROOT / 'recipe').glob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    args.out.mkdir(parents=True)
    classes = args.out / 'classes'
    classes.mkdir()
    compile_output, compile_diagnostics = run([
        args.jdk_bin / 'javac.exe', '-encoding', 'UTF-8', '-d', classes,
        ROOT / 'java' / NETPLAY / 'StationRelayTls.java',
        ROOT / 'tests/fixtures/org/emulationstation/frontend/station/StationConfig.java',
        ROOT / 'tests/StationRelayTlsRouteProbe.java'])
    host_output, diagnostics = run([args.jdk_bin / 'java.exe', '-cp', classes,
                                    'org.emulationstation.frontend.netplay.StationRelayTlsRouteProbe'])
    host = json.loads(host_output)
    r.need(host['passed'] is True and host['checks'] >= 18 and host['networkAccessed'] is False,
           'Actual TLS source host checks required')
    baseline_java = (ROOT / 'evidence/baseline-java/StationRelayTls.java.txt').read_bytes().decode('utf-8')
    proposed_java = (ROOT / 'java' / NETPLAY / 'StationRelayTls.java').read_bytes().decode('utf-8')
    start = baseline_java.index(' static SSLSocketFactory create()throws Exception {')
    end = baseline_java.index(' static SSLSocketFactory pinned(', start)
    new_factory = baseline_java[start:end].replace('create()throws', 'createMultiplayer()throws', 1).replace(
        'String hex=StationConfig.TLS_SPKI_SHA256;', 'String hex="' + r.DIRECT_PIN + '";', 1)
    old_endpoint = '  URI base=endpoint();return new URI("wss",null,base.getHost(),base.getPort(),"/v1/station/online/multiplayer/relay",null,null);'
    new_endpoint = '  return new URI("' + r.DIRECT_URI + '");'
    r.need(proposed_java.count(new_factory) == 1 and proposed_java.count(new_endpoint) == 1 and
           proposed_java.replace(new_factory, '', 1).replace(new_endpoint, old_endpoint, 1) == baseline_java,
           'Entire readable TLS source inverse must recover unchanged legacy create/endpoint/pinned')
    baseline_session = (ROOT / 'evidence/baseline-java/StationMultiplayerSession.java.txt').read_bytes()
    session = (ROOT / 'java' / NETPLAY / 'StationMultiplayerSession.java').read_bytes()
    r.need(session.count(b'StationRelayTls.createMultiplayer()') == 1 and session.replace(
        b'StationRelayTls.createMultiplayer()', b'StationRelayTls.create()', 1) == baseline_session,
        'Entire readable Session source inverse must recover original READY/ACK/tickets/exit')
    projection = args.out / 'projection'
    shutil.copytree(args.donor_smali, projection)
    for kind in r.CHANGED:
        r.class_path(projection, kind).write_bytes(r.class_path(ROOT / 'evidence/proposed-smali', kind).read_bytes())
    actual, inverse, methods = r.verify_projection(projection, plan)
    r.need(len(actual) == 608 and all(inverse[k] == plan['baselineClassSha256'][k] for k in r.CHANGED),
           'Two complete changed classes and 606 preserved classes must pass source projection')
    negative = []
    tls = r.class_path(projection, r.TLS)
    tls_bytes = tls.read_bytes()
    tls.write_bytes(tls_bytes.replace(r.DIRECT_PIN.encode(), r.LEGACY_PIN.encode(), 1))
    negative.append(rejected(lambda: r.verify_projection(projection, plan), 'Wrong API pin in direct factory rejected'))
    tls.write_bytes(tls_bytes.replace(b'downloads-station.lzgames.com.br', b'app.lzgames.com.br', 1))
    negative.append(rejected(lambda: r.verify_projection(projection, plan), 'Unexpected direct host rejected'))
    tls.write_bytes(tls_bytes)
    channel = r.class_path(projection, r.CHANNEL)
    channel_bytes = channel.read_bytes()
    channel.write_bytes(channel_bytes.replace(r.NEW_CALL.encode(), r.OLD_CALL.encode(), 1))
    negative.append(rejected(lambda: r.verify_projection(projection, plan), 'V3 Channel using legacy factory rejected'))
    channel.write_bytes(channel_bytes)
    remote_kind = r.NETPLAY + 'StationMultiplayerTunnel$Remote;'
    remote = r.class_path(projection, remote_kind)
    remote_bytes = remote.read_bytes()
    hostname = r.body(remote_bytes, '.method protected onSetSSLParameters(Ljavax/net/ssl/SSLParameters;)V')
    r.need(b'"HTTPS"' in hostname and b'->setEndpointIdentificationAlgorithm(Ljava/lang/String;)V' in hostname and
           r.digest(remote_bytes) == plan['criticalPreservedClassSha256'][remote_kind],
           'Actual WebSocket Remote preserves HTTPS hostname identification')
    remote.write_bytes(remote_bytes.replace(b'"HTTPS"', b'""', 1))
    negative.append(rejected(lambda: r.verify_projection(projection, plan), 'Disabling actual WebSocket hostname validation rejected'))
    remote.write_bytes(remote_bytes)
    owner_kind = r.NETPLAY + 'StationMultiplayerSession;'
    owner = r.class_path(projection, owner_kind)
    owner_bytes = owner.read_bytes()
    r.need(b'"station-stream.v3"' in owner_bytes and b'"TICKET_BINDING"' in owner_bytes, 'Exact ticket policy exists')
    owner.write_bytes(owner_bytes.replace(b'"station-stream.v3"', b'"station-stream.v2"', 1))
    negative.append(rejected(lambda: r.verify_projection(projection, plan), 'Altering protocol/ticket/readiness owner rejected'))
    owner.write_bytes(owner_bytes)
    r.verify_projection(projection, plan)
    record = {'schema': 'station.r146.direct-v3-route.host-tests.v1', 'passed': True,
              'scopeDeclarationSha256': r.sha(ROOT / 'evidence/route-scope.json'),
              'baselineDexSha256': r.BASE_DEX, 'hostProbe': host,
              'javaWholeSourceInversePassed': True, 'sourceWholeClassInversePassed': True,
              'originalClasses': 608, 'modifiedClasses': 2, 'unrelatedClassesPreserved': 606,
              'actualWebSocketHttpsHostnameIdentificationPreserved': True,
              'negativeGuards': negative, 'javaTlsSourceSha256': r.sha(ROOT / 'java' / NETPLAY / 'StationRelayTls.java'),
              'hostProbeSourceSha256': r.sha(ROOT / 'tests/StationRelayTlsRouteProbe.java'),
              'tools': TOOLS, 'hostCompileDiagnostics': compile_diagnostics,
              'networkAccessed': False, 'phoneAccessed': False, 'apkCompiled': False,
              'compiledDexPostassemblyProofPending': True, 'physicalGameplayValidated': False,
              'limits': ['TLS probe uses inert JSSE boundaries and synthetic SPKI certificates; no live endpoint handshake.',
                         'Hostname protection checked in the unchanged actual WebSocket class and rejected when removed.',
                         'Production DEX build is deferred until distinct source scope freeze; it must decode actual output and repeat full inverse.']}
    with (args.out / 'host-test-receipt.json').open('x', encoding='utf-8') as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'passed': True, 'tlsChecks': host['checks'], 'negativeGuards': len(negative),
                      'actualHostnameCheckPreserved': True, 'apkCompiled': False,
                      'receipt': str(args.out / 'host-test-receipt.json')}))


if __name__ == '__main__':
    main()
