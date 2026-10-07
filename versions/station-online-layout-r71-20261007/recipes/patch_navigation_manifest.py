"""Patch one typed Manifest attribute after checking its complete binary identity.

No resources are rebuilt. The singleInstance -> singleTask change applies only
on ESActivity. Consumers receive bytes and a semantic receipt; this module has
no filesystem writes or packaging/install side effects.
"""
import hashlib
import struct

BASE_SHA256='1ce56b447f6f7afa1b7fbeab7a31bc0bc5d14bf823a6b14eab58be6b37624d6a'
FRONTEND='org.emulationstation.frontend.ESActivity'
ANDROID='http://schemas.android.com/apk/res/android'

def require(ok,message):
    if not ok: raise ValueError(message)

def u16(data,offset):return struct.unpack_from('<H',data,offset)[0]
def u32(data,offset):return struct.unpack_from('<I',data,offset)[0]
def digest(data):return hashlib.sha256(data).hexdigest()

def pool(data,start,header):
    count=u32(data,start+8);utf8=bool(u32(data,start+16)&256);strings=start+u32(data,start+20)
    def length(pos,wide):
        value=u16(data,pos) if wide else data[pos];pos+=2 if wide else 1;flag=32768 if wide else 128
        if value&flag:
            value=((value&(flag-1))<<(16 if wide else 8))+(u16(data,pos) if wide else data[pos]);pos+=2 if wide else 1
        return value,pos
    result=[]
    for i in range(count):
        pos=strings+u32(data,start+header+i*4)
        size,pos=length(pos,not utf8)
        if utf8:size,pos=length(pos,False)
        result.append(data[pos:pos+size*(1 if utf8 else 2)].decode('utf8' if utf8 else 'utf-16le'))
    return result

def attributes(data):
    require(u16(data,0)==3 and u32(data,4)==len(data),'Malformed binary XML')
    strings=[];resources=[];found=[];offset=u16(data,2)
    while offset<len(data):
        kind,header,size=struct.unpack_from('<HHI',data,offset)
        require(size>=header>=8 and offset+size<=len(data),'Malformed XML chunk')
        if kind==1:strings=pool(data,offset,header)
        elif kind==0x180:resources=[u32(data,p) for p in range(offset+header,offset+size,4)]
        elif kind==0x102:
            element=strings[u32(data,offset+20)];start=offset+16+u16(data,offset+24);stride=u16(data,offset+26);count=u16(data,offset+28)
            require(stride>=20 and start+stride*count<=offset+size,'Malformed XML attributes')
            attrs=[]
            for i in range(count):
                pos=start+i*stride;ns,name,raw=struct.unpack_from('<III',data,pos);typ=data[pos+15];value=u32(data,pos+16)
                attrs.append(dict(name=strings[name],namespace=None if ns==0xffffffff else strings[ns],resource=resources[name] if name<len(resources) else None,type=typ,value=strings[value] if typ==3 else value,dataOffset=pos+16,raw=raw))
            found.append((element,attrs))
        offset+=size
    require(offset==len(data),'Truncated XML')
    return found

def patch_manifest(data):
    require(digest(data)==BASE_SHA256,'Use the exact preserved R70 Manifest')
    matches=[]
    for element,attrs in attributes(data):
        if element!='activity':continue
        name=[a for a in attrs if a['namespace']==ANDROID and a['resource']==0x01010003]
        if len(name)==1 and name[0]['value']==FRONTEND:
            matches += [a for a in attrs if a['namespace']==ANDROID and a['resource']==0x0101001d]
    require(len(matches)==1,'ESActivity launchMode is not unique')
    old=matches[0];require(old['name']=='launchMode' and old['type']==0x10 and old['value']==3,'Expected singleInstance typed enum')
    require(old['raw']==0xffffffff,'Unexpected raw launchMode string')
    result=bytearray(data);struct.pack_into('<I',result,old['dataOffset'],2);result=bytes(result)
    semantic_before=attributes(data);semantic_after=attributes(result)
    delta=[]
    for (element,left),(right_element,right) in zip(semantic_before,semantic_after):
        require(element==right_element and len(left)==len(right),'Manifest structure changed')
        for a,b in zip(left,right):
            if a!=b:delta.append((element,a,b))
    require(len(delta)==1 and delta[0][1]==old and delta[0][2]==dict(old,value=2),'Unexpected semantic Manifest change')
    changed=[i for i,(a,b) in enumerate(zip(data,result)) if a!=b]
    require(len(data)==len(result) and changed==[old['dataOffset']],'Unexpected binary Manifest change')
    receipt=dict(baseSHA256=digest(data),resultSHA256=digest(result),bytes=len(data),
        component=FRONTEND,attribute='android:launchMode',before='singleInstance',after='singleTask',
        beforeValue=3,afterValue=2,dataOffset=old['dataOffset'],changedByteOffsets=changed,
        semanticChanges=1,allOtherManifestBytesPreserved=True)
    return result,receipt
