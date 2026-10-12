"""Index defined classes/method signatures from the exact private APK.

Exports symbol metadata, not DEX bytes, instructions, string constants or keys.
Requires the public entry-hash map. This is an inventory, not code validation.
"""
from pathlib import Path
import argparse, gzip, hashlib, json, struct, zipfile

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--apk',type=Path,required=True)
p.add_argument('--entry-map',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args()
entries=json.loads(a.entry_map.read_text(encoding='utf-8'))
expected={r['path']:r for r in entries}

def uleb(raw,at):
    value=0;shift=0
    for _ in range(5):
        byte=raw[at];at+=1;value|=(byte&127)<<shift
        if not byte&128:return value,at
        shift+=7
    raise ValueError('Invalid ULEB128')

def dex_index(raw,partition):
    assert raw[:4]==b'dex\n' and raw[7]==0 and struct.unpack_from('<I',raw,32)[0]==len(raw)
    assert struct.unpack_from('<I',raw,40)[0]==0x12345678
    assert hashlib.sha1(raw[32:]).digest()==raw[12:32]
    def u32(at):return struct.unpack_from('<I',raw,at)[0]
    strings=[]
    for i in range(u32(56)):
        at=u32(u32(60)+4*i);_,at=uleb(raw,at);end=raw.index(0,at)
        # Java names/descriptors are retained, arbitrary constant strings aren't
        # exported. Modified UTF-8 NUL/supplementary encoding is normalized.
        text=raw[at:end].replace(b'\xc0\x80',b'\x00').decode('utf-8',errors='surrogatepass')
        text=text.encode('utf-16','surrogatepass').decode('utf-16','surrogatepass')
        strings.append(text)
    types=[strings[u32(u32(68)+4*i)] for i in range(u32(64))]
    protos=[]
    for i in range(u32(72)):
        at=u32(76)+12*i;params=u32(at+8)
        args=[] if params==0 else [types[struct.unpack_from('<H',raw,params+4+2*j)[0]] for j in range(u32(params))]
        protos.append('('+''.join(args)+')'+types[u32(at+4)])
    methods=[]
    for i in range(u32(88)):
        owner,proto,name=struct.unpack_from('<HHI',raw,u32(92)+8*i)
        methods.append((types[owner],strings[name],protos[proto]))
    result=[];classes=[]
    for i in range(u32(96)):
        at=u32(100)+32*i;owner=types[u32(at)];flags=u32(at+4);data=u32(at+24)
        classes.append({'dex':partition,'class':owner,'accessFlags':flags})
        if not data:continue
        counts=[]
        for _ in range(4):v,data=uleb(raw,data);counts.append(v)
        for _ in range(counts[0]+counts[1]):_,data=uleb(raw,data);_,data=uleb(raw,data)
        for count in counts[2:]:
            index=0
            for _ in range(count):
                diff,data=uleb(raw,data);index+=diff;access,data=uleb(raw,data);code,data=uleb(raw,data)
                klass,name,signature=methods[index];assert klass==owner
                result.append({'dex':partition,'class':klass,'name':name,'descriptor':signature,'accessFlags':access,'native':bool(access&0x100),'hasCode':code!=0})
    return classes,result

all_classes=[];all_methods=[];counts=[]
with zipfile.ZipFile(a.apk) as archive:
    for n in sorted(expected):
        if not n.endswith('.dex'):continue
        raw=archive.read(n);r=expected[n]
        assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256'],n
        classes,methods=dex_index(raw,n);all_classes+=classes;all_methods+=methods
        counts.append({'dex':n,'sha256':r['sha256'],'classDefinitions':len(classes),'methodDefinitions':len(methods)})
assert sum(r['dex'].startswith('classes') for r in counts)==40
a.out.mkdir(parents=True,exist_ok=True)
def write(n,x):(a.out/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
summary={'schema':'station.dex.defined.api.index.v1','dexCount':len(counts),'rootDexCount':40,'assetDexCount':len(counts)-40,'classDefinitions':len(all_classes),'methodDefinitions':len(all_methods),'nativeDeclarations':sum(r['native'] for r in all_methods),'dex':counts,'includesMethodBodies':False,'includesArbitraryStringConstants':False,'limitations':'Signatures and flags from defined root and asset DEX classes; not original Java sources, external/native implementation or executed coverage.'}
write('dex-api-summary.json',summary);write('dex-defined-classes.json',all_classes)
raw=json.dumps(all_methods,ensure_ascii=False,separators=(',',':')).encode('utf-8')+b'\n'
(a.out/'dex-defined-methods.json.gz').write_bytes(gzip.compress(raw,mtime=0))
print(json.dumps({k:v for k,v in summary.items() if k!='dex'}))
