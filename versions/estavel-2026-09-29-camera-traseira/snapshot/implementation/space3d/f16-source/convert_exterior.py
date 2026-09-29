"""Convert licensed FlightGear AC3D exterior to a static glTF 2.0 binary.
Source vertices/UVs preserved; normals rebuilt using AC3D smoothing creases.
No FlightGear executable, flight simulation, or armament logic is imported.
"""
from pathlib import Path
import sys, json, math, struct, shlex, copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'python-libs'))
import numpy as np
from inspect_ac import AC, flatten
ROOT=Path(__file__).resolve().parent
EXCLUDE={'ExternalFlame','InternalFlame','RNLAF_Tailroot','Chute','FanRHighSpeed','FanRHighSpeed.001','FanSpinning','CanopyBackInside','CanopyForwardInside','FuselageLogoLeft','FuselageLogoRight','LogoPilotRight','Rect'}
def rotation(axis,angle):
 a=np.array(axis,dtype=float);a/=np.linalg.norm(a); x,y,z=a; c=math.cos(math.radians(angle));s=math.sin(math.radians(angle));C=1-c
 return np.array([[c+x*x*C,x*y*C-z*s,x*z*C+y*s],[y*x*C+z*s,c+y*y*C,y*z*C-x*s],[z*x*C-y*s,z*y*C+x*s,c+z*z*C]])
def material_parse(line):
 p=shlex.split(line);r={'name':p[1]};i=2
 while i<len(p):
  k=p[i];n=3 if k in ('rgb','amb','emis','spec') else 1;r[k]=list(map(float,p[i+1:i+1+n]));i+=n+1
 return r
model=AC(ROOT/'Models/f16.ac'); meshes=[]; exclusions=[]
def ingest(ac,filename,post=np.eye(4),suffix='',filter_main=False,include_only=None):
 mats=[material_parse(line) for line in ac.materials]
 def walk(o,parent):
  local=np.eye(4)
  if o.get('rot'):local[:3,:3]=np.array(o['rot']).reshape(3,3)
  if o.get('loc'):local[:3,3]=o['loc']
  world=parent@local
  name=o.get('name','object')
  if filter_main and (name=='LandingGear' or name in EXCLUDE or name.startswith(('VstabBand','VstabLogo','Winglogo'))):
   exclusions.append(name);return
  if o['vertices'] and (include_only is None or name in include_only):
   vertices=np.array(o['vertices'],dtype=float)
   if filter_main and name in ('ExternalFrontGearDoor','InternalFrontGearDoor'):
    center=np.array([-2.5,-.805,-.28]);R=rotation([.999843,.007935,-.015871],-91)
    vertices=(vertices-center)@R.T+center
   vertices=(np.c_[vertices,np.ones(len(vertices))]@(post@world).T)[:,:3]
   normals=[];adj=[[] for _ in vertices]
   for si,s in enumerate(o['surfaces']):
    points=vertices[[int(v[0]) for v in s['refs']]];n=np.zeros(3)
    for j in range(1,len(points)-1):n+=np.cross(points[j]-points[0],points[j+1]-points[0])
    length=np.linalg.norm(n); n=n/length if length>1e-12 else np.array([0.,1.,0.]);normals.append(n)
    for ref in s['refs']:adj[int(ref[0])].append(si)
   groups={};crease=math.cos(math.radians(o.get('crease',45)))
   for si,s in enumerate(o['surfaces']):
    if s.get('SURF',0)&15:continue
    mat=s.get('mat',0); rec=groups.setdefault(mat,{'vertices':[],'indices':[],'lookup':{}})
    corners=[]
    for v in s['refs']:
     vi=int(v[0]);n=normals[si]
     if s.get('SURF',0)&16:
      nn=sum((normals[j] for j in adj[vi] if np.dot(n,normals[j])>=crease),start=np.zeros(3));length=np.linalg.norm(nn);n=nn/length if length>1e-12 else n
     uv=np.array(v[1:3])*o.get('texrep',[1,1])+o.get('texoff',[0,0]);uv[1]=1-uv[1]
     row=tuple(np.round(np.r_[vertices[vi],n,uv],8));index=rec['lookup'].get(row)
     if index is None:index=len(rec['vertices']);rec['vertices'].append(row);rec['lookup'][row]=index
     corners.append(index)
    for j in range(1,len(corners)-1):rec['indices']+= [corners[0],corners[j],corners[j+1]]
   for mi,rec in groups.items():
    meshes.append({'name':name+suffix,'source':filename,'material':mats[mi],'texture':((Path(filename).parent/o['texture']).as_posix() if o.get('texture') else None),'vertices':rec['vertices'],'indices':rec['indices'],'doubleSided':any(s.get('SURF',0)&32 for s in o['surfaces'])})
  for c in o['children']:walk(c,world)
 walk(ac.root,np.eye(4))
ingest(model,'Models/f16.ac',filter_main=True)
# PW nozzle petal geometry. Same 16-fold rotational assembly as nozzle.xml.
petals=AC(ROOT/'Models/nozzle-section.ac')
for i in range(16):
 post=np.eye(4);post[:3,:3]=rotation([1,0,0],i*22.5);post[:3,3]=[4.617,0,0]
 ingest(petals,'Models/nozzle-section.ac',post,suffix=f'-{i:02}')
# Exhaust tunnel/fan belongs to the visual model; no effect or animation logic.
ingest(AC(ROOT/'Models/outlet.ac'),'Models/outlet.ac')
# Visible cockpit/pilot geometry, excluding dense kneeboard springs and hidden lower details.
pilot_parts={'L-head','helmet','L-visor','L-face-mask','L-chest','L-collar','L-harness','LL-arm1','LL-arm2','LR-arm1','LR-arm2','LL-wrist','LR-wrist','hand','hand.001','thumb','thumb.001','patchL','patchR','patchC','life-jacket','L-mask-tube'}
ingest(AC(ROOT/'Models/pilot_externalview.ac'),'Models/pilot_externalview.ac',include_only=pilot_parts)
seat_parts={'back-cushion','back-structure','head-rest','main-chute-container','main-chute-container'}
ingest(AC(ROOT/'Models/Cockpit/chair/chair.ac'),'Models/Cockpit/chair/chair.ac',include_only=seat_parts)
cockpit_ac=AC(ROOT/'Models/Cockpit/Main/cockpit.ac')
cockpit_keep={o.get('name') for o,_ in flatten(cockpit_ac.root) if o['vertices']} - {'screws','hud-optic','PedalAdj','floor','up','down','steady','rdy'}
ingest(cockpit_ac,'Models/Cockpit/Main/cockpit.ac',include_only=cockpit_keep)
# Coordinate convention: +Y up, +Z forward, +X aircraft right. Meters preserved.
R=np.array([[0,0,1],[0,1,0],[-1,0,0]],dtype=float)
for m in meshes:
 v=np.array(m['vertices']);v[:,:3]=(v[:,:3]@R.T)/7.5;v[:,3:6]=v[:,3:6]@R.T;m['vertices']=v.astype('<f4')
g={'asset':{'version':'2.0','generator':'Turborama static AC3D visual converter','copyright':'Copyright (C) 2023 Erik Hofman and contributors; GPL-2.0-or-later'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'materials':[],'textures':[],'images':[],'samplers':[{'magFilter':9729,'minFilter':9987,'wrapS':10497,'wrapT':10497}],'bufferViews':[],'accessors':[],'buffers':[]}
bin=bytearray();tex_ids={};mat_ids={};stats=[]
def block(data,target=None):
 while len(bin)%4:bin.append(0)
 start=len(bin);bin.extend(data);view={'buffer':0,'byteOffset':start,'byteLength':len(data)}
 if target:view['target']=target
 g['bufferViews'].append(view);return len(g['bufferViews'])-1
def acc(a,ctype,typ,target,bounds=False):
 a=np.ascontiguousarray(a);view=block(a.tobytes(),target);ob={'bufferView':view,'componentType':ctype,'count':len(a),'type':typ}
 if bounds:ob['min']=a.min(axis=0).tolist();ob['max']=a.max(axis=0).tolist()
 g['accessors'].append(ob);return len(g['accessors'])-1
for m in meshes:
 tex=m['texture'];material=m['material'];key=(tex,material['name'],m['doubleSided']);mid=mat_ids.get(key)
 if mid is None:
  texid=None
  if tex:
   if tex not in tex_ids:
    path=ROOT/tex;im=block(path.read_bytes());g['images'].append({'name':tex,'bufferView':im,'mimeType':('image/jpeg' if path.suffix.lower() in ('.jpg','.jpeg') else 'image/png')});g['textures'].append({'source':len(g['images'])-1,'sampler':0});tex_ids[tex]=len(g['textures'])-1
   texid=tex_ids[tex]
  glass='glass' in material['name'].lower() or 'canopy2' in (tex or '')
  metal='plate' in material['name'].lower() or 'nozzle' in m['name'].lower()
  pbr={'baseColorFactor':material.get('rgb',[1,1,1])+[max(.15,1-material.get('trans',[0])[0])], 'metallicFactor':.8 if metal else (.25 if glass else .1),'roughnessFactor':.10 if glass else (.35 if metal else .60)}
  if texid is not None:pbr['baseColorTexture']={'index':texid}
  ob={'name':material['name']+' '+(tex or ''),'pbrMetallicRoughness':pbr,'doubleSided':bool(m['doubleSided'])}
  if glass:ob['alphaMode']='BLEND';ob['doubleSided']=True
  g['materials'].append(ob);mid=len(g['materials'])-1;mat_ids[key]=mid
 v=m['vertices'];idx=np.array(m['indices'],dtype='<u2');a={'POSITION':acc(v[:,:3],5126,'VEC3',34962,True),'NORMAL':acc(v[:,3:6],5126,'VEC3',34962),'TEXCOORD_0':acc(v[:,6:8],5126,'VEC2',34962)}
 g['meshes'].append({'name':m['name'],'primitives':[{'attributes':a,'indices':acc(idx,5123,'SCALAR',34963),'material':mid}]});g['nodes'].append({'name':m['name'],'mesh':len(g['meshes'])-1});g['scenes'][0]['nodes'].append(len(g['nodes'])-1)
 stats.append({'name':m['name'],'source':m['source'],'vertices':len(v),'triangles':len(idx)//3,'material':mid,'texture':tex,'material_name':material['name'],'glass':('glass' in material['name'].lower() or 'canopy2' in (tex or '')),'bbox':[v[:,:3].min(axis=0).tolist(),v[:,:3].max(axis=0).tolist()]})
g['buffers']=[{'byteLength':len(bin)}];raw=json.dumps(g,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4);bin+=b'\0'*((-len(bin))%4);length=12+8+len(raw)+8+len(bin)
(ROOT/'f16-exterior-original.glb').write_bytes(struct.pack('<III',0x46546c67,2,length)+struct.pack('<II',len(raw),0x4e4f534a)+raw+struct.pack('<II',len(bin),0x004e4942)+bin)
report={'source':'FlightGear NikolaiVChr/f16','license':'GPL-2.0-or-later','coordinate_system':'+Y up; +Z forward; +X right; source meters scaled 1/7.5; original origin retained','modifications':['Static exterior only','Landing gear removed and front gear door closed','Original static flame planes removed','Optional original painted logos removed','USAF tail base retained; RNLAF/parachute geometry removed','Single Pratt & Whitney exhaust nozzle assembled from 16 petal sections','AC3D surface crease normals rebuilt','Visible upper pilot, seat, and cockpit shell included', 'Scale 1/7.5 with original longitudinal origin retained', 'No flight/armament code imported'],'excluded_objects':exclusions,'mesh_count':len(stats),'vertex_count':sum(x['vertices'] for x in stats),'triangle_count':sum(x['triangles'] for x in stats),'objects':stats}
(ROOT/'conversion-report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['objects','excluded_objects']},indent=2));print('GLB bytes',length)
