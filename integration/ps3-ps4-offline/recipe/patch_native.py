"""One offline command opt-in, with an exact inverse of the current R124 source."""
from pathlib import Path
import argparse, hashlib, json

SOURCE_SHA='97315bc41c9ea6ab6b7c4673c45352fb0422139cc70f2cd4e545d260b42598fb'
ANCHOR='static UiString gamecubeCommandHook(const void* folder){\n const char*key=strData(folder);\n'
PREFIX='#include "offline_routes.h"\n'
ADDITION=' {UiString offline={};if(stationOfflineSonyCommand(key,&offline))return offline;}\n'

def patch(raw):
 if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError('Exact current R124 native command source required')
 text=raw.decode('utf-8')
 if text.count(ANCHOR)!=1 or PREFIX in text or ADDITION in text:raise ValueError('Native route anchor changed')
 result=text.replace(ANCHOR,PREFIX+ANCHOR+ADDITION,1).encode('utf-8')
 if result.decode('utf-8').replace(PREFIX,'',1).replace(ADDITION,'',1).encode('utf-8')!=raw:raise ValueError('Other native methods changed')
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
 raw=a.source.read_bytes();out=patch(raw);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_bytes(out)
 record={'sourceSha256':SOURCE_SHA,'patchedSha256':hashlib.sha256(out).hexdigest(),'changedMethods':['gamecubeCommandHook'],'exactInverse':True,'graphicsMethodsChanged':False,'onlineMethodsChanged':False}
 a.receipt.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record))
if __name__=='__main__':main()
