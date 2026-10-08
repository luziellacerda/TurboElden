"""Read declared input-player counts from a pinned official FBNeo source archive.
This is descriptive engine evidence, not verification of a user's ZIP or modes.
"""
import re,json,zipfile,hashlib
from pathlib import Path
ROOT=Path(r'E:\ESTUDO APK\work\station-player-audit-20261008')
COMMIT='f963326de06f479fc9d54b0e03603feaffca393c'
TOKEN=re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*[\s\S]*?\*/|//[^\n]*|.',re.S)
def fields(text):
    parts=[];buf=[];depth=0
    for m in TOKEN.finditer(text):
        t=m.group()
        if t.startswith(('/*','//')):continue
        if t in ('(','{','['):depth+=1
        elif t in (')','}',']'):depth-=1
        if t==',' and depth==0:parts.append(''.join(buf).strip());buf=[]
        else:buf.append(t)
    if buf:parts.append(''.join(buf).strip())
    return parts
def main():
    records=[];unparsed=[];sources={}
    with zipfile.ZipFile(ROOT/'fbneo-source.zip') as z:
        for name in z.namelist():
            if '/src/burn/drv/' not in name or not name.endswith('.cpp'):continue
            data=z.read(name);s=data.decode('utf8',errors='replace');path=name.split('/',1)[1]
            matches=list(re.finditer(r'struct\s+BurnDriver(?:D|X)?\s+(\w+)\s*=\s*\{([\s\S]*?)\n\s*\};',s))
            if not matches:continue
            sources[path]={'sha256':hashlib.sha256(data).hexdigest(),'url':f'https://github.com/finalburnneo/FBNeo/blob/{COMMIT}/{path}'}
            for m in matches:
                p=fields(m[2])
                if len(p)<15 or not re.fullmatch(r'"[a-zA-Z0-9_\-]+"',p[0]) or not p[14].isdigit():
                    unparsed.append({'path':path,'symbol':m[1]});continue
                count=int(p[14])
                if not 1<=count<=16:unparsed.append({'path':path,'symbol':m[1],'count':count});continue
                title=re.match(r'"((?:\\.|[^"\\])*)"',p[5])
                records.append({'driver':p[0][1:-1],'symbol':m[1],'players':count,'title':title[1].split('\\0')[0] if title else p[5],
                    'source':path,'line':s.count('\n',0,m.start())+1,'flags':p[13],'hardware':p[15] if len(p)>15 else ''})
    d={'commit':COMMIT,'kind':'official-emulator-declared-input-players-not-mode-or-rom-qualification','sources':sources,'records':records,'unparsed':unparsed}
    (ROOT/'fbneo-players.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'records':len(records),'unparsed':len(unparsed),'files':len(sources)}))
if __name__=='__main__':main()
