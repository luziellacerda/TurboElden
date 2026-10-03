"""Bind rebuilt service implementations while preserving every renderer virtual address.
Only a candidate ELF is emitted; this script does not install or modify an APK.
"""
from pathlib import Path
import struct,json,hashlib,sys
r=Path(__file__).resolve().parent
sys.path.insert(0,str(r/'tools/python'))
import lief
source=r/'input/libmain.so';data=bytearray(source.read_bytes())
expected='a1ae357dc29caac52d47386a71a0a9a685ecffb9c01d536f5af50b5ba658cda8'
if hashlib.sha256(data).hexdigest()!=expected:raise RuntimeError('Input native identity changed')
elf=lief.parse(bytes(data));header=struct.unpack_from('<16sHHIQQQIHHHHHH',data)
if header[1:3]!=(3,183) or header[0][:6]!=b'\x7fELF\x02\x01':raise RuntimeError('Requires ELF64 little endian AArch64 DYN')
phoff,phsize,phcount=header[5],header[9],header[10]
if phsize!=56:raise RuntimeError('Unexpected program header size')
ph=[list(struct.unpack_from('<IIQQQQQQ',data,phoff+i*56)) for i in range(phcount)]
loads=[x for x in ph if x[0]==1]
def offset(address,size=1):
 for h in loads:
  if h[3]<=address and address+size<=h[3]+h[5]:return h[2]+address-h[3]
 raise RuntimeError('Address outside file-backed LOAD')
def read(address,size):return bytes(data[offset(address,size):offset(address,size)+size])
dynamic=next(h for h in ph if h[0]==2).copy()
entries=[]
for pos in range(dynamic[2],dynamic[2]+dynamic[5],16):
 tag,value=struct.unpack_from('<qQ',data,pos)
 if tag==0:break
 entries.append((tag,value))
tags=dict(entries)
if tags.get(9)!=24 or tags.get(11)!=24:raise RuntimeError('Unsupported ELF entries')
bindings={
 0x18f790:'StationCatalog_refresh',0x192b48:'StationCatalog_update',
 0x192b7c:'StationCatalog_update',0x192f10:'StationCatalog_update',0x193cfc:'StationCatalog_update',
 0x194924:'StationCatalog_applyPending',0x194a60:'StationCatalog_refreshInstalled',
 0x195c28:'StationCatalog_update',0x196020:'StationCatalog_prioritize',
 0x1961ec:'StationCatalog_start',0x196a2c:'StationCatalog_cancel',
 0x196ac0:'StationCatalog_active',0x196c40:'StationCatalog_progress',0x196cd4:'StationCatalog_uninstall',
}
# Additional reviewed services are supplied by a checked-in, explicit contract only.
extra=r/'src/native/service-bindings.json'
if extra.exists():bindings.update({int(k,16):v for k,v in json.loads(extra.read_text()).items()})
exports=sorted(set(bindings.values()))
front=lief.parse(str(r/'build/native/arm64-v8a/libstation_frontend.so'))
for name in exports:
 symbol=front.get_dynamic_symbol(name)
 if symbol is None or not symbol.value:raise RuntimeError('Missing built replacement: '+name)
symbols=list(elf.dynamic_symbols)
sizes={}
for address in bindings:
 at=[s for s in symbols if s.value==address and s.size>=4]
 if not at:raise RuntimeError('Missing original service symbol '+hex(address))
 if len({s.size for s in at})!=1:raise RuntimeError('Conflicting symbol size')
 sizes[address]=at[0].size
ranges=sorted((a,a+sizes[a]) for a in bindings)
if any(a[1]>b[0] for a,b in zip(ranges,ranges[1:])):raise RuntimeError('Overlapping replacement bodies')
# Old indices remain stable. Only undefined imports are appended.
strings=bytearray(read(tags[5],tags[10]));symtab=bytearray(read(tags[6],len(symbols)*24))
version=bytearray(read(tags[0x6ffffff0],len(symbols)*2))
indices={}
for name in exports:
 nameoff=len(strings);strings.extend(name.encode()+b'\0');indices[name]=len(symtab)//24
 symtab.extend(struct.pack('<IBBHQQ',nameoff,0x12,0,0,0,0));version.extend(struct.pack('<H',1))
needed=len(strings);strings.extend(b'libstation_frontend.so\0')
# A single-bucket GNU hash preserves the established symbol indices exactly.
def gnu_hash(name):
 h=5381
 for c in name.encode():h=((h*33)+c)&0xffffffff
 return h
names=[s.name for s in symbols]+exports
hashes=[gnu_hash(n) for n in names[1:]];bloom=0
for h in hashes:bloom|=(1<<(h%64))|(1<<((h>>5)%64))
gnu=bytearray(struct.pack('<IIIIQI',1,1,1,5,bloom,1))
for i,h in enumerate(hashes):gnu.extend(struct.pack('<I',(h&~1)|(i==len(hashes)-1)))
def align(value,n=16384):return (value+n-1)&~(n-1)
rxoff=align(len(data));rxaddr=align(max(x[3]+x[6] for x in loads));newcount=phcount+2
meta=bytearray(newcount*56)
def append(blob,alignment=8):
 while len(meta)%alignment:meta.append(0)
 addr=rxaddr+len(meta);meta.extend(blob);return addr
straddr=append(strings);symaddr=append(symtab);veraddr=append(version,2);hashaddr=append(gnu)
relocations=bytearray(read(tags[7],tags[8]))
# Relocations and stubs have deterministic sizes, so RW addresses can be fixed before encoding.
reladdr=append(relocations+bytes(len(exports)*24))
stubaddr=append(bytes(len(exports)*16),16)
rwaddr=align(rxaddr+len(meta));rwoff=align(rxoff+len(meta));got={name:rwaddr+i*8 for i,name in enumerate(exports)}
for i,name in enumerate(exports):
 struct.pack_into('<QQq',meta,reladdr-rxaddr+len(relocations)+i*24,got[name],(indices[name]<<32)|1025,0)
 pc=stubaddr+i*16;delta=(got[name]>>12)-(pc>>12)
 if not -(1<<20)<=delta<(1<<20):raise RuntimeError('ADRP range')
 adrp=0x90000010|((delta&3)<<29)|(((delta>>2)&0x7ffff)<<5)
 ldr=0xf9400210|(((got[name]&4095)//8)<<10)
 struct.pack_into('<IIII',meta,pc-rxaddr,adrp,ldr,0xd61f0200,0xd503201f)
rw=bytearray(len(exports)*8)
while len(rw)%16:rw.append(0)
dynaddr=rwaddr+len(rw);dynoff=rwoff+len(rw)
updates={5:straddr,10:len(strings),6:symaddr,0x6ffffef5:hashaddr,0x6ffffff0:veraddr,7:reladdr,8:len(relocations)+len(exports)*24}
newentries=[(t,updates.get(t,v)) for t,v in entries]
newentries.extend([(1,needed),(0,0)])
for entry in newentries:rw.extend(struct.pack('<qQ',*entry))
for h in ph:
 if h[0]==6:h[2:7]=[rxoff,rxaddr,rxaddr,newcount*56,newcount*56]
 if h[0]==2:h[2:7]=[dynoff,dynaddr,dynaddr,len(newentries)*16,len(newentries)*16]
ph.extend([[1,5,rxoff,rxaddr,rxaddr,len(meta),len(meta),16384],[1,6,rwoff,rwaddr,rwaddr,len(rw),len(rw),16384]])
# PT_LOAD must be sorted by virtual address; other header order is immaterial.
loaditer=iter(sorted((h for h in ph if h[0]==1),key=lambda h:h[3]))
ph=[next(loaditer) if h[0]==1 else h for h in ph]
for i,h in enumerate(ph):struct.pack_into('<IIQQQQQQ',meta,i*56,*h)
report=[]
for address,name in bindings.items():
 size=sizes[address];fileoff=offset(address,size);body=bytes(data[fileoff:fileoff+size]);target=stubaddr+exports.index(name)*16
 branch=(target-address)//4
 if (target-address)%4 or not -(1<<25)<=branch<(1<<25):raise RuntimeError('Branch range')
 # Remove the replaced implementation, leaving one direct linker branch at its existing entry.
 data[fileoff:fileoff+size]=(struct.pack('<I',0xd4200000)*(size//4))+bytes(size%4)
 struct.pack_into('<I',data,fileoff,0x14000000|(branch&0x3ffffff))
 report.append({'entry':hex(address),'bytesRemoved':size,'oldSha256':hashlib.sha256(body).hexdigest(),'replacement':name})
data.extend(bytes(rxoff-len(data)));data.extend(meta);data.extend(bytes(rwoff-len(data)));data.extend(rw)
struct.pack_into('<Q',data,32,rxoff);struct.pack_into('<H',data,56,newcount)
# Android validates section metadata as well; keep it consistent with relocated tables.
section_updates={tags[5]:(straddr,rxoff+straddr-rxaddr,len(strings)),tags[6]:(symaddr,rxoff+symaddr-rxaddr,len(symtab)),
 tags[0x6ffffff0]:(veraddr,rxoff+veraddr-rxaddr,len(version)),tags[0x6ffffef5]:(hashaddr,rxoff+hashaddr-rxaddr,len(gnu)),
 tags[7]:(reladdr,rxoff+reladdr-rxaddr,len(relocations)+len(exports)*24),dynamic[3]:(dynaddr,dynoff,len(newentries)*16)}
for i in range(header[12]):
 pos=header[6]+i*64;section=list(struct.unpack_from('<IIQQQQIIQQ',data,pos))
 if section[3] in section_updates:
  section[3],section[4],section[5]=section_updates[section[3]];struct.pack_into('<IIQQQQIIQQ',data,pos,*section)

out=r/'build/native/arm64-v8a/libmain.so';out.write_bytes(data)
check=lief.parse(str(out))
for old in symbols:
 new=check.get_dynamic_symbol(old.name)
 if old.name and (new is None or new.value!=old.value):raise RuntimeError('Renderer address moved: '+old.name)
for old in loads:
 matches=[h for h in check.segments if int(h.type)==1 and h.virtual_address==old[3]]
 if len(matches)!=1 or matches[0].file_offset!=old[2]:raise RuntimeError('Original LOAD moved')
result={'sourceSha256':expected,'outputSha256':hashlib.sha256(data).hexdigest(),'originalSymbolsPreserved':len(symbols),'replacements':report,'apkIntegrated':False,'legacyRemovalComplete':False}
(r/'build/native-link-manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='replacements'},indent=2));print('Rebuilt service entry points:',len(report))
