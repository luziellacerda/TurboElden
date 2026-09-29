from pathlib import Path
import json, shlex
ROOT=Path(__file__).resolve().parent
class AC:
 def __init__(self,path):
  self.lines=path.read_text().splitlines();self.i=1;self.materials=[]
  while self.lines[self.i].startswith('MATERIAL'):
   self.materials.append(self.lines[self.i]);self.i+=1
  self.root=self.obj()
 def read(self):
  line=self.lines[self.i];self.i+=1;return line
 def obj(self):
  start=shlex.split(self.read());assert start[0]=='OBJECT';o={'type':start[1],'vertices':[],'surfaces':[],'children':[]}
  while self.i<len(self.lines):
   line=self.read();p=shlex.split(line)
   if not p:continue
   k=p[0]
   if k=='kids':
    o['children']=[self.obj() for _ in range(int(p[1]))];return o
   if k=='numvert': o['vertices']=[list(map(float,self.read().split())) for _ in range(int(p[1]))]
   elif k=='numsurf':
    for _ in range(int(p[1])):
     s={}
     while True:
      q=self.read().split()
      if q[0]=='refs':
       s['refs']=[list(map(float,self.read().split())) for _ in range(int(q[1]))];break
      s[q[0]]=int(q[1],0)
     o['surfaces'].append(s)
   elif k=='data':o['data']=self.read()
   elif k in ('name','texture','url'):o[k]=p[1]
   elif k in ('rot','loc','texrep','texoff'):o[k]=list(map(float,p[1:]))
   elif k in ('crease','subdiv'):o[k]=float(p[1])
   else:o[k]=p[1:]
def flatten(o,parents=()):
 yield o,parents
 for c in o['children']:yield from flatten(c,parents+(o.get('name','?'),))
def report(path):
 a=AC(path);objects=[]
 for o,parents in flatten(a.root):
  v=o['vertices'];s=o['surfaces']
  if not v:continue
  objects.append({'name':o.get('name'), 'parents':parents,'texture':o.get('texture'),'vertices':len(v),'triangles':sum(max(0,len(x['refs'])-2) for x in s),'bbox':[ [min(p[k] for p in v) for k in range(3)], [max(p[k] for p in v) for k in range(3)] ],'loc':o.get('loc'),'rot':o.get('rot')})
 return {'file':str(path.relative_to(ROOT)),'vertex_count':sum(o['vertices'] for o in objects),'triangle_count':sum(o['triangles'] for o in objects),'objects':objects}
if __name__=='__main__':
 data=[report(p) for p in (ROOT/'Models').glob('*.ac')]
 (ROOT/'mesh-inspection.json').write_text(json.dumps(data,indent=2))
 for item in data:
  print(item['file'],item['vertex_count'],item['triangle_count'])
  if 'f16.ac' in item['file']:
   for o in item['objects']:print(o['name'],o['vertices'],o['triangles'],o['bbox'])
