from pathlib import Path
import copy, json, re, shutil, xml.etree.ElementTree as ET

R=Path(r'\\?\E:\ESTUDO APK\work\native-carousel\implementation\dolphin-integration')
D=R/'dolphin-decoded'; F=R/'frontend-decoded'; M=R/'merged'
A='{http://schemas.android.com/apk/res/android}'
AUTO='{http://schemas.android.com/apk/res-auto}'
ET.register_namespace('android',A[1:-1]); ET.register_namespace('app',AUTO[1:-1])
def prefix(name):return 'td_'+name.replace('$','private_')
# Remove only obsolete donor files created by the previous naming rule.
if (M/'res').exists():
    for f in (M/'res').glob('*/td_$*'):
        if f.is_file():f.unlink()
shutil.copytree(F,M,dirs_exist_ok=True)

# Isolate dependencies, but keep platform API stubs bound to Android's boot classes.
front_classes={f.relative_to(root).as_posix()[:-6] for root in F.glob('smali*') for f in root.rglob('*.smali')}
def platform_class(name):
    return name.startswith(('java/','javax/','dalvik/','org/xml/','org/w3c/')) or (name.startswith('android/') and not name.startswith('android/support/'))
class_map={}
for root in D.glob('smali*'):
    for f in root.rglob('*.smali'):
        old=f.relative_to(root).as_posix()[:-6]
        if old.startswith('org/dolphinemu/dolphinemu/') or platform_class(old):new=old
        elif old.startswith('androidx/'):new='tdolphin/'+old[9:]
        else:new='tdolphin/shaded/'+old
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
        if m[3] and m[3]!='org.dolphinemu.dolphinemu:':return m[0]
        name=names.get((m[4],m[5]));return m[1]+m[2]+m[4]+'/'+name if name else m[0]
    s=resource_ref.sub(sub,s)
    s=re.sub(r'\?([A-Za-z_][\w.]*)',lambda m:'?'+names.get(('attr',m[1]),m[1]),s)
    return hex_ref.sub(lambda m:f'0x{idmap.get(int(m[0],16),int(m[0],16)):08x}',s)

def xml_node(e,values=False,parent=None):
    if e.tag in dot_map:e.tag=dot_map[e.tag]
    for key,val in list(e.attrib.items()):
        newkey=key
        if key.startswith(AUTO):newkey=AUTO+'td_'+key[len(AUTO):]
        if key.startswith('{http://schemas.android.com/apk/res/org.dolphinemu.dolphinemu}'):
            newkey=AUTO+'td_'+key.split('}',1)[1]
        val=refs(val)
        if val in dot_map:val=dot_map[val]
        if key=='name' and values:
            if parent=='resources':val=prefix(val)
            elif parent=='style' and not val.startswith('android:'):val='td_'+val
        if key=='parent' and e.tag=='style' and val and not val.startswith(('@','android:')):val='td_'+val
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
 'androidx.graphics.path':'tdolphin.graphics.path',
 'file_redirect_hook':'dile_redirect_hook',
 'gsl_alloc_hook':'dsl_alloc_hook',
 'hook_impl':'dhok_impl',
 'main_hook':'dolp_hook',
}
for n,root in enumerate(sorted(D.glob('smali*')),start=10):
    target=M/f'smali_classes{n}';target.mkdir(exist_ok=True)
    for f in root.rglob('*.smali'):
        old=f.relative_to(root).as_posix()[:-6]
        if platform_class(old):
            obsolete=target/('tdolphin/shaded/'+old+'.smali')
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
            if val=='org.dolphinemu.dolphinemu':val='org.emulationstation.frontend'
            if val=='.filesprovider':val='.dolphin.filesprovider'
            if val=='.user':val='.dolphin.user'
            if val=='_preferences':val='_dolphin_preferences'
            return m[1]+val+m[3]
        s=const_string.sub(string_sub,s)
        unrelocated=[m[1] for m in descriptor.finditer(s) if m[1] in class_map and class_map[m[1]]!=m[1]]
        assert not unrelocated,(f,unrelocated[:3])
        # Startup tests an unprefixed resource string; both sides retain the same marker.
        dest.write_text(s,encoding='utf-8')

# Donor components stay inside this app and have a dedicated emulator process.
manifest=ET.parse(M/'AndroidManifest.xml');application=manifest.getroot().find('application')
donor_app=ET.parse(D/'AndroidManifest.xml').getroot().find('application')
for e in donor_app:
    if e.tag not in ['activity','provider']:continue
    original=e.get(A+'name','')
    if any(x in original for x in ['PreviewActivity','MainActivity','TvMainActivity','AppLinkActivity']):continue
    child=copy.deepcopy(e);xml_node(child)
    child.set(A+'process',':dolphin')
    if child.tag=='activity':
        child.set(A+'exported','false');child.set(A+'enableOnBackInvokedCallback','false')
    if child.tag=='provider':
        authority=child.get(A+'authorities','').replace('org.dolphinemu.dolphinemu.','org.emulationstation.frontend.dolphin.')
        child.set(A+'authorities',authority)
    application.append(child)
ET.SubElement(application,'activity',{A+'name':'org.emulationstation.frontend.DolphinEntryActivity',A+'process':':dolphin',A+'exported':'false',A+'theme':'@style/td_Theme.Dolphin.Main',A+'screenOrientation':'sensorLandscape',A+'enableOnBackInvokedCallback':'false'})
permissions={x.get(A+'name') for x in manifest.getroot().findall('uses-permission')}
if 'android.permission.RECORD_AUDIO' not in permissions:ET.SubElement(manifest.getroot(),'uses-permission',{A+'name':'android.permission.RECORD_AUDIO'})
manifest.write(M/'AndroidManifest.xml',encoding='utf-8',xml_declaration=True)

# Unique SONAMEs prevent collisions with SDL and the other emulators.
libdir=M/'lib/arm64-v8a';libdir.mkdir(parents=True,exist_ok=True)
binary_replacements={b'androidx/':b'tdolphin/',b'libmain.so':b'libdolp.so'}
for old,new in library_names.items():binary_replacements[('lib'+old+'.so').encode()]=('lib'+new+'.so').encode()
for f in (D/'lib/arm64-v8a').glob('*.so'):
    b=f.read_bytes()
    for old,new in binary_replacements.items():
        assert len(old)==len(new),(old,new)
        b=b.replace(old,new)
    name='libdolp.so' if f.name=='libmain.so' else 'lib'+library_names.get(f.name[3:-3],f.name[3:-3])+'.so'
    (libdir/name).write_bytes(b)

# Preserve frontend assets at final packaging; append only Dolphin's Sys assets.
shutil.copytree(D/'assets/Sys',M/'assets/Sys',dirs_exist_ok=True)
(M/'assets/dolphin-integration').mkdir(exist_ok=True)
shutil.copy2(R/'source/COPYING',M/'assets/dolphin-integration/COPYING')
if (R/'source/LICENSES').exists():shutil.copytree(R/'source/LICENSES',M/'assets/dolphin-integration/LICENSES',dirs_exist_ok=True)
provenance={'official_version':'2609-7','commit':'5102a0339c2177575378107b76541e47cc52122d','official_apk':'https://dl.dolphin-emu.org/builds/3a/73/dolphin-master-2609-7.apk','source':'https://github.com/dolphin-emu/dolphin','source_rebuilt':False,'integration':'Official Android engine and UI embedded; dependencies and resources relocated; JNI class names preserved; isolated process inside TurboramaStation'}
(M/'assets/dolphin-integration/provenance.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
(R/'class-map.json').write_text(json.dumps(class_map),encoding='utf-8')
(R/'resource-map.json').write_text(json.dumps(resource_map,indent=2),encoding='utf-8')
print('Prepared',len(class_map),'classes and',len(resource_map),'resources; next: bootstrap and native routing.')
