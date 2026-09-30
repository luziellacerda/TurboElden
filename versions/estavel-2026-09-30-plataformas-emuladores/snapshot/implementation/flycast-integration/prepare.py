from pathlib import Path
import copy, json, re, shutil, xml.etree.ElementTree as ET

R=Path(r'\\?\E:\ESTUDO APK\work\native-carousel\implementation\flycast-integration')
D=R/'current-decoded'; F=R/'frontend-decoded'; M=R/'merged'
A='{http://schemas.android.com/apk/res/android}'
AUTO='{http://schemas.android.com/apk/res-auto}'
ET.register_namespace('android',A[1:-1]); ET.register_namespace('app',AUTO[1:-1])
def prefix(name):return 'tf_'+name.replace('$','private_')
# Remove only obsolete donor files created by the previous naming rule.
if (M/'res').exists():
    for f in (M/'res').glob('*/td_$*'):
        if f.is_file():f.unlink()
shutil.copytree(F,M,dirs_exist_ok=True)

# Isolate dependencies, but keep platform API stubs bound to Android's boot classes.
# Read every original DEX class definition, including the preserved Dolphin DEX.
import zipfile,struct
front_classes=set()
with zipfile.ZipFile(R.parent/'TurboramaStation-Dolphin-2609-7.apk') as apk:
    for name in apk.namelist():
        if not (name.startswith('classes') and name.endswith('.dex')):continue
        data=apk.read(name)
        u32=lambda off:struct.unpack_from('<I',data,off)[0]
        strings_off=u32(60);types_off=u32(68);count=u32(96);classes_off=u32(100)
        for i in range(count):
            idx=u32(classes_off+32*i);sid=u32(types_off+4*idx);off=u32(strings_off+4*sid)
            while data[off]&128:off+=1
            off+=1;end=data.index(0,off);desc=data[off:end].decode('utf-8')
            front_classes.add(desc[1:-1])

def platform_class(name):
    return name.startswith(('java/','javax/','dalvik/','org/xml/','org/w3c/')) or (name.startswith('android/') and not name.startswith('android/support/'))
class_map={}
for root in D.glob('smali*'):
    for f in root.rglob('*.smali'):
        old=f.relative_to(root).as_posix()[:-6]
        if old.startswith(('com/flycast/emulator/','com/google/androidgamesdk/')) or platform_class(old):new=old
        elif old.startswith('androidx/'):new='tflycast/'+old[9:]
        else:new='tflycast/shaded/'+old
        class_map[old]=new
dot_map={k.replace('/','.'):v.replace('/','.') for k,v in class_map.items()}

front_public=ET.parse(M/'res/values/public.xml'); pub=front_public.getroot()
front_types={}; next_entry={}
for e in pub:
    if e.tag!='public':continue
    rid=int(e.attrib['id'],16);typ=e.attrib['type']
    front_types[typ]=(rid>>16)&255
    next_entry[typ]=max(next_entry.get(typ,0),(rid&65535)+1)
donor_public=ET.parse(D/'res/values/public.xml').getroot()
resource_map={}; names={}; idmap={}
for e in donor_public:
    if e.tag!='public':continue
    typ=e.attrib['type']; name=e.attrib['name'];new=prefix(name)
    if typ not in front_types:
        front_types[typ]=max(front_types.values())+1;next_entry[typ]=0
    assert next_entry[typ]<65536
    rid=0x7f000000|(front_types[typ]<<16)|next_entry[typ];next_entry[typ]+=1
    old=int(e.attrib['id'],16);idmap[old]=rid;names[(typ,name)]=new
    resource_map[e.attrib['id']]=f'0x{rid:08x}'
    ET.SubElement(pub,'public',{'type':typ,'name':new,'id':f'0x{rid:08x}'})
front_public.write(M/'res/values/public.xml',encoding='utf-8',xml_declaration=True)

resource_ref=re.compile(r'([@?])(\+?)([A-Za-z0-9_.]+:)?([a-zA-Z_][a-zA-Z_0-9]*)/([A-Za-z0-9_.$]+)')
hex_ref=re.compile(r'(?<![\w])0x7f[0-9a-fA-F]{6}(?![\w])')
descriptor=re.compile(r'L([A-Za-z0-9_$/.-]+);')
const_string=re.compile(r'(const-string(?:/jumbo)?\s+\w+,\s+")([^"\n]*)(")')

def refs(s):
    def sub(m):
        if m[3] and m[3]!='com.flycast.emulator:':return m[0]
        name=names.get((m[4],m[5]));return m[1]+m[2]+m[4]+'/'+name if name else m[0]
    s=resource_ref.sub(sub,s)
    s=re.sub(r'\?([A-Za-z_][\w.]*)',lambda m:'?'+names.get(('attr',m[1]),m[1]),s)
    return hex_ref.sub(lambda m:f'0x{idmap.get(int(m[0],16),int(m[0],16)):08x}',s)

def xml_node(e,values=False,parent=None):
    if e.tag in dot_map:e.tag=dot_map[e.tag]
    for key,val in list(e.attrib.items()):
        newkey=key
        if key.startswith(AUTO):newkey=AUTO+'tf_'+key[len(AUTO):]
        if key.startswith('{http://schemas.android.com/apk/res/com.flycast.emulator}'):
            newkey=AUTO+'tf_'+key.split('}',1)[1]
        val=refs(val)
        if val in dot_map:val=dot_map[val]
        if key=='name' and values:
            if parent=='resources':val=prefix(val)
            elif parent=='style' and not val.startswith('android:'):val='tf_'+val
        if key=='parent' and e.tag=='style' and val and not val.startswith(('@','android:')):val='tf_'+val
        if key.endswith('constraint_referenced_ids'):
            val=','.join(names.get(('id',x.strip()),x.strip()) for x in val.split(','))
        if newkey!=key:del e.attrib[key]
        e.attrib[newkey]=val
    if e.text:
        e.text=refs(e.text)
        if e.text.strip() in dot_map:e.text=dot_map[e.text.strip()]
    for child in e:xml_node(child,values,e.tag)

for folder in (D/'res').iterdir():
    if not folder.is_dir():continue
    outdir=M/'res'/folder.name;outdir.mkdir(exist_ok=True)
    for f in folder.iterdir():
        if f.name=='public.xml':continue
        dest=outdir/prefix(f.name)
        if f.suffix=='.xml':
            tree=ET.parse(f);xml_node(tree.getroot(),folder.name.startswith('values'))
            tree.write(dest,encoding='utf-8',xml_declaration=True)
        else:shutil.copy2(f,dest)

library_names={
 'file_redirect_hook':'file_redirecf_hook',
 'gsl_alloc_hook':'fsl_alloc_hook',
 'hook_impl':'fhok_impl',
 'main_hook':'flyc_hook',
}

for n,root in enumerate(sorted(D.glob('smali*')),start=13):
    target=M/f'smali_classes{n}';target.mkdir(exist_ok=True)
    for f in root.rglob('*.smali'):
        old=f.relative_to(root).as_posix()[:-6]
        if platform_class(old):
            obsolete=target/('tflycast/shaded/'+old+'.smali')
            if obsolete.is_file():obsolete.unlink()
            if old in front_classes:continue
        dest=target/(class_map[old]+'.smali');dest.parent.mkdir(parents=True,exist_ok=True)
        s=f.read_text(encoding='utf-8')
        s=descriptor.sub(lambda m:'L'+class_map.get(m[1],m[1])+';',s)
        s=hex_ref.sub(lambda m:f'0x{idmap.get(int(m[0],16),int(m[0],16)):08x}',s)
        s=re.sub(r'const/high16(\s+\w+,\s+)(0x[0-9a-fA-F]+)',lambda m:('const' if int(m[2],16)&65535 else 'const/high16')+m[1]+m[2],s)
        def string_sub(m):
            val=m[2]
            val=dot_map.get(val,class_map.get(val,val))
            if val in library_names:val=library_names[val]
            if val=='com.flycast.emulator':val='org.emulationstation.frontend'
            if val=='.filesprovider':val='.dolphin.filesprovider'
            if val=='.user':val='.dolphin.user'
            if val=='_preferences':val='_dolphin_preferences'
            return m[1]+val+m[3]
        s=const_string.sub(string_sub,s)
        unrelocated=[m[1] for m in descriptor.finditer(s) if m[1] in class_map and class_map[m[1]]!=m[1]]
        assert not unrelocated,(f,unrelocated[:3])
        # Startup tests an unprefixed resource string; both sides retain the same marker.
        dest.write_text(s,encoding='utf-8')

# Embed only the official Flycast Activity and supporting providers.
manifest=ET.parse(M/'AndroidManifest.xml');application=manifest.getroot().find('application')
donor_app=ET.parse(D/'AndroidManifest.xml').getroot().find('application')
for e in donor_app:
    if e.tag not in ['activity','provider']:continue
    original=e.get(A+'name','')
    if e.tag=='activity' and original!='com.flycast.emulator.NativeGLActivity':continue
    child=copy.deepcopy(e);xml_node(child)
    child.set(A+'process',':flycast')
    if child.tag=='activity':
        child.set(A+'exported','false');child.set(A+'enableOnBackInvokedCallback','false')
        child.set(A+'theme','@android:style/Theme.NoTitleBar.Fullscreen')
        child.set(A+'taskAffinity','org.emulationstation.frontend.flycast')
    if child.tag=='provider':
        child.set(A+'authorities',child.get(A+'authorities','').replace('com.flycast.emulator.','org.emulationstation.frontend.flycast.'))
    application.append(child)
permissions={x.get(A+'name') for x in manifest.getroot().findall('uses-permission')}
for name in ['android.permission.RECORD_AUDIO','android.permission.ACCESS_WIFI_STATE','android.permission.CHANGE_WIFI_MULTICAST_STATE','android.permission.ACCESS_NETWORK_STATE','android.permission.BLUETOOTH']:
    if name not in permissions:ET.SubElement(manifest.getroot(),'uses-permission',{A+'name':name})
manifest.write(M/'AndroidManifest.xml',encoding='utf-8',xml_declaration=True)
libdir=M/'lib/arm64-v8a';libdir.mkdir(parents=True,exist_ok=True)
binary_replacements={b'androidx/':b'tflycast/'}
for old,new in library_names.items():binary_replacements[('lib'+old+'.so').encode()]=('lib'+new+'.so').encode()
for f in (D/'lib/arm64-v8a').glob('*.so'):
    data=f.read_bytes()
    for old,new in binary_replacements.items():
        assert len(old)==len(new),(old,new)
        data=data.replace(old,new)
    name='lib'+library_names.get(f.name[3:-3],f.name[3:-3])+'.so'
    (libdir/name).write_bytes(data)
assets=M/'assets/flycast-integration';assets.mkdir(parents=True,exist_ok=True)
shutil.copy2(R/'source/LICENSE',assets/'LICENSE')
selected=json.loads((R/'selected-build.json').read_text('utf-8'))
provenance={'official_version':'v2.7-44-ge36e9df2d','commit':'e36e9df2dcc1487acdb1dc7725766f1f5ba029b5','official_apk':selected['url'],'official_apk_sha256':selected['sha256'],'source':'https://github.com/flyinghead/flycast','source_rebuilt':False,'integration':'Official Android engine and UI embedded, isolated dependencies/resources and process; JNI namespace preserved.'}
(assets/'provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
(R/'class-map.json').write_text(json.dumps(class_map),encoding='utf-8')
(R/'resource-map.json').write_text(json.dumps(resource_map,indent=2),encoding='utf-8')
print('Prepared',len(class_map),'classes and',len(resource_map),'resources.')
