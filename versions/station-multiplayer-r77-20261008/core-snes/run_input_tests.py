"""Compile real Mercury inputPoll and Multitap data() methods into a no-ROM host fixture."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from datetime import datetime,timezone

HERE=Path(__file__).resolve().parent
BASE=Path(r'E:\ESTUDO APK\work\station-netplay-20261004\upstream\libretro--bsnes-mercury-79d7f9de218b')
WORK=Path(r'E:\ESTUDO APK\work\station-multiplayer-r77-20261008\snes')
CLANG=Path(r'C:\Program Files\LLVM\bin\clang++.exe')
def sha(data):return hashlib.sha256(data).hexdigest()
def extract(text,signature):
    start=text.index(signature);level=0
    for i in range(text.index('{',start),len(text)):
        if text[i]=='{':level+=1
        elif text[i]=='}':
            level-=1
            if level==0:return text[start:i+1]
    raise AssertionError(signature)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--work',type=Path,default=WORK);a=p.parse_args()
    before=(BASE/'target-libretro/libretro.cpp').read_bytes();after=(a.work/'source/target-libretro/libretro.cpp').read_bytes()
    assert sha(before)=='90bfb5826f9e2e85a05d11137eeeebdbc05359b7eba3632d4296e87c5dae007a'
    assert sha(after)=='e0d95df5f51a215457a9dc693d1797450e1e41179b96229b04c738a0277fa3c7'
    controller=(BASE/'sfc/controller/multitap/multitap.cpp').read_bytes();assert sha(controller)=='f294c21171175e5b87d548dd48143bccb7253b812274a1c8dce8a2be69610968'
    header=(BASE/'sfc/system/input.hpp').read_bytes();assert sha(header)=='6c8b54bf61c1144787eb9c35df9d947889d9ebbf3ea84f123c50371f39207bf2'
    device=extract(header.decode(),'enum class Device : unsigned')+';'
    joypad=extract(header.decode(),'enum class JoypadID : unsigned')+';'
    blocks=[];methods={}
    signatures=['static unsigned snes_to_retro(unsigned device)','static unsigned snes_to_retro(unsigned, unsigned id)','int16_t inputPoll(unsigned port, unsigned device, unsigned id)']
    for label,data in [('Baseline',before),('Fixed',after)]:
        text=data.decode();body='\n'.join(extract(text,s) for s in signatures)
        methods[label]=sha(body.encode());blocks.append('struct '+label+' : CallbacksBase {\n'+body+'\n};\n')
    baseline_method=extract(before.decode(),signatures[2]);candidate_method=extract(after.decode(),signatures[2])
    assert before.decode().replace(baseline_method,candidate_method)==after.decode(),'change outside inputPoll'
    data_method=extract(controller.decode(),'uint2 Multitap::data()').replace('Multitap::','MultitapFixture::')
    latch_method=extract(controller.decode(),'void Multitap::latch(bool data)').replace('Multitap::','MultitapFixture::')
    template=(HERE/'input_test.cpp.in').read_text(encoding='utf-8')
    result=template.replace('@DEVICE_ENUM@',device).replace('@JOYPAD_ENUM@',joypad).replace('@CALLBACK_CLASSES@','\n'.join(blocks)).replace('@MULTITAP_METHODS@',data_method+'\n'+latch_method)
    tests=a.work/'tests';tests.mkdir(exist_ok=True);src=tests/'input_test.cpp';src.write_text(result,encoding='utf-8',newline='\n');binary=tests/'input_test.exe'
    cmd=[str(CLANG),'-std=c++17','-O2','-Wall','-Wextra','-Werror','-I'+str(BASE/'target-libretro'),str(src),'-o',str(binary)]
    c=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');(tests/'compile.log').write_text(c.stdout+c.stderr,encoding='utf-8')
    if c.returncode:raise RuntimeError(c.stdout+c.stderr)
    r=subprocess.run([str(binary)],capture_output=True,text=True,encoding='utf-8',timeout=30);(tests/'test.log').write_text(r.stdout+r.stderr,encoding='utf-8')
    if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    metrics=json.loads(r.stdout.strip().splitlines()[-1]);receipt={'utc':datetime.now(timezone.utc).isoformat(),'baselineWrapperSHA256':sha(before),'patchedWrapperSHA256':sha(after),'multitapSHA256':sha(controller),'inputEnumsSHA256':sha(header),'extractedCallbackSHA256':methods,'generatedTestSHA256':sha(result.encode()),'recipeSHA256':sha(Path(__file__).read_bytes()),'metrics':metrics,'compiler':cmd,'realCode':['inputPoll and conversion helpers from baseline/patched wrapper','Multitap::data and latch from pinned source','pinned libretro.h','Input::Device and JoypadID enums'],'models':['SNES IO select bit','frontend callback input states','controller fields and virtual interface'],'limitations':['No ROM, Android execution, multiplayer network or physical controllers','Existing mouse/lightgun forwarding preserved, existing upstream TODO not fixed']}
    (tests/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))

if __name__=='__main__':main()
