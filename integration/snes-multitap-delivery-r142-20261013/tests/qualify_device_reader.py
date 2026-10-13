from pathlib import Path
import hashlib,json,subprocess,re
R=Path(__file__).resolve().parents[4]
UP=Path('E:/StationNetplayWork/upstream/libretro--RetroArch-69a4f0ea1e8a')
OUT=R/'topgear-players-private-20261013/qualification-v2'
def sha(b):return hashlib.sha256(b).hexdigest()
def extract(t,s):
    a=t.index(s);depth=0
    for i in range(t.index('{',a),len(t)):
        if t[i]=='{':depth+=1
        elif t[i]=='}':
            depth-=1
            if not depth:return t[a:i+1]
    raise ValueError(s)
def main():
    assert not OUT.exists();OUT.mkdir()
    files={n:(UP/n).read_bytes() for n in ['configuration.c','command.c']}
    manifest=json.loads((R/'publication-app/integration/online-snes-startup-r138/native/baseline-five-player/CORRESPONDING-SOURCE-MANIFEST.json').read_text())
    assert all(sha(b)==manifest[n] for n,b in files.items())
    cfg=files['configuration.c'].decode();cmd=files['command.c'].decode()
    loader=extract(cfg,'bool input_remapping_load_file(void *data, const char *path)')
    init=extract(cmd,'void command_event_init_controllers(')
    occurrences=[m.start() for m in re.finditer('"input_libretro_device_p"',cfg)]
    start=cfg.index('bool input_remapping_load_file(');end=cfg.index('bool input_remapping_save_file(')
    assert len(occurrences)==2 and start<occurrences[0]<end and occurrences[1]>end
    pre=r'''
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <climits>
#include <string>
#include <map>
#define MAX_USERS 16
#define RARCH_FIRST_CUSTOM_BIND 16
#define RARCH_UNMAPPED UINT_MAX
#define RETROK_UNKNOWN 0
#define RETRO_DEVICE_NONE 0
#define RETRO_DEVICE_JOYPAD 1
#define INP_FLAG_REMAPPING_CACHE_ACTIVE 1
struct settings_t { struct { unsigned input_remap_ids[16][24],input_keymapper_ids[16][24],input_libretro_device[16],input_analog_dpad_mode[16],input_remap_ports[16],input_turbo_mode,input_turbo_button,input_turbo_period,input_turbo_duty_cycle; } uints; struct {bool input_turbo_enable,input_turbo_allow_dpad;} bools;struct {int input_turbo_bind;} ints;};
static settings_t store,*config_st=&store;
struct runloop_state_t {struct {char* remapfile;} name;};static runloop_state_t rs;
struct input_state_t {unsigned flags;};static input_state_t is;
struct config_file_t {std::map<std::string,int> ints;};
static runloop_state_t* runloop_state_get_ptr(){return &rs;}
static input_state_t* input_state_get_ptr(){return &is;}
static bool string_is_empty(const char* s){return !s||!*s;}
static size_t strlcpy(char* d,const char* s,size_t n){size_t z=strlen(s);if(n){size_t c=z<n-1?z:n-1;memcpy(d,s,c);d[c]=0;}return z;}
static void fill_pathname_join_delim(char*d,const char*a,const char*b,char c,size_t n){snprintf(d,n,"%s%c%s",a,c,b);}
static bool config_get_int(config_file_t*c,const char*k,int*v){auto i=c->ints.find(k);if(i==c->ints.end())return false;*v=i->second;return true;}
#define configuration_set_uint(s,x,v) ((x)=(v))
#define CONFIG_GET_INT_BASE(c,s,f,k) do{int v;if(config_get_int(c,k,&v))(s)->f=v;}while(0)
#define CONFIG_GET_BOOL_BASE(c,s,f,k) do{int v;if(config_get_int(c,k,&v))(s)->f=v!=0;}while(0)
static void input_remapping_deinit(bool){free(rs.name.remapfile);rs.name.remapfile=nullptr;}
static void input_remapping_update_port_map(){}
static void input_remapping_set_defaults(bool){for(unsigned i=0;i<16;i++){store.uints.input_remap_ports[i]=i;for(unsigned j=0;j<24;j++)store.uints.input_remap_ids[i][j]=j;}}
struct retro_controller_description {const char* desc;unsigned id;};
struct retro_controller_info {const retro_controller_description*types;unsigned num_types;};
struct rarch_system_info_t {struct {unsigned size;retro_controller_info data[2];}ports;};
struct retro_ctx_controller_info_t {unsigned port,device;};
static unsigned connected[2];
static unsigned input_config_get_device(unsigned p){return store.uints.input_libretro_device[p];}
static const retro_controller_description* libretro_find_controller_description(const retro_controller_info* p,unsigned id){for(unsigned i=0;i<p->num_types;i++)if(p->types[i].id==id)return &p->types[i];return nullptr;}
static bool core_set_controller_port_device(retro_ctx_controller_info_t*p){if(p->port<2)connected[p->port]=p->device;return true;}
#define RARCH_WARN(...) ((void)0)
'''
    test=r'''
int main(){
 const retro_controller_description a[]={{"Joypad",1}},b[]={{"Joypad",1},{"Multitap",257}};
 rarch_system_info_t sys{{2,{{a,1},{b,2}}}};
 unsigned cases=0;
 for(unsigned count=2;count<=2;count++){
  memset(&store,0,sizeof(store));for(unsigned i=0;i<16;i++)store.uints.input_libretro_device[i]=1;
  input_remapping_set_defaults(false);command_event_init_controllers(&sys,&store,16);
  if(connected[1]!=1)return 1; // cfg keys do not enter the remap reader
  config_file_t room;unsigned devices[]={1,257,1,1,1};
  for(unsigned i=0;i<16;i++)room.ints["input_libretro_device_p"+std::to_string(i+1)]=i<5?devices[i]:0;
  if(!input_remapping_load_file(&room,"private/bsnes-mercury/bsnes-mercury.rmp"))return 2;
  command_event_init_controllers(&sys,&store,16);
  if(connected[0]!=1||connected[1]!=257)return 3;
  for(unsigned i=0;i<16;i++){if(store.uints.input_libretro_device[i]!=(i<5?devices[i]:0)||store.uints.input_remap_ports[i]!=i)return 4;for(unsigned j=0;j<24;j++)if(store.uints.input_remap_ids[i][j]!=j||store.uints.input_keymapper_ids[i][j]!=0)return 5;}
  if(store.bools.input_turbo_enable||store.bools.input_turbo_allow_dpad||store.uints.input_turbo_mode)return 6;
  input_remapping_deinit(false);cases++;
 }
 puts("cases=1 actualRemapLoader=true actualControllerInit=true adapter=257 unrelatedButtonMappingsPreserved=true");
}
'''
    source=OUT/'qualification.cpp';source.write_text(pre+'\n'+loader+'\n'+init+'\n'+test,encoding='utf-8')
    compiler=Path('C:/Program Files/LLVM/bin/clang++.exe');binary=OUT/'qualification.exe'
    p=subprocess.run([str(compiler),'-std=c++17',str(source),'-o',str(binary)],capture_output=True,text=True,timeout=180)
    assert p.returncode==0,p.stderr
    p=subprocess.run([str(binary)],capture_output=True,text=True,timeout=30);assert p.returncode==0,p.stdout+p.stderr
    receipt=dict(schema='station.snes-device-delivery.qualification.v1',passed=True,executedCases=1,productionRemapLoaderExecuted=True,productionControllerInitExecuted=True,globalConfigDeviceKeyNotRead=True,extractedBodiesByteExact=True,sourceSha256={n:sha(b) for n,b in files.items()},extractedSha256={'input_remapping_load_file':sha(loader.encode()),'command_event_init_controllers':sha(init.encode())},fixtureSourceSha256=sha(source.read_bytes()),compilerSha256=sha(compiler.read_bytes()),fixtureBinarySha256=sha(binary.read_bytes()),stdout=p.stdout.strip(),unchangedRuntimeSha256='ae72f1371e8e5a2d35f9250793ce2870f3feab73a3e17c83c9fbd48a9d15f378',actualAndroidVariablesMeasured=False,physicalGameplayValidated=False,limitations=['Config getters, settings structures, port dispatch and default button maps controlled on host; not full Android runtime','Profiles and networking unchanged; actual installed adapter still needs phone test'])
    (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))
if __name__=='__main__':main()
