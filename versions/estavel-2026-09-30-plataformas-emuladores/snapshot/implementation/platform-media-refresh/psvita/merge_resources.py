from pathlib import Path
import copy, json, re, shutil, xml.etree.ElementTree as ET

R=Path(r'E:\ESTUDO APK\work\native-carousel\implementation\platform-media-refresh\psvita')
D=R/'donor-decoded'; F=R/'frontend-decoded'; M=R/'merged'
A='{http://schemas.android.com/apk/res/android}'
AUTO='{http://schemas.android.com/apk/res-auto}'
ET.register_namespace('android',A[1:-1]); ET.register_namespace('app',AUTO[1:-1])
def prefix(name):return 'tv_'+name.replace('$','private_')
shutil.copytree(F,M,dirs_exist_ok=True)
front_classes=set(json.loads((R/'base-classes.json').read_text()))
def platform_class(name):
    return name.startswith(('java/','javax/','dalvik/','org/xml/','org/w3c/')) or (name.startswith('android/') and not name.startswith('android/support/'))
class_map={}
for root in D.glob('smali*'):
    for f in root.rglob('*.smali'):
        old=f.relative_to(root).as_posix()[:-6]
        if old.startswith(('org/vita3k/',)) or platform_class(old):new=old
        elif old.startswith('org/libsdl/'):new=old.replace('org/libsdl/','org/vtsdlx/',1)
        elif old.startswith('androidx/'):new='tvita3kc/'+old[9:]
        else:new='tvita3kc/shaded/'+old
        class_map[old]=new
native_classes=set()
for f in D.rglob('*.smali'):
 text=f.read_text('utf-8')
 if re.search(r'^\.method .*\bnative\b',text,re.M):
  name=re.search(r'^\.class (?:.* )?(L[^;]+;)',text,re.M)[1][1:-1]
  if not name.startswith(('org/libsdl/','androidx/')):
   assert name not in front_classes, 'Native class collision: '+name
   class_map[name]=name;native_classes.add(name)
(R/'native-classes.json').write_text(json.dumps(sorted(native_classes)))
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
        if m[3] and m[3]!='org.vita3k.emulator:':return m[0]
        name=names.get((m[4],m[5]));return m[1]+m[2]+m[4]+'/'+name if name else m[0]
    s=resource_ref.sub(sub,s)
    s=re.sub(r'\?([A-Za-z_][\w.]*)',lambda m:'?'+names.get(('attr',m[1]),m[1]),s)
    return hex_ref.sub(lambda m:f'0x{idmap.get(int(m[0],16),int(m[0],16)):08x}',s)

def xml_node(e,values=False,parent=None):
    if e.tag in dot_map and ("." in e.tag or e.tag not in {"item","style","resources","string","id","array","attr","bool","integer","color","dimen","plurals","font","menu","selector","shape","vector","path","group","view"}):e.tag=dot_map[e.tag]
    for key,val in list(e.attrib.items()):
        newkey=key
        if key.startswith(AUTO):newkey=AUTO+'tv_'+key[len(AUTO):]
        if key.startswith('{http://schemas.android.com/apk/res/org.vita3k.emulator}'):
            newkey=AUTO+'tv_'+key.split('}',1)[1]
        val=refs(val)
        if key in ("class",A+"name") and not values and val in dot_map:val=dot_map[val]
        if key=='name' and values:
            if parent=='resources':val=prefix(val)
            elif parent=='style' and not val.startswith('android:'):val='tv_'+val
        if key=='parent' and e.tag=='style' and val and not val.startswith(('@','android:')):val='tv_'+val
        if key.endswith('constraint_referenced_ids'):
            val=','.join(names.get(('id',x.strip()),x.strip()) for x in val.split(','))
        if newkey!=key:del e.attrib[key]
        e.attrib[newkey]=val
    if e.text:
        e.text=refs(e.text)
        if "." in e.text.strip() and e.text.strip() in dot_map:e.text=dot_map[e.text.strip()]
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
 'SPIRV-Tools-shared':'X360V-Tools-shared',
 'androidx.graphics.path':'tvita3kc.graphics.path',
 'datastore_shared_counter':'x360store_shared_counter',
 'file_redirect_hook':'vile_redirect_hook',
 'gsl_alloc_hook':'vsl_alloc_hook',
 'hook_impl':'vhok_impl',
 'main_hook':'vita_hook',
 'c++_shared':'v3c_shared',
}
for n,root in enumerate(sorted(D.glob('smali*')),start=23):
    target=M/f'smali_classes{n}';target.mkdir(exist_ok=True)
    for f in root.rglob('*.smali'):
        old=f.relative_to(root).as_posix()[:-6]
        if platform_class(old):
            obsolete=target/('tvita3kc/shaded/'+old+'.smali')
            if obsolete.is_file():obsolete.unlink()
            if old in front_classes:continue
        dest=target/(class_map[old]+'.smali');dest.parent.mkdir(parents=True,exist_ok=True)
        s=f.read_text(encoding='utf-8')
        s=descriptor.sub(lambda m:'L'+class_map.get(m[1],m[1])+';',s)
        s=hex_ref.sub(lambda m:f'0x{idmap.get(int(m[0],16),int(m[0],16)):08x}',s)
        s=re.sub(r'const/high16(\s+\w+,\s+)(0x[0-9a-fA-F]+)',lambda m:('const' if int(m[2],16)&65535 else 'const/high16')+m[1]+m[2],s)
        def string_sub(m):
            val=m[2]
            if "." in val or "/" in val:val=dot_map.get(val,class_map.get(val,val))
            if val in library_names:val=library_names[val]
            if val=='org.vita3k.emulator':val='org.emulationstation.frontend'
            if val.startswith('org.vita3k.emulator.') and val.endswith(('provider','romlibrary','androidx-startup')):val=val.replace('org.vita3k.emulator.','org.emulationstation.frontend.psvita.',1)
            if val=='ARMSX2':val='TURBORAMA_PS2'
            if val=='_preferences':val='_ps2_preferences'
            return m[1]+val+m[3]
        s=const_string.sub(string_sub,s)
        unrelocated=[m[1] for m in descriptor.finditer(s) if m[1] in class_map and class_map[m[1]]!=m[1]]
        assert not unrelocated,(f,unrelocated[:3])
        # Startup tests an unprefixed resource string; both sides retain the same marker.
        dest.write_text(s,encoding='utf-8')


manifest=ET.parse(M/'AndroidManifest.xml');app=manifest.getroot().find('application')
app.set(A+'allowNativeHeapPointerTagging','false')
donor=ET.parse(D/'AndroidManifest.xml').getroot();donor_app=donor.find('application')
for e in donor_app:
 if e.tag not in ['activity','provider','uses-library','service']:continue
 name=e.get(A+'name','')
 if 'shortcuts.' in name or 'ShortcutActivity' in name or 'profileinstaller' in name:continue
 child=copy.deepcopy(e);xml_node(child)
 if e.tag != 'uses-library':child.set(A+'process',':psvita');child.set(A+'exported','false')
 if e.tag=='service':child.set(A+'exported','false')
 if name.endswith('EmulatorHostActivity'):child.set(A+'process',':psvita')
 if e.tag=='activity':
  child.set(A+'enableOnBackInvokedCallback','false');child.set(A+'taskAffinity','org.emulationstation.frontend')
  child.set(A+'theme',refs(e.get(A+'theme',donor_app.get(A+'theme'))))
  child.set(A+'launchMode','standard')
  child.attrib.pop(A+'parentActivityName',None)
  for x in list(child):
   if x.tag=='intent-filter':child.remove(x)
 if e.tag=='provider':child.set(A+'authorities',child.get(A+'authorities','').replace('org.vita3k.emulator.','org.emulationstation.frontend.psvita.'))
 app.append(child)
permissions={e.get(A+'name') for e in manifest.getroot().findall('uses-permission')}
for e in donor.findall('uses-permission'):
 name=e.get(A+'name','')
 if name in permissions or name in ['android.permission.REQUEST_INSTALL_PACKAGES'] or name.startswith('org.vita3k.emulator.'):continue
 manifest.getroot().append(copy.deepcopy(e))
# DocumentsProvider.attachInfo requires export, URI grants and the system-only permission.
# Include inherited Wii U components when assembling the later Xbox revision.
for provider in app.findall('provider'):
 if provider.get(A+'name') in ('info.cemu.cemu.provider.DocumentsProvider','org.vita3k.emulator.DocumentsProvider'):
  provider.set(A+'exported','true')
  provider.set(A+'grantUriPermissions','true')
  provider.set(A+'permission','android.permission.MANAGE_DOCUMENTS')
manifest.write(M/'AndroidManifest.xml',encoding='utf-8',xml_declaration=True)
libdir=M/'lib/arm64-v8a';libdir.mkdir(parents=True,exist_ok=True)
replacements={b'androidx/':b'tvita3kc/',b'org/libsdl/':b'org/vtsdlx/'}
for old,new in library_names.items():replacements[('lib'+old+'.so').encode()]=('lib'+new+'.so').encode()
for f in (D/'lib/arm64-v8a').glob('*.so'):
 b=f.read_bytes()
 for old,new in replacements.items():
  assert len(old)==len(new),(old,new)
  b=b.replace(old,new)
 name='lib'+library_names.get(f.name[3:-3],f.name[3:-3])+'.so'
 (libdir/name).write_bytes(b)
shutil.copytree(D/'assets',M/'assets',dirs_exist_ok=True)

(R/'class-map.json').write_text(json.dumps(class_map))
(R/'resource-map.json').write_text(json.dumps(resource_map))
print('Prepared Vita classes:',len(class_map),'resources:',len(idmap))
