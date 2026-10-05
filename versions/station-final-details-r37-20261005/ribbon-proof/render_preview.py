"""Rasterize the actual mesh triangles for a local design proof (no app screenshot)."""
from pathlib import Path
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE=Path(__file__).resolve().parent
def rgba(n): return np.array([(n>>24)&255,(n>>16)&255,(n>>8)&255,n&255],dtype=float)
def render(frame):
    size=860; pad=28
    im=np.zeros((size,size,3),dtype=float)
    yy,xx=np.mgrid[0:size,0:size]
    base=18+((xx+yy)/size)*12
    im[:]=np.stack([base*.7,base,base*.93],axis=-1)
    inside=(xx>=pad)&(yy>=pad)&(xx<pad+800)&(yy<pad+800)
    cover=np.stack([45+xx*.12,38+yy*.07,66+xx*.02],axis=-1)
    im[inside]=cover[inside]
    for i in range(2,len(frame['vertices'])):
        points=frame['vertices'][i-2:i+1]
        p=np.array([[v[0]+pad,v[1]+pad] for v in points]); colors=np.array([rgba(v[2]) for v in points])
        den=(p[1,1]-p[2,1])*(p[0,0]-p[2,0])+(p[2,0]-p[1,0])*(p[0,1]-p[2,1])
        if abs(den)<1e-6: continue
        lo=np.maximum(np.floor(p.min(axis=0)).astype(int),0);hi=np.minimum(np.ceil(p.max(axis=0)).astype(int)+1,size)
        y,x=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];x=x+.5;y=y+.5
        w0=((p[1,1]-p[2,1])*(x-p[2,0])+(p[2,0]-p[1,0])*(y-p[2,1]))/den
        w1=((p[2,1]-p[0,1])*(x-p[2,0])+(p[0,0]-p[2,0])*(y-p[2,1]))/den
        w2=1-w0-w1;mask=(w0>=0)&(w1>=0)&(w2>=0)
        src=w0[:,:,None]*colors[0]+w1[:,:,None]*colors[1]+w2[:,:,None]*colors[2]
        alpha=src[:,:,3:4]/255;area=im[lo[1]:hi[1],lo[0]:hi[0]]
        out=area*(1-alpha)+src[:,:,:3]*alpha;area[mask]=out[mask]
    result=Image.fromarray(np.clip(im,0,255).astype('uint8'),'RGB')
    # The production word is rendered by the original native font; this approximation
    # only shows contrast and placement. Native font sizing remains unchanged.
    label=Image.new('RGBA',(450,88));draw=ImageDraw.Draw(label)
    font=ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf',54)
    draw.text((225,44),'INSTALADO',font=font,fill='#F5FFF9',anchor='mm')
    rotated=label.rotate(45,resample=Image.Resampling.BICUBIC,expand=True)
    cx=pad+152;cy=pad+152
    result.paste(rotated,(int(cx-rotated.width/2),int(cy-rotated.height/2)),rotated)
    return result.crop((0,0,490,490))
frames=json.loads((HERE/'geometry.json').read_text())
proof=Image.new('RGB',(490*3,490+42),'#08110e');d=ImageDraw.Draw(proof)
for column,index in enumerate((0,2,3)):
    proof.paste(render(frames[index]),(490*column,42));d.text((490*column+14,14),f"GEOMETRY PREVIEW / {frames[index]['time']} ms",fill='#cef8de')
proof.save(HERE/'ribbon-proof.png')
print(HERE/'ribbon-proof.png')
