import pathlib,struct,json,hashlib
p=pathlib.Path(__file__).parent
raw=(p.parent/'libmain-baseline.so').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='a1ae357dc29caac52d47386a71a0a9a685ecffb9c01d536f5af50b5ba658cda8'
shoff=struct.unpack_from('<Q',raw,40)[0]; count,strings=struct.unpack_from('<HH',raw,60)
secs=[struct.unpack_from('<IIQQQQIIQQ',raw,shoff+i*64) for i in range(count)]
ns=secs[strings]; names=raw[ns[4]:ns[4]+ns[5]]
def z(data,n):return data[n:data.index(b'\0',n)].decode()
sd={z(names,s[0]):s for s in secs}
s=sd['.dynsym']; st=secs[s[6]]; strs=raw[st[4]:st[4]+st[5]]
syms=[struct.unpack_from('<IBBHQQ',raw,i) for i in range(s[4],s[4]+s[5],24)]
exports={z(strs,x[0]):x[4] for x in syms if x[4]}
(p/'exports.json').write_text(json.dumps(exports,indent=2),encoding='utf-8')
rel=[]
for sec in secs:
 if sec[1]!=4:continue
 for i in range(sec[4],sec[4]+sec[5],24):
  at,info,add=struct.unpack_from('<QQq',raw,i); typ=info&0xffffffff; sym=info>>32
  value=syms[sym][4] if sym else add
  if value:rel.append((at,value,typ))
(p/'relocations.h').write_text('static const unsigned long relocations[][2]={\n'+''.join('{0x%x,0x%x},\n'%(a,v) for a,v,t in rel)+'};\n',encoding='utf-8')
rows=json.loads((p.parent/'mapa-sistemas-agrupados.json').read_text(encoding='utf-8'))
headers=['struct SystemDef {const char* key; const char* title; const char* path; const unsigned char* image; unsigned long length;};']
def c(s):return json.dumps(s,ensure_ascii=True)
for i,row in enumerate(rows):
 img=pathlib.Path(row['capas'][0]).read_bytes()
 headers.append('static const unsigned char img%d[]={%s};'%(i,','.join(str(x) for x in img)))
headers.append('static const SystemDef systems[]={')
for i,row in enumerate(rows):
 title=row['chave_filtro'].strip()
 headers.append('{%s,%s,%s,img%d,sizeof(img%d)},'%(c(row['chave_filtro']),c(title),c('/data/data/org.emulationstation.frontend/files/native-systems/%02d.jpg'%i),i,i))
headers.append('};\nstatic constexpr int NSYSTEMS=sizeof(systems)/sizeof(systems[0]);')
(p/'systems.h').write_text('\n'.join(headers),encoding='utf-8')
print('Generated',len(rows),'systems,',len(rel),'relocations; image bytes',sum(pathlib.Path(x['capas'][0]).stat().st_size for x in rows))
