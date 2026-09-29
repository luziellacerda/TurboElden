"""Convert the licensed Space Pirates glTF asset to fixed native GPU buffers.
Modified for Turborama: hull only, centered scale, 1024px material maps; no game code.
"""
from pathlib import Path
import struct, json, io, hashlib
from PIL import Image
P=Path(__file__).resolve().parent
b=(P/'valkyrie_mesh.glb').read_bytes()
n=struct.unpack_from('<I',b,12)[0]; doc=json.loads(b[20:20+n]); binary=b[28+n:]
def accessor(i):
    a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']]
    count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    fmt={5123:'H',5126:'f'}[a['componentType']]*count;size=struct.calcsize('<'+fmt)
    start=v.get('byteOffset',0)+a.get('byteOffset',0); stride=v.get('byteStride',size)
    return [struct.unpack_from('<'+fmt,binary,start+j*stride) for j in range(a['count'])]
primitive=doc['meshes'][0]['primitives'][0];attrs=primitive['attributes']
pos=accessor(attrs['POSITION']);normal=accessor(attrs['NORMAL']);uv=accessor(attrs['TEXCOORD_0']);tan=accessor(attrs['TANGENT'])
vertices=b''.join(struct.pack('<12f',*(tuple(x/.15530242 for x in p)+n+t+u)) for p,n,t,u in zip(pos,normal,tan,uv))
indices=b''.join(struct.pack('<H',i[0]) for i in accessor(primitive['indices']))
(P/'ship.vertices').write_bytes(vertices);(P/'ship.indices').write_bytes(indices)
header=['// Converted from BabylonJS/SpacePirates, Apache-2.0. See space3d/NOTICE.md.']
def embed(name,data):
    header.append('alignas(16) static const unsigned char '+name+'[]={\n'+',\n'.join(','.join(str(x) for x in data[i:i+32]) for i in range(0,len(data),32))+'\n};')
embed('shipVertices',vertices);embed('shipIndices',indices)
names=['normal','orm','emission','albedo']
for i,name in enumerate(names):
    image=doc['images'][doc['textures'][i]['source']];v=doc['bufferViews'][image['bufferView']]
    raw=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
    im=Image.open(io.BytesIO(raw)).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
    im.save(P/(name+'.png'));embed('ship'+name.title(),im.tobytes())
(P.parent/'space3d_assets.h').write_text('\n'.join(header),encoding='utf-8')
metadata={'source':'https://github.com/BabylonJS/SpacePirates','commit':(P/'upstream-commit.txt').read_text(encoding='utf-8-sig').strip(),'license':'Apache-2.0','source_sha256':hashlib.sha256(b).hexdigest(),'vertices':len(pos),'triangles':len(indices)//6,'textures':4,'texture_size':1024,'nozzles':[{'position':[x/.15530242 for x in n['translation']],'scale':n.get('scale',[1])[0]} for n in doc['nodes'] if 'thruster_' in n['name']]}
(P/'model-manifest.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8');print(json.dumps(metadata,indent=2))
