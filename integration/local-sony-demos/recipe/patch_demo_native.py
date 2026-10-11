"""Sony platform artwork fallback only; retains every R128 render method."""
import hashlib

ANCHOR='  if(art)strAssign(item+0xc8,art->path);\n'
ADDITION='''  if(!art&&(presentationKeyEqual(key,"Playstation 3")||presentationKeyEqual(key,"Playstation 4"))){
   for(B*source=at<B*>(real,0x88);source<at<B*>(real,0x90);source+=0xe8){
    if(strcmp(strData(source+0x60),key)==0&&*strData(source+0xc8)){strAssign(item+0xc8,strData(source+0xc8));break;}
   }
  }
'''

def patch(raw:bytes)->bytes:
    text=raw.decode('utf-8')
    if text.count(ANCHOR)!=1 or ADDITION in text:raise ValueError('R128 platform artwork anchor changed')
    result=text.replace(ANCHOR,ANCHOR+ADDITION,1).encode('utf-8')
    if result.decode('utf-8').replace(ADDITION,'',1).encode('utf-8')!=raw:raise ValueError('Native inverse mismatch')
    return result

def verify(original:bytes,result:bytes)->dict:
    if patch(original)!=result:raise ValueError('Unexpected native delta')
    return {'changedMethods':['syncModel'],'exactInverse':True,
            'renderMethodsChanged':False,'commandRoutesChanged':False,
            'originalSourceSha256':hashlib.sha256(original).hexdigest(),
            'sourceSha256':hashlib.sha256(result).hexdigest()}
