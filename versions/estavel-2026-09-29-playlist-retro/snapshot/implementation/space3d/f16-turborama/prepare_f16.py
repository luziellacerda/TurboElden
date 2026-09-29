"""Convert the licensed exterior GLB to the native F16 mesh/material atlas.
The raster concept is a look reference only; every aircraft pixel is rendered from geometry.
Corresponding source for this modified GPL-2.0-or-later model is retained alongside it.
"""
from pathlib import Path
import sys,struct,json,io,hashlib,math
P=Path(__file__).resolve().parent;D=P.parent;sys.path.insert(0,str(D/'python-libs'))
import numpy as np
from PIL import Image,ImageDraw,ImageFont
SOURCE=D/'f16-source'/'f16-exterior-original.glb'
raw=SOURCE.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);binary=raw[28+n:]
report=json.loads((SOURCE.parent/'conversion-report.json').read_text())
scale=1.0 if ('scaled 1/7.5' in report.get('coordinate_system','')) else 1/7.5
def accessor(i):
 a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']]
 c={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];dtype={5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]
 start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',np.dtype(dtype).itemsize*c)
 return np.ndarray((a['count'],c),dtype=dtype,buffer=binary,offset=start,strides=(stride,np.dtype(dtype).itemsize)).copy()
W=H=2048
maps={'albedo':Image.new('RGBA',(W,H),(25,30,33,255)),'normal':Image.new('RGBA',(W,H),(128,128,255,255)),'orm':Image.new('RGBA',(W,H),(255,110,100,255)),'emission':Image.new('RGBA',(W,H),(0,0,0,0))}
images=[];tiles=[]
slots=[(0,0,1536),(1536,0,512),(1536,512,512),(1536,1024,512),(1536,1536,512),(0,1536,256),(256,1536,256),(512,1536,256),(768,1536,256),(1024,1536,256),(1280,1536,256)]
for i,meta in enumerate(doc['images']):
 v=doc['bufferViews'][meta['bufferView']];b=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
 im=Image.open(P/'f16-graphite-albedo-v1.png').convert('RGBA') if i==0 else Image.open(io.BytesIO(b)).convert('RGBA');images.append(im)
 assert i<14,'Too many image maps for native atlas'
 special={0:(0,0,1536),2:(1536,0,512),3:(1536,512,512),4:(1536,1024,512)};small=[(j*256,1536,256) for j in range(6)]+[(1536,1536,256),(1792,1536,256),(1536,1792,256),(1792,1792,256)];remaining=[j for j in range(len(doc['images'])) if j not in special];x,y,s=special[i] if i in special else small[remaining.index(i)];pad=3;tile=im.resize((s-pad*2,s-pad*2),Image.Resampling.LANCZOS)
 maps['albedo'].paste(tile,(x+pad,y+pad));tiles.append((x+pad,y+pad,s-pad*2,s-pad*2))
 # Derive fine seam relief for the PBR material from the source's panel drawing.
 a=np.asarray(tile).astype(np.float32)/255.;lum=a[:,:,:3]@np.array([.2126,.7152,.0722])
 dy,dx=np.gradient(lum);normal=np.dstack([-dx*1.8,-dy*1.8,np.ones_like(lum)]);normal/=np.linalg.norm(normal,axis=2,keepdims=True)
 normal=np.dstack([np.clip(normal*.5+.5,0,1),np.ones_like(lum)])
 maps['normal'].paste(Image.fromarray((normal*255).astype('uint8')),(x+pad,y+pad))
 # Material roughness carries fine variation without baked illumination.
 rng=np.random.default_rng(1600+i);grain=rng.normal(0,1.6,lum.shape)
 orm=np.stack([np.clip(245-((dx*dx+dy*dy)**.5)*80,110,255),np.clip(102+lum*24+grain,65,170),np.full_like(lum,105),np.full_like(lum,255)],axis=2).astype('uint8')
 maps['orm'].paste(Image.fromarray(orm),(x+pad,y+pad))
 # Pad atlas tile edges to prevent color bleeding when sampling.
 for name in maps:
  if name=='emission':continue
  m=maps[name];m.paste(m.crop((x+pad,y+pad,x+pad+1,y+s-pad)).resize((pad,s-2*pad)),(x,y+pad));m.paste(m.crop((x+s-pad-1,y+pad,x+s-pad,y+s-pad)).resize((pad,s-2*pad)),(x+s-pad,y+pad))
  m.paste(m.crop((x,y+pad,x+s,y+pad+1)).resize((s,pad)),(x,y));m.paste(m.crop((x,y+s-pad-1,x+s,y+s-pad)).resize((s,pad)),(x,y+s-pad))
# Typography is generated from a locally installed font, no font file embedded.
font=ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf',176);box=font.getbbox('TURBORAMA')
mask=Image.new('L',(box[2]-box[0]+12,box[3]-box[1]+12),0);ImageDraw.Draw(mask).text((6-box[0],6-box[1]),'TURBORAMA',font=font,fill=255)
mask=mask.resize((1024,192),Image.Resampling.LANCZOS);mark=Image.new('RGBA',mask.size,(0,0,0,0));mark.putalpha(mask)
maps['emission'].paste(mark,(0,1824));mask.save(P/'wordmark.png')
palette={}
def classify(name,material):
 s=(name+' '+material.get('name','')).lower()
 if 'glass' in s or ('canopy' in s and 'frame' not in s and 'inner' not in s):return 2
 if any(x in s for x in ['nozzle','outlet','exhaust','fanr','engine']):return 3
 if any(x in s for x in ['pilot','cockpit','seat','console','panel','intake']):return 4
 if 'lightred' in s:return 5
 if 'lightgreen' in s:return 6
 if any(x in s for x in ['poslight','lightwhite','formationlight']):return 7
 return 1
def split_periodic_uv(pos,norm,uv,idx,material):
 """Clip triangles at every REPEAT/MIRRORED_REPEAT boundary before atlasing.
 New corners interpolate all source attributes together, so position/normal/UV
 describe the same surface point. Boundary vertices remain distinct at UV=0/1.
 Untextured primitives and entirely nonrepeating UVs retain their original data.
 """
 tx=material.get('pbrMetallicRoughness',{}).get('baseColorTexture')
 if tx is None:return pos,norm,uv,idx
 texture=doc['textures'][tx['index']]
 sampler=doc.get('samplers',[])[texture['sampler']] if 'sampler' in texture else {}
 wraps=[sampler.get('wrapS',10497),sampler.get('wrapT',10497)]
 assert np.isfinite(uv).all(),'Nonfinite source UV'
 periodic=[mode in (10497,33648) for mode in wraps]
 if np.all(uv>=0.) and np.all(uv<=1.):return pos,norm,uv,idx
 # Clamped axes need no subdivision. Periodic axes must never be clamped.
 source=np.column_stack([pos,norm,uv]).astype(np.float64)
 for axis in range(2):
  if not periodic[axis]:source[:,6+axis]=np.minimum(1.,np.maximum(0.,source[:,6+axis]))
 rows=[];out_indices=[];lookup={};epsilon=1e-10
 def clip(poly,axis,bound,keep_above):
  if not poly:return []
  result=[];previous=poly[-1]
  previous_inside=(previous[axis]>=bound-epsilon) if keep_above else (previous[axis]<=bound+epsilon)
  for current in poly:
   inside=(current[axis]>=bound-epsilon) if keep_above else (current[axis]<=bound+epsilon)
   if inside!=previous_inside:
    denominator=current[axis]-previous[axis]
    if abs(denominator)>epsilon:
     t=(bound-previous[axis])/denominator
     cut=previous+(current-previous)*t;cut[axis]=bound;result.append(cut)
   if inside:result.append(current)
   previous=current;previous_inside=inside
  clean=[]
  for row in result:
   if not clean or np.max(np.abs(row-clean[-1]))>epsilon:clean.append(row)
  if len(clean)>1 and np.max(np.abs(clean[0]-clean[-1]))<=epsilon:clean.pop()
  return clean
 def register(row,cell):
  row=row.copy()
  for axis in range(2):
   if periodic[axis]:
    value=row[6+axis]-cell[axis]
    if wraps[axis]==33648 and cell[axis]%2:value=1.-value
    assert -1e-7<=value<=1.+1e-7,(value,cell)
    row[6+axis]=min(1.,max(0.,value)) # Numeric boundary cleanup only.
  length=np.linalg.norm(row[3:6])
  if length>1e-12:row[3:6]/=length
  key=tuple(np.round(row,8));index=lookup.get(key)
  if index is None:
   index=len(rows);lookup[key]=index;rows.append(row)
  return index
 for triangle in idx.reshape(-1,3):
  polygon=source[triangle]
  cells=[]
  for axis in range(2):
   if not periodic[axis]:cells.append(range(1));continue
   low=polygon[:,6+axis].min();high=polygon[:,6+axis].max()
   first=math.floor(low+epsilon);last=max(first,math.ceil(high-epsilon)-1)
   cells.append(range(first,last+1))
  assert len(cells[0])*len(cells[1])<=4096,'Source triangle spans too many texture repetitions'
  for ucell in cells[0]:
   for vcell in cells[1]:
    cell=(ucell,vcell);poly=[row.copy() for row in polygon]
    for axis in range(2):
     if periodic[axis]:
      poly=clip(poly,6+axis,cell[axis],True)
      poly=clip(poly,6+axis,cell[axis]+1.,False)
    if len(poly)<3:continue
    for i in range(1,len(poly)-1):
     tri=(poly[0],poly[i],poly[i+1])
     if np.linalg.norm(np.cross(tri[1][:3]-tri[0][:3],tri[2][:3]-tri[0][:3]))<1e-14:continue
     out_indices.extend(register(row,cell) for row in tri)
 assert rows and len(rows)<65536,'Clipped primitive exceeds GLES2 index capacity'
 data=np.asarray(rows,dtype=np.float32)
 return data[:,:3],data[:,3:6],data[:,6:8],np.asarray(out_indices,dtype=np.uint32)

def material_uv(m,uv):
 pbr=m.get('pbrMetallicRoughness',{});tx=pbr.get('baseColorTexture')
 if tx:
  i=doc['textures'][tx['index']]['source'];x,y,w,h=tiles[i]
  assert np.all(uv>=-1e-7) and np.all(uv<=1.+1e-7),'Atlas UV must be split into texture cells first'
  return (uv*np.array([w-1,h-1])+np.array([x+.5,y+.5]))/np.array([W,H])
 color=tuple(round(c*255) for c in pbr.get('baseColorFactor',[.18,.20,.22,1]))
 if color not in palette:
  j=len(palette);assert j<192
  x=1056+(j%24)*16;y=1824+(j//24)*16
  ImageDraw.Draw(maps['albedo']).rectangle((x,y,x+15,y+15),fill=color)
  palette[color]=((x+8)/W,(y+8)/H)
 return np.tile(palette[color],(len(uv),1))
parts=[]
for mesh in doc['meshes']:
 for pr in mesh['primitives']:
  m=doc['materials'][pr.get('material',0)];typ=classify(mesh.get('name',''),m)
  pos=accessor(pr['attributes']['POSITION'])*scale;norm=accessor(pr['attributes']['NORMAL']);uv=accessor(pr['attributes']['TEXCOORD_0']);idx=accessor(pr['indices']).flatten().astype('uint32')
  pos,norm,uv,idx=split_periodic_uv(pos,norm,uv,idx,m)
  parts.append((typ,mesh.get('name',''),pos,norm,material_uv(m,uv),idx))
parts.sort(key=lambda v:v[0]==2) # All glass follows all opaque geometry.
verts=[];indices=[];objects=[];offset=0;opaque_count=0
for typ,name,pos,norm,uv,idx in parts:
 tan=np.zeros_like(pos);bit=np.zeros_like(pos)
 for tri in idx.reshape(-1,3):
  a,b,c=tri;edge1=pos[b]-pos[a];edge2=pos[c]-pos[a];d1=uv[b]-uv[a];d2=uv[c]-uv[a];det=d1[0]*d2[1]-d1[1]*d2[0]
  if abs(det)<1e-12:continue
  t=(edge1*d2[1]-edge2*d1[1])/det;bvec=(edge2*d1[0]-edge1*d2[0])/det
  for k in tri:tan[k]+=t;bit[k]+=bvec
 norm/=np.maximum(np.linalg.norm(norm,axis=1,keepdims=True),1e-8)
 tan-=norm*np.sum(tan*norm,axis=1,keepdims=True);bad=np.linalg.norm(tan,axis=1)<1e-8
 tan[bad]=np.cross(norm[bad],np.array([0,1,0]));bad=np.linalg.norm(tan,axis=1)<1e-8;tan[bad]=np.cross(norm[bad],np.array([1,0,0]));tan/=np.maximum(np.linalg.norm(tan,axis=1,keepdims=True),1e-8)
 hand=np.where(np.sum(np.cross(norm,tan)*bit,axis=1)<0,-1.,1.)*typ
 verts.append(np.column_stack([pos,norm,tan,hand,uv]).astype('<f4'));indices.append(idx+offset)
 objects.append({'name':name,'kind':typ,'vertex_offset':offset,'vertices':len(pos),'triangles':len(idx)//3,'bbox':[pos.min(axis=0).tolist(),pos.max(axis=0).tolist()]})
 offset+=len(pos)
 if typ!=2:opaque_count+=len(idx)
assert offset<65536,offset
vb=np.concatenate(verts).tobytes();ib=np.concatenate(indices).astype('<u2').tobytes()
(D/'ship.vertices').write_bytes(vb);(D/'ship.indices').write_bytes(ib)
header=['// Derived F-16 visual model, GPL-2.0-or-later. See space3d/NOTICE.md and f16-source/.',f'static constexpr int shipTextureWidth={W},shipTextureHeight={H};',f'static constexpr unsigned shipOpaqueIndices={opaque_count};']
def embed(name,data):header.append('alignas(16) static const unsigned char '+name+'[]={\n'+',\n'.join(','.join(str(x) for x in data[i:i+64]) for i in range(0,len(data),64))+'\n};')
embed('shipVertices',vb);embed('shipIndices',ib)
for name,im in maps.items():im.save(D/(name+'.png'));embed('ship'+name.title(),im.tobytes())
(D.parent/'space3d_assets.h').write_text('\n'.join(header),encoding='utf-8')
meta={'model':'F-16 TURBORAMA','source':'https://github.com/NikolaiVChr/f16','source_commit':json.loads((SOURCE.parent/'source-manifest.json').read_text())['commit'],'license':'GPL-2.0-or-later','source_glb_sha256':hashlib.sha256(raw).hexdigest(),'vertices':offset,'triangles':len(ib)//6,'maps':4,'texture_size':[W,H],'native_tangent_w':'sign = tangent handedness; abs = material class','model_scale_applied':scale,'brand_tile':[0,1824,1024,192],'objects':objects,'nozzles':[{'position':[0,0,-.70681],'exit_position':[0,0,-.72181064],'direction':[0,0,-1],'radius':.043}],'reference_image_is_geometry':False}
(D/'model-manifest.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in meta.items() if k!='objects'},indent=2))
