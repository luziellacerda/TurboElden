"""Check the actual Android CUE identity against portable server vectors."""
from pathlib import Path
import argparse, base64, hashlib, json, os, subprocess
ROOT=Path(__file__).resolve().parents[1]

def digest(data):return hashlib.sha256(data).hexdigest()
def encoded(text):return base64.urlsafe_b64encode(text.encode()).decode().rstrip('=')
def expected(files):
    lines=['TurboRamaStation/content-set/v1','launch='+encoded('Jogo.cue')]
    for name,body in sorted(files.items(),key=lambda pair:pair[0].encode('utf8')):lines.append(encoded(name)+'\t'+str(len(body))+'\t'+digest(body))
    return digest(('\n'.join(lines)+'\n').encode())

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True);parser.add_argument('--jdk',type=Path,required=True)
    args=parser.parse_args();args.work.mkdir(parents=True,exist_ok=False)
    source=ROOT/'java/netplay-src/org/emulationstation/frontend/netplay/StationContentIdentity.java'
    stub=args.work/'org/emulationstation/frontend/station/StationApi.java';stub.parent.mkdir(parents=True)
    stub.write_text('package org.emulationstation.frontend.station; public final class StationApi { public static final class Cancellation { public void check() throws java.io.IOException {} } }\n')
    fixture=args.work/'IdentityFixture.java'
    fixture.write_text('package org.emulationstation.frontend.netplay; import java.io.File; import org.emulationstation.frontend.station.StationApi; public final class IdentityFixture { public static void main(String[] args) throws Exception { System.out.println(StationContentIdentity.identity(new File(args[0]),args[1],new StationApi.Cancellation())); } }\n')
    classes=args.work/'classes';classes.mkdir();suffix='.exe' if os.name=='nt' else ''
    result=subprocess.run([str(args.jdk/('javac'+suffix)),'--release','8','-encoding','UTF-8','-d',str(classes),str(stub),str(source),str(fixture)],capture_output=True)
    (args.work/'compile.log').write_bytes(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError('Identity fixture compilation failed')
    files={'Jogo.cue':'FILE "faixas/áudio.bin" BINARY\nFILE a.bin BINARY\n'.encode(),'faixas/áudio.bin':b'synthetic audio','a.bin':b'synthetic data'}
    game=args.work/'game';game.mkdir()
    def write():
        for name,body in files.items():
            path=game/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    def run(scheme="cue-set-v1"):return subprocess.run([str(args.jdk/('java'+suffix)),'-cp',str(classes),'org.emulationstation.frontend.netplay.IdentityFixture',str(game/'Jogo.cue'),scheme],capture_output=True)
    write();checks=0
    for scheme in ('', 'wiiu-set-v1', 'unknown'):
        result=run(scheme);checks+=1
        if scheme=='':
            if result.returncode or result.stdout.decode().strip()!=digest(files['Jogo.cue']):raise RuntimeError('Legacy launch identity changed')
        elif result.returncode==0:raise RuntimeError('Unsupported identity scheme accepted')
    result=run();checks+=1
    if result.returncode or result.stdout.decode().strip()!=expected(files):raise RuntimeError('Server/Android CUE identity diverged')
    before=expected(files);files['a.bin']=b'changed synthetic track';write();result=run();checks+=1
    if result.returncode or result.stdout.decode().strip()!=expected(files) or expected(files)==before:raise RuntimeError('Track change not bound')
    for raw in (b'FILE "missing.bin" BINARY\n',b'FILE "../outside.bin" BINARY\n',b'FILE "C:\\track.bin" BINARY\n',b'REM no file\n',b'FILE '+b'x'*(512*1024),b'FILE "a.bin"\n',b'FILE "a.bin" BINARY\n\xff'):
        files['Jogo.cue']=raw;write();checks+=1
        if run().returncode==0:raise RuntimeError('Invalid CUE dependency accepted')
    files['Jogo.cue']=b'FILE a.bin BINARY\n';write()
    if os.name!='nt':
        (game/'a.bin').unlink();(game/'a.bin').symlink_to(game/'faixas/áudio.bin');checks+=1
        if run().returncode==0:raise RuntimeError('Symbolic track accepted')
    receipt=dict(passed=True,checks=checks,scope='actual Java/Python portable CUE identities; no Android gameplay',sourceSHA256=digest(source.read_bytes()),recipeSHA256=digest(Path(__file__).read_bytes()))
    (ROOT/'evidence/content-identity-tests.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))

if __name__=='__main__':main()
