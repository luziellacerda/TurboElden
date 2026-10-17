"""Change only R179 version attributes; retain its updater and permissions."""
from pathlib import Path
import importlib.util, struct

_path=Path(__file__).resolve().parents[2]/'psx-updater-r170/recipe/manifest_delta.py'
_spec=importlib.util.spec_from_file_location('r170_binary_xml',_path)
_xml=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_xml)

def patch(raw):
    original=_xml.chunks(raw)
    pools=[v for k,v in original if k==1]
    _xml.need(len(pools)==1,'Exactly one pool')
    pool=_xml.Pool(pools[0]);roots=[];permissions=[];sdk=[]
    for i,(kind,chunk) in enumerate(original):
        if kind!=0x102:continue
        tag=_xml.name(chunk,pool);attrs=_xml.attributes(chunk,pool)
        if tag=='manifest':roots.append(i)
        if tag=='uses-permission':permissions.append(attrs[(_xml.NS,'name')][2])
        if tag=='uses-sdk':sdk.append((attrs[(_xml.NS,'minSdkVersion')][2],attrs[(_xml.NS,'targetSdkVersion')][2]))
    _xml.need(len(roots)==1 and sdk==[(26,34)],'Preserve SDK26/34')
    _xml.need('android.permission.WAKE_LOCK' in permissions and 'android.permission.ACCESS_WIFI_STATE' in permissions,'Existing Wi-Fi lease permissions')
    root=bytearray(original[roots[0]][1]);attrs=_xml.attributes(root,pool)
    _xml.need(attrs[(None,'package')][2]==_xml.PACKAGE,'Exact package')
    off,kind,value,_=attrs[(_xml.NS,'versionCode')]
    _xml.need(kind==16 and value==21,'Exact R179 required')
    struct.pack_into('<I',root,off+16,22)
    off,kind,value,_=attrs[(_xml.NS,'versionName')]
    _xml.need(kind==3 and value=='1.0.8-R179','Exact R179 name')
    index=pool.index('1.0.8-R180')
    struct.pack_into('<I',root,off+8,index);struct.pack_into('<I',root,off+16,index)
    body=b''.join(pool.build() if k==1 else bytes(root) if i==roots[0] else c for i,(k,c) in enumerate(original))
    result=struct.pack('<HHI',3,8,len(body)+8)+body;after=_xml.chunks(result)
    _xml.need(len(after)==len(original),'No new components or nodes')
    for i,(before,actual) in enumerate(zip(original,after)):
        if before[0]!=1 and i!=roots[0]:_xml.need(before==actual,'Unrelated manifest node changed')
    _xml.need(_xml.Pool(next(c for k,c in after if k==1)).values==pool.values+['1.0.8-R180'],'Only version string appended')
    return result
