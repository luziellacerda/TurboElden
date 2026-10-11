"""Append only one internal bridge activity and two package visibility entries."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct, zipfile

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
MANIFEST_SHA='e8822a0c4e98c6d6edd57797a1876c740f05682ac6a533bf580736f171ba0387'
ACTIVITY='org.emulationstation.frontend.offline.StationSonyOfflineActivity'
TEMPLATE='org.emulationstation.frontend.netplay.StationPsxOnlineActivity'
PACKAGE='org.turboramastation.frontend'
TARGETS=('aenu.aps3e','com.bachatas4.android.github')

def helper():
 path=REPO/'versions/station-game-menu-controller-audit-r120-20261010/recipes/patch_component_factory.py'
 spec=importlib.util.spec_from_file_location('offline_axml',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def patch(data,h):
 if hashlib.sha256(data).hexdigest()!=MANIFEST_SHA:raise ValueError('Current R127 manifest required')
 chunks=list(h.chunks(data));po,_,ph,ps=next(c for c in chunks if c[1]==1)
 ro,_,rh,rs=next(c for c in chunks if c[1]==0x180)
 resources=list(struct.unpack_from('<'+'I'*((rs-rh)//4),data,ro+rh));strings=h.string_pool(data,po);extra=[]
 def string(text):
  if text in strings:return strings.index(text)
  if text not in extra:extra.append(text)
  return len(strings)+extra.index(text)
 if ACTIVITY in strings:raise ValueError('Offline activity already present')
 clone=None;application_end=None;application_start=None;queries_end=None;queries_started=False;name_index=None;android_ns=None
 for off,kind,header,size in chunks:
  if kind not in (0x102,0x103):continue
  tag=strings[h.u32(data,off+20)]
  if tag=='application':
   if kind==0x102:application_start=off
   else:application_end=off
  if tag=='queries':
   if kind==0x102:queries_started=True
   else:queries_end=off
  if kind!=0x102 or tag!='activity':continue
  start,width,count=struct.unpack_from('<HHH',data,off+24)
  if width!=20:raise ValueError('Attribute width changed')
  attrs={}
  for i in range(count):
   p=off+16+start+i*width;n=h.u32(data,p+4)
   if n<len(resources):attrs[resources[n]]=p
  at=attrs.get(0x01010003)
  if at is None or strings[h.u32(data,at+16)]!=TEMPLATE:continue
  if h.u32(data,attrs[0x01010010]+16)!=0:raise ValueError('Template must remain unexported')
  end=off+size
  if struct.unpack_from('<H',data,end)[0]!=0x103:raise ValueError('Template must be a leaf')
  clone=bytearray(data[off:end+h.u32(data,end+4)])
  for pos,text in ((at,ACTIVITY),(attrs[0x01010011],PACKAGE)):
   index=string(text);h.put32(clone,pos-off+8,index);h.put32(clone,pos-off+16,index)
  name_index=h.u32(data,at+4);android_ns=h.u32(data,at)
 if clone is None or application_end is None or application_start is None:raise ValueError('Current PSX manifest template missing')
 def node(kind,name,attributes=b''):
  line=0;comment=0xffffffff;namespace=0xffffffff
  if kind==0x102:
   tail=struct.pack('<IIHHHHHH',namespace,string(name),20,20,len(attributes)//20,0,0,0)+attributes
  else:tail=struct.pack('<II',namespace,string(name))
  return struct.pack('<HHIII',kind,16,16+len(tail),line,comment)+tail
 packages=b''
 for target in TARGETS:
  index=string(target)
  attr=struct.pack('<IIIHBBI',android_ns,name_index,index,8,0,3,index)
  packages+=node(0x102,'package',attr)+node(0x103,'package')
 if queries_started and queries_end is None:raise ValueError('Unclosed queries element')
 insertion=queries_end if queries_started else application_start
 query_insert=packages if queries_started else node(0x102,'queries')+packages+node(0x103,'queries')
 old=data[po:po+ps];count,styles,flags,start,style_start=struct.unpack_from('<IIIII',data,po+8)
 raw=bytearray(old[start:style_start or ps]);offsets=[];utf8=bool(flags&256)
 for text in extra:
  offsets.append(len(raw));encoded=text.encode('utf-8' if utf8 else 'utf-16-le')
  raw+=h.encode_length(len(text),utf8)+(h.encode_length(len(encoded),True) if utf8 else b'')+encoded+(b'\0' if utf8 else b'\0\0')
 raw+=b'\0'*(-len(raw)%4)
 pool=bytearray(old[:ph]+old[ph:ph+count*4]+struct.pack('<'+'I'*len(offsets),*offsets)+old[ph+count*4:start]+raw+(old[style_start:] if style_start else b''))
 h.put32(pool,4,len(pool));h.put32(pool,8,count+len(extra));h.put32(pool,20,start+4*len(extra))
 if style_start:h.put32(pool,24,start+4*len(extra)+len(raw))
 events=sorted(((insertion,query_insert),(application_end,bytes(clone))))
 result=bytearray();last=po+ps;result+=data[:po]+pool
 inserted=[]
 for at,added in events:
  result+=data[last:at];inserted.append((len(result),len(added)));result+=added;last=at
 result+=data[last:];h.put32(result,4,len(result))
 reverse=bytearray(result)
 for at,size in reversed(inserted):reverse=reverse[:at]+reverse[at+size:]
 reverse=reverse[:po]+old+reverse[po+len(pool):];h.put32(reverse,4,len(reverse))
 if bytes(reverse)!=data or h.string_pool(result,po)!=strings+extra:raise ValueError('Original manifest not exactly preserved')
 list(h.chunks(result));return bytes(result)

def main():
 p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
 with zipfile.ZipFile(a.base) as z:data=z.read('AndroidManifest.xml')
 result=patch(data,helper());a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_bytes(result)
 receipt={'donorManifestSha256':MANIFEST_SHA,'manifestSha256':hashlib.sha256(result).hexdigest(),'addedActivity':ACTIVITY,'process':PACKAGE,'exported':False,'addedPackageQueries':list(TARGETS),'exactInverse':True,'existingAttributesAndActivitiesUnchanged':True,'existingFactoryUnchanged':True}
 a.receipt.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))
if __name__=='__main__':main()
