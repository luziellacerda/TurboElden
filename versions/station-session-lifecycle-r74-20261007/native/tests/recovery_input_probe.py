"""Test exact R73/R74 wait fragments with a modeled Android input queue.
Twelve seconds are simulated; this is not a real Android ANR or gameplay test.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/('sources' if (ROOT/'sources').exists() else 'source')
BASE=Path(r'E:\R73fixed\RetroArch-69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576')

def sha(x):return hashlib.sha256(x).hexdigest()

PRE=r'''
#include <stdbool.h>
#include <stdio.h>
static bool waiting=true,human_quit,shutdown;
static int pending,acked,polls,frames,sleeps,protocol_polls;
static bool station_recovery_waiting(void){return waiting;}
static bool station_recovery_active(void){return true;}
static void input_driver_poll(void){polls++;acked+=pending;pending=0;if(human_quit)shutdown=true;}
static bool station_netplay_recovery_poll(void){protocol_polls++;return true;}
static void station_recovery_confirm(bool w,bool c){(void)w;(void)c;}
static void retro_sleep(int ms){sleeps+=ms;}
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL input line%d %s pending=%d acked=%d\n",__LINE__,#x,pending,acked);return 2;}}while(0)
'''
POST=r'''
int main(void){
   for(int i=0;i<240;i++){pending+=10;CHECK(iterate()==0);}
   CHECK(pending==0);CHECK(acked==2400);CHECK(frames==0);CHECK(sleeps==12000);CHECK(protocol_polls==240);
   human_quit=true;pending=1;CHECK(iterate()==-1);CHECK(pending==0);CHECK(frames==0);
   /* Normal game execution still polls through its core path, only once. */
   waiting=false;human_quit=false;shutdown=false;int previous=polls;pending=1;
   CHECK(iterate()==0);CHECK(frames==1);CHECK(polls==previous+1);CHECK(pending==0);
   puts("PASS modeled 12s recovery wait: ACK2400, no gameframes; human quit handled; normal frame unchanged");return 0;
}
'''

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    out=args.out.resolve();assert str(out).startswith('E:\\');out.mkdir(parents=True,exist_ok=True)
    results=[]
    for label,tree in [('baseline',BASE),('candidate',SOURCE)]:
        source=(tree/'runloop.c').read_text(encoding='utf8')
        start=source.index('#if defined(ANDROID) && defined(HAVE_NETWORKING)\n   if(station_recovery_waiting())')
        end=source.index('#endif',start)
        wait=source[source.index('\n',start)+1:end]
        pre=''
        if label=='candidate':
            match=re.search(r'   if \(station_recovery_waiting\(\)\)\n      input_driver_poll\(\);',source)
            assert match and match.start()<source.index('switch ((enum runloop_state_enum)runloop_check_state(')
            pre=match.group(0)
        # Model the normal state check and normal core input callback only.
        c=PRE+'\nstatic int iterate(void){\n'+pre+'\nif(shutdown)return -1;\n'+wait+'\ninput_driver_poll();frames++;return 0;\n}\n'+POST
        src=out/(label+'-input.c');exe=out/(label+'-input.exe');src.write_text(c,encoding='utf8')
        build=subprocess.run([r'C:\Program Files\LLVM\bin\clang.exe','-std=c11',str(src),'-o',str(exe)],capture_output=True,text=True)
        assert build.returncode==0,build.stderr
        run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5)
        assert run.returncode==(2 if label=='baseline' else 0),(label,run.stdout,run.stderr)
        results.append({'label':label,'sourceSHA256':sha((tree/'runloop.c').read_bytes()),'waitFragmentSHA256':sha(wait.encode()),
                        'pollFragmentSHA256':sha(pre.encode()),'exitCode':run.returncode,'stdout':run.stdout.strip(),'stderr':run.stderr.strip()})
    assert results[0]['waitFragmentSHA256']==results[1]['waitFragmentSHA256'],'Recovery pump behavior changed'
    receipt={'scope':__doc__,'testRecipeSHA256':sha(Path(__file__).read_bytes()),'results':results,
             'androidTested':False,'realGameFramesTested':False}
    for path in (out/'recovery-input-result.json',ROOT/'tests/recovery-input-result.json'):
        path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
