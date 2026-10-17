from pathlib import Path
import hashlib,re
OWNER='Lorg/emulationstation/frontend/netplay/StationRetroLaunch;'
RELATIVE='org/emulationstation/frontend/netplay/StationRetroLaunch.smali'
ORIGINAL_CLASS_SHA='b09705cff96824dee7cff60fc260f94b084a0c168a780fb5bcfd2acbbb831268'
METHOD='.method private static prepareSnesMultitap(Lorg/emulationstation/frontend/netplay/StationOnlineGame;Ljava/io/File;Ljava/lang/StringBuilder;I)V'
def need(x,t):
 if not x:raise ValueError(t)
def norm(b):return b.decode().replace('\r\n','\n')
def projection(t):
 labels={}
 def f(m):
  x=m[0]
  if x not in labels:labels[x]=':label'+str(len(labels))
  return labels[x]
 return '\n'.join(l.strip() for l in re.sub(r':[A-Za-z_][A-Za-z_0-9]*',f,t).splitlines() if l.strip())
def span(t):
 a=t.index(METHOD);return a,t.index('.end method',a)+len('.end method')
def body(name):return Path(__file__).with_name(name).read_text().strip()
def patch(raw):
 need(hashlib.sha256(raw).hexdigest()==ORIGINAL_CLASS_SHA,'Exact R142 Launch required')
 t=norm(raw);a,b=span(t);need(t[a:b]==body('r142-multitap-method.smali'),'Exact R142 helper required')
 t=t[:a]+body('snes-multitap-method.smali')+t[b:];return t.replace('\n','\r\n' if b'\r\n' in raw else '\n').encode()
def inverse(raw):
 t=norm(raw);a,b=span(t);need(projection(t[a:b])==projection(body('snes-multitap-method.smali')),'Unique flag helper differs from frozen source')
 return t[:a]+body('r142-multitap-method.smali')+t[b:]
def verify(donor,candidate):
 before={p.relative_to(donor).as_posix():p.read_bytes() for p in donor.rglob('*.smali')};after={p.relative_to(candidate).as_posix():p.read_bytes() for p in candidate.rglob('*.smali')}
 need(len(before)==len(after)==608 and set(before)==set(after),'No added or removed class')
 need({n for n in before if before[n]!=after[n]}=={RELATIVE},'Only Launch helper may change')
 need(inverse(after[RELATIVE])==norm(before[RELATIVE]),'All original R142 instructions recover exactly')
 return dict(originalClassCount=608,finalClassCount=608,unchangedClasses=607,modifiedClasses=[OWNER],modifiedMethods=[METHOD],addedMethods=[],addedClasses=[],removedClasses=[],inversePassed=True,condition='snes + snes-multitap-port2-v1 only',uniqueRemapFlag=True)
