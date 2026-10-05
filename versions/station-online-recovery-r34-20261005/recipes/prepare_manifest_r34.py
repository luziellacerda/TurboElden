from pathlib import Path
import struct,zipfile,json,hashlib
W=Path(__file__).resolve().parent
B=Path(r"G:\BAKUP SISTEMA APP 03-10-2026\apks-candidatos-visuais\TurboStations-Titulo-Barra-R33-20261005.apk")
with B.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='9313b3b893468270512b8e8ee3fa984763d6db334b4534a2f863216a0cc4a7ea'
with zipfile.ZipFile(B) as z:original=z.read('AndroidManifest.xml')
data=bytearray(original);strings=[];offset=8;changed=[]
def u16(p):return struct.unpack_from('<H',data,p)[0]
def u32(p):return struct.unpack_from('<I',data,p)[0]
def length8(p):
 a=data[p];return (((a&127)<<8)|data[p+1],p+2) if a&128 else (a,p+1)
while offset<len(data):
 kind,header,size=struct.unpack_from('<HHI',data,offset);assert size>=header and offset+size<=len(data)
 if kind==1:
  count=u32(offset+8);flags=u32(offset+16);start=u32(offset+20)
  for i in range(count):
   p=offset+start+u32(offset+header+4*i)
   if flags&0x100:
    _,p=length8(p);length,p=length8(p);strings.append(bytes(data[p:p+length]).decode('utf8'))
   else:
    length=u16(p);p+=2
    if length&0x8000:length=((length&0x7fff)<<16)|u16(p);p+=2
    strings.append(bytes(data[p:p+length*2]).decode('utf-16le'))
 if kind==0x102 and strings[u32(offset+20)]=='activity':
  start=offset+16+u16(offset+24);step=u16(offset+26);count=u16(offset+28)
  attrs={strings[u32(start+i*step+4)]:start+i*step for i in range(count)}
  a=attrs.get('name');value=strings[u32(a+16)] if a is not None and data[a+15]==3 else ''
  if value=='org.emulationstation.frontend.netplay.StationRetroActivity':
   a=attrs['enableOnBackInvokedCallback'];assert data[a+15]==0x12 and u32(a+16)==0
   struct.pack_into('<I',data,a+16,0xffffffff);changed.append(a+16)
 offset+=size
assert len(changed)==1
assert [i for i,(a,b) in enumerate(zip(original,data)) if a!=b]==list(range(changed[0],changed[0]+4))
path=W/'AndroidManifest.xml'
if path.exists():assert path.read_bytes()==bytes(data),'Prepared manifest differs'
else:path.write_bytes(data)
print('Manifest verified: exactly four bytes changed for the online Activity Back callback')
