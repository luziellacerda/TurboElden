"""Only deliver the existing signed SNES multitap devices to the actual R141 remap reader."""
from pathlib import Path
import hashlib,re
OWNER='Lorg/emulationstation/frontend/netplay/StationRetroLaunch;'
RELATIVE='org/emulationstation/frontend/netplay/StationRetroLaunch.smali'
ORIGINAL_CLASS_SHA='56e3d48b9586edebb028fcca7aa11eeabdf66aeb4c5e433733be7363d8e34b65'
METHOD='.method static prepare(Landroid/content/Context;Lorg/emulationstation/frontend/netplay/StationOnlineGame;Lorg/json/JSONObject;Lorg/json/JSONObject;Lorg/emulationstation/frontend/station/StationApi$Cancellation;)Ljava/lang/String;'
HELPER='.method private static prepareSnesMultitap(Lorg/emulationstation/frontend/netplay/StationOnlineGame;Ljava/io/File;Ljava/lang/StringBuilder;I)V'
ANCHOR='    :cond_1a\n    new-instance v5, Ljava/io/File;'
CALL='    move-object/from16 v9, v28\n\n    invoke-static {v1, v9, v2, v6}, '+OWNER+'->prepareSnesMultitap(Lorg/emulationstation/frontend/netplay/StationOnlineGame;Ljava/io/File;Ljava/lang/StringBuilder;I)V\n\n'
def need(ok,t):
 if not ok:raise ValueError(t)
def norm(raw):return raw.decode('utf-8').replace('\r\n','\n')
def digest(raw):return hashlib.sha256(raw).hexdigest()
def method_projection(text):
 labels={}
 def label(m):
  value=m.group(0)
  if value not in labels:labels[value]=':label'+str(len(labels))
  return labels[value]
 text=re.sub(r':[A-Za-z_][A-Za-z_0-9]*',label,text)
 return '\n'.join(l.strip() for l in text.splitlines() if l.strip())
def patch(raw):
 need(digest(raw)==ORIGINAL_CLASS_SHA,'Exact R141 Launch required')
 t=norm(raw);need(t.count(ANCHOR)==1 and HELPER not in t,'Unique prepare boundary required')
 # v6 active mask, v1 verified game, v2 config, v28 room directory; v9 dead.
 t=t.replace(ANCHOR,'    :cond_1a\n'+CALL+'    new-instance v5, Ljava/io/File;')
 pos=t.index('.method private static root(')
 t=t[:pos]+Path(__file__).with_name('snes-multitap-method.smali').read_text().strip()+'\n\n'+t[pos:]
 eol='\r\n' if b'\r\n' in raw else '\n';return t.replace('\n',eol).encode()
def inverse(raw):
 t=norm(raw);need(t.count(HELPER)==1,'One controller helper required')
 a=t.index(HELPER);b=t.index('.end method',a)+len('.end method')
 expected=Path(__file__).with_name('snes-multitap-method.smali').read_text()
 need(method_projection(t[a:b])==method_projection(expected),'New helper differs from frozen scope')
 t=t[:a]+t[b:].lstrip('\n')
 t=t.replace('    :cond_1a\n'+CALL+'    new-instance v5, Ljava/io/File;',ANCHOR)
 return t
def verify(donor,candidate):
 before={p.relative_to(donor).as_posix():p.read_bytes() for p in donor.rglob('*.smali')}
 after={p.relative_to(candidate).as_posix():p.read_bytes() for p in candidate.rglob('*.smali')}
 need(len(before)==len(after)==608 and set(before)==set(after),'No class expansion allowed')
 need({n for n in before if before[n]!=after[n]}=={RELATIVE},'Only Launch may change')
 need(inverse(after[RELATIVE])==norm(before[RELATIVE]),'All original class instructions must recover exactly')
 return dict(originalClassCount=608,finalClassCount=608,unchangedClasses=607,modifiedClasses=[OWNER],modifiedMethods=[METHOD],addedMethods=[HELPER],addedClasses=[],removedClasses=[],inversePassed=True,condition='snes + snes-multitap-port2-v1 only')
