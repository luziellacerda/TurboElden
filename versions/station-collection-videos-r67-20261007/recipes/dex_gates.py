"""Inspect declared DEX classes and refuse module loss or cross-module duplicates."""
import re,struct
def definitions(data):
    if len(data)<112 or not re.fullmatch(rb'dex\n0[0-9]{2}\x00',data[:8]):raise ValueError('DEX header required')
    file_size,header_size,endian=struct.unpack_from('<III',data,32)
    if file_size!=len(data) or header_size!=112 or endian!=0x12345678:raise ValueError('Unexpected DEX layout')
    def table(offset,width):
        count,pos=struct.unpack_from('<II',data,offset)
        if count>1000000 or pos+count*width>len(data):raise ValueError('Invalid DEX table')
        return count,pos
    strings,so=table(56,4);types,to=table(64,4);classes,co=table(96,32)
    def string(index):
        if index>=strings:raise ValueError('Invalid DEX string index')
        pos=struct.unpack_from('<I',data,so+index*4)[0]
        for _ in range(5):
            if pos>=len(data):raise ValueError('Truncated DEX string')
            value=data[pos];pos+=1
            if value<128:break
        else:raise ValueError('Invalid DEX string length')
        end=data.find(b'\x00',pos,min(len(data),pos+4096))
        if end<0:raise ValueError('Invalid DEX descriptor')
        return data[pos:end].decode('ascii')
    result=set()
    for i in range(classes):
        ti=struct.unpack_from('<I',data,co+i*32)[0]
        if ti>=types:raise ValueError('Invalid DEX type index')
        si=struct.unpack_from('<I',data,to+ti*4)[0];name=string(si)
        if not re.fullmatch(r'L[^;\s]+;',name) or name in result:raise ValueError('Invalid/duplicate DEX class')
        result.add(name)
    return result

def verify_modules(archive,replacements):
    names=[n for n in archive.namelist() if re.fullmatch(r'classes(?:[0-9]+)?\.dex',n)]
    if not set(replacements).issubset(names):raise ValueError('Expected DEX slots absent')
    all_classes=set();counts={}
    for name in names:
        original=definitions(archive.read(name));classes=definitions(replacements[name]) if name in replacements else original
        if name in replacements:
            top={c for c in original if '$' not in c}
            if not top.issubset(classes):raise ValueError('Original module top-level classes lost')
            if name=='classes28.dex' and 'Lorg/emulationstation/frontend/station/StationRequestProof;' not in classes:
                raise ValueError('Protected client class absent')
        if all_classes & classes:raise ValueError('Declared class duplicated across APK DEX modules')
        all_classes.update(classes);counts[name]=len(classes)
    return dict(noDuplicateClasses=True,originalModuleTopLevelClassesPreserved=True,moduleClassCounts=counts)
