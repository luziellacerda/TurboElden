"""Append one private launch anchor, retaining every original manifest chunk.

The new anchor clones StationRoomsActivity's private, main-process, landscape
attributes. Actual Mupen GameActivity and CoreService remain in :n64core.
"""
from pathlib import Path
import argparse, hashlib, json, struct, zipfile, importlib.util

BASE_SHA='c4e9a6d69497bb928f53b35b49bef86d1b57a0b2b0bd5d0aa1953cfd5d9752a4'
ANCHOR='org.emulationstation.frontend.netplay.StationN64Activity'
PARENT='org.emulationstation.frontend.netplay.StationRoomsActivity'

def patch(data,helper):
    assert hashlib.sha256(data).hexdigest()==BASE_SHA, 'Unexpected base manifest'
    chunks=list(helper.chunks(data)); po,_,ph,ps=next(c for c in chunks if c[1]==1)
    ro,_,rh,rs=next(c for c in chunks if c[1]==0x180)
    resources=list(struct.unpack_from('<'+'I'*((rs-rh)//4),data,ro+rh))
    strings=helper.string_pool(data,po);assert ANCHOR not in strings
    candidate=None;application_end=None
    for offset,kind,header,size in chunks:
        if kind==0x103 and strings[helper.u32(data,offset+20)]=='application':application_end=offset
        if kind!=0x102 or strings[helper.u32(data,offset+20)]!='activity':continue
        attr_start,attr_size,attr_count=struct.unpack_from('<HHH',data,offset+24);assert attr_size==20
        attrs={}
        for i in range(attr_count):
            pos=offset+16+attr_start+i*attr_size;index=helper.u32(data,pos+4)
            if index<len(resources):attrs[resources[index]]=pos
        name=attrs.get(0x01010003)
        if name is None or strings[helper.u32(data,name+16)]!=PARENT:continue
        assert 0x01010011 not in attrs and helper.u32(data,attrs[0x01010010]+16)==0
        end=offset+size;assert struct.unpack_from('<H',data,end)[0]==0x103, 'Anchor must be leaf'
        clone=bytearray(data[offset:end+helper.u32(data,end+4)]);rel=name-offset
        helper.put32(clone,rel+8,len(strings));helper.put32(clone,rel+16,len(strings));candidate=bytes(clone)
    assert candidate and application_end
    count,styles,flags,start,style_start=struct.unpack_from('<IIIII',data,po+8)
    old=data[po:po+ps];end=style_start or ps;string_data=old[start:end]
    utf8=bool(flags&256);encoded=ANCHOR.encode('utf-8' if utf8 else 'utf-16-le')
    encoded=helper.encode_length(len(ANCHOR),utf8)+(helper.encode_length(len(encoded),True) if utf8 else b'')+encoded+(b'\0' if utf8 else b'\0\0')
    new_data=string_data+encoded;new_data+=b'\0'*((-len(new_data))%4)
    pool=bytearray(old[:ph]+old[ph:ph+count*4]+struct.pack('<I',len(string_data))+old[ph+count*4:start]+new_data+(old[style_start:] if style_start else b''))
    helper.put32(pool,4,len(pool));helper.put32(pool,8,count+1);helper.put32(pool,20,start+4)
    if style_start:helper.put32(pool,24,start+4+len(new_data))
    output=bytearray(data[:po]+pool+data[po+ps:application_end]+candidate+data[application_end:]);helper.put32(output,4,len(output))
    insert=application_end+len(pool)-ps
    reverse=bytearray(output[:insert]+output[insert+len(candidate):])
    reverse=reverse[:po]+old+reverse[po+len(pool):];helper.put32(reverse,4,len(reverse))
    assert bytes(reverse)==data, 'Other manifest bytes changed'
    assert helper.string_pool(output,po)==strings+[ANCHOR];list(helper.chunks(output))
    return bytes(output)

def main():
    p=argparse.ArgumentParser();p.add_argument('--apk',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    helper_path=Path(__file__).resolve().parents[2]/'station-game-menu-controller-audit-r120-20261010/recipes/patch_component_factory.py'
    spec=importlib.util.spec_from_file_location('axml',helper_path);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    with zipfile.ZipFile(a.apk) as archive:original=archive.read('AndroidManifest.xml')
    result=patch(original,helper);a.out.parent.mkdir(parents=True,exist_ok=True);assert not a.out.exists();a.out.write_bytes(result)
    print(json.dumps({'sha256':hashlib.sha256(result).hexdigest(),'addedActivity':ANCHOR,'reverseIdentity':True}))
if __name__=='__main__':main()
