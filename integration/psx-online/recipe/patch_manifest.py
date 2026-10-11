"""Append one private PSX SDL activity, with an exact inverse of the donor."""
from pathlib import Path
import argparse, hashlib, json, struct, zipfile, importlib.util

ROOT=Path(__file__).resolve().parents[1]
BASE_SHA='f2924c7b49ea4e40f67c41e0f2997ea4dcd5aee6f2d495517b3c5dfa3c664a9d'
ANCHOR='org.emulationstation.frontend.netplay.StationPsxOnlineActivity'
TEMPLATE='org.emulationstation.frontend.netplay.StationDolphinOnlineActivity'
PROCESS=':station_psx_online'

def patch(data,helper):
    chunks=list(helper.chunks(data));po,_,ph,ps=next(c for c in chunks if c[1]==1)
    ro,_,rh,rs=next(c for c in chunks if c[1]==0x180)
    resources=list(struct.unpack_from('<'+'I'*((rs-rh)//4),data,ro+rh));strings=helper.string_pool(data,po)
    if ANCHOR in strings or PROCESS in strings:raise ValueError('PSX already present')
    clone=None;application_end=None
    for off,kind,header,size in chunks:
        if kind==0x103 and strings[helper.u32(data,off+20)]=='application':application_end=off
        if kind!=0x102 or strings[helper.u32(data,off+20)]!='activity':continue
        start,width,count=struct.unpack_from('<HHH',data,off+24)
        if width!=20:raise ValueError('Attribute width')
        attrs={}
        for i in range(count):
            p=off+16+start+i*width;n=helper.u32(data,p+4)
            if n<len(resources):attrs[resources[n]]=p
        at=attrs.get(0x01010003)
        if at is None or strings[helper.u32(data,at+16)]!=TEMPLATE:continue
        if helper.u32(data,attrs[0x01010010]+16)!=0 or strings[helper.u32(data,attrs[0x01010011]+16)]!=':dolphin':raise ValueError('Private process template')
        end=off+size
        if struct.unpack_from('<H',data,end)[0]!=0x103:raise ValueError('Activity must be a leaf')
        clone=bytearray(data[off:end+helper.u32(data,end+4)])
        for pos,index in ((at,len(strings)),(attrs[0x01010011],len(strings)+1)):
            helper.put32(clone,pos-off+8,index);helper.put32(clone,pos-off+16,index)
    if clone is None or application_end is None:raise ValueError('PSX manifest template missing')
    count,styles,flags,start,style_start=struct.unpack_from('<IIIII',data,po+8)
    old=data[po:po+ps];end=style_start or ps;raw=bytearray(old[start:end]);offsets=[];utf8=bool(flags&256)
    for text in (ANCHOR,PROCESS):
        offsets.append(len(raw));encoded=text.encode('utf-8' if utf8 else 'utf-16-le')
        raw+=helper.encode_length(len(text),utf8)+(helper.encode_length(len(encoded),True) if utf8 else b'')+encoded+(b'\0' if utf8 else b'\0\0')
    raw+=b'\0'*(-len(raw)%4)
    pool=bytearray(old[:ph]+old[ph:ph+count*4]+struct.pack('<II',*offsets)+old[ph+count*4:start]+raw+(old[style_start:] if style_start else b''))
    helper.put32(pool,4,len(pool));helper.put32(pool,8,count+2);helper.put32(pool,20,start+8)
    if style_start:helper.put32(pool,24,start+8+len(raw))
    output=bytearray(data[:po]+pool+data[po+ps:application_end]+clone+data[application_end:]);helper.put32(output,4,len(output))
    insertion=application_end+len(pool)-ps
    reverse=bytearray(output[:insertion]+output[insertion+len(clone):]);reverse=reverse[:po]+old+reverse[po+len(pool):];helper.put32(reverse,4,len(reverse))
    if bytes(reverse)!=data or helper.string_pool(output,po)!=strings+[ANCHOR,PROCESS]:raise ValueError('Other manifest changed')
    list(helper.chunks(output));return bytes(output)

def main():
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    sha=hashlib.sha256()
    with a.base.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):sha.update(b)
    if sha.hexdigest()!=BASE_SHA:raise ValueError('R126 exact base required')
    path=ROOT.parents[1]/'versions/station-game-menu-controller-audit-r120-20261010/recipes/patch_component_factory.py'
    spec=importlib.util.spec_from_file_location('axml',path);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    with zipfile.ZipFile(a.base) as archive:data=archive.read('AndroidManifest.xml')
    result=patch(data,helper);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_bytes(result)
    print(json.dumps({'baseManifestSha256':hashlib.sha256(data).hexdigest(),'manifestSha256':hashlib.sha256(result).hexdigest(),'addedPrivateActivity':ANCHOR,'process':PROCESS,'reverseByteIdentical':True}))
if __name__=='__main__':main()
