"""Exercise extracted, hashed R74/R76 pump methods against deterministic scheduling fixtures."""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
BASE = Path(r'E:\ESTUDO APK\work\station-session-lifecycle-r74-20261007\compiled-final\java\netplay-src\org\emulationstation\frontend\netplay')
WORK = Path(r'E:\ESTUDO APK\work\station-pump-wakeup-r76-20261008\pump-tests')
JDK = Path(r'C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot\bin')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def extract(text, signature):
    start = text.index(signature)
    level = 0
    for i in range(text.index('{', start), len(text)):
        if text[i] == '{': level += 1
        elif text[i] == '}':
            level -= 1
            if level == 0: return text[start:i + 1]
    raise AssertionError(signature)

def once(text, old, new):
    assert text.count(old) == 1, repr(old)
    return text.replace(old, new)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, default=WORK)
    p.add_argument('--base', type=Path, default=BASE)
    a = p.parse_args()
    baseline = (a.base/'StationRecoveryTunnel.java').read_bytes()
    candidate = (HERE/'java/netplay-src/org/emulationstation/frontend/netplay/StationRecoveryTunnel.java').read_bytes()
    wire = (a.base/'StationRecoveryWire.java').read_bytes()
    assert sha(baseline) == '8af5ceb585498512ff9ff4e1409a46ee2ed9dca9ee66bcb0c43bc11fa7817896'
    assert sha(wire) == 'cb7e83ee84c1297c91c23bc24c47f7eb34204ce8ffda933f71d4b27bbc418a20'
    methods = {}; classes = []
    producer = 'synchronized(gate){tx.append(tx.next,Arrays.copyOf(bytes,count));readySent=-1;gate.notifyAll();}pump();'
    for name, raw in [('BaselinePump', baseline), ('FixedPump', candidate)]:
        text = raw.decode('utf-8'); method = extract(text, 'private void pump()')
        assert text.count(producer) == 1
        methods[name] = sha(method.encode())
        hooked = once(method, 'if(frame==null)return;', 'if(frame==null){probeEmpty();return;}')
        classes.append('final class '+name+' extends PumpBase {\n'+hooked+'\n'
          '@Override void signal(){pump();}\n'
          '@Override void produce(byte[] bytes)throws Exception {int count=bytes.length;'+producer+'}\n}\n')
    template = (HERE/'tests/StationPumpRegression.java.in').read_text(encoding='utf-8')
    generated = once(template, '@GENERATED_CLASSES@', '\n'.join(classes))
    a.work.mkdir(parents=True, exist_ok=True)
    src = a.work/'src/org/emulationstation/frontend/netplay'; src.mkdir(parents=True, exist_ok=True)
    (src/'StationPumpRegression.java').write_text(generated, encoding='utf-8', newline='\n')
    (src/'StationRecoveryWire.java').write_bytes(wire)
    classes_dir = a.work/'classes'; classes_dir.mkdir(exist_ok=True)
    cp = subprocess.run([str(JDK/'javac.exe'), '-encoding','UTF-8','-d',str(classes_dir),
      str(src/'StationRecoveryWire.java'),str(src/'StationPumpRegression.java')], capture_output=True,text=True,encoding='utf-8')
    (a.work/'compile.log').write_text(cp.stdout+cp.stderr,encoding='utf-8')
    if cp.returncode: raise RuntimeError(cp.stdout+cp.stderr)
    run = subprocess.run([str(JDK/'java.exe'),'-cp',str(classes_dir),'org.emulationstation.frontend.netplay.StationPumpRegression'],capture_output=True,text=True,encoding='utf-8',timeout=90)
    (a.work/'test.log').write_text(run.stdout+run.stderr,encoding='utf-8')
    if run.returncode: raise RuntimeError(run.stdout+run.stderr)
    metrics = json.loads(run.stdout.strip().splitlines()[-1])
    receipt = {'utc':datetime.now(timezone.utc).isoformat(),'baselineSHA256':sha(baseline),
      'candidateSHA256':sha(candidate),'wireSHA256':sha(wire),'extractedMethods':methods,
      'recipeSHA256':sha(Path(__file__).read_bytes()),'templateSHA256':sha(template.encode()),
      'generatedSHA256':sha(generated.encode()),'metrics':metrics,
      'realCode':['pump method copied directly from pinned baseline and actual candidate','nativeInput producer fragment','TSR2 codec and bounded Bytes buffer'],
      'models':['WebSocket send/queue/open state','listener/native status','transport lost/provide effects','controlled executor rejection'],
      'hooks':['one CountDownLatch after empty decision and before finally, no algorithm substitutions'],
      'limits':['No Android or network in this suite','Does not prove frequency or latency of physical gameplay','Transient rejecting executor retries only on next caller; real executor only rejects at shutdown']}
    (a.work/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(run.stdout,end=''); print('receipt='+str(a.work/'receipt.json'))

if __name__ == '__main__': main()
