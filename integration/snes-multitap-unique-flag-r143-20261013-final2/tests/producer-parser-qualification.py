from pathlib import Path
import hashlib,json,subprocess,importlib.util
R=Path(__file__).resolve().parents[4]
UP=Path('E:/StationNetplayWork/upstream/libretro--RetroArch-69a4f0ea1e8a')
OUT=R/'topgear-r142-failed-private-20261013/parser-qualification-r2'
def sha(b):return hashlib.sha256(b).hexdigest()
def extract(t,s):
 a=t.index(s);level=0
 for i in range(t.index('{',a),len(t)):
  if t[i]=='{':level+=1
  elif t[i]=='}':
   level-=1
   if not level:return t[a:i+1]
 raise ValueError(s)
def main():
 assert not OUT.exists();OUT.mkdir()
 raw=(UP/'libretro-common/file/config_file.c').read_bytes();text=raw.decode()
 manifest=json.loads((R/'publication-app/integration/online-snes-startup-r138/native/baseline-five-player/CORRESPONDING-SOURCE-MANIFEST.json').read_text())
 assert sha(raw)==manifest['libretro-common/file/config_file.c']
 signatures=['static char *config_file_strip_comment(','static char *config_file_extract_value(','static bool config_file_parse_line(','static int config_file_from_string_internal(','struct config_entry_list *config_get_entry(','bool config_get_bool(']
 # Skip the forward declaration for parse_line.
 bodies={s:extract(text[text.index('static bool config_file_parse_line(',text.index('static bool config_file_parse_line(')+1):] if s=='static bool config_file_parse_line(' else text,s) for s in signatures}
 header=r'''
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cctype>
#include <cassert>
#include <string>
#include <file/config_file.h>
#include <array/rhmap.h>
#define MAX_INCLUDE_DEPTH 16
static char *strtok_r(char*a,const char*b,char**c){return strtok_s(a,b,c);}
#define PATH_MAX_LENGTH 4096
#define STRLEN_CONST(s) (sizeof(s)-1)
#define ISSPACE(x) isspace(x)
static bool string_is_empty(const char*s){return !s||!*s;}
static bool string_is_equal(const char*a,const char*b){return a&&b&&!strcmp(a,b);}
static bool string_starts_with_size(const char*a,const char*b,size_t n){return !strncmp(a,b,n);}
static size_t strlcpy(char*d,const char*s,size_t n){size_t z=strlen(s);if(n){size_t c=z<n-1?z:n-1;memcpy(d,s,c);d[c]=0;}return z;}
static void config_file_add_sub_conf(config_file_t*,char*,char*,size_t,config_file_cb_t*){assert(false);}
void config_file_initialize(config_file_t*c){memset(c,0,sizeof(*c));}
static int config_file_load_internal(config_file_t*,const char*,unsigned,config_file_cb_t*){assert(false);return -1;}
static void config_file_add_child_list(config_file_t*,config_file_t*){assert(false);}
bool config_file_deinitialize(config_file_t*){assert(false);return false;}
size_t config_file_add_reference(config_file_t*,char*){assert(false);return 0;}
'''
 tail=r'''
static bool read(const char*txt){config_file_t c{};char*b=strdup(txt);assert(config_file_from_string_internal(&c,b,"room/retroarch.cfg")==0);bool result=true;assert(config_get_bool(&c,"auto_remaps_enable",&result));free(b);return result;}
int main(){
 const char* old="auto_remaps_enable = \"false\"\ninput_remapping_directory = \"room/input-devices\"\nauto_remaps_enable = \"true\"\n";
 assert(!read(old));
 assert(read("auto_remaps_enable = \"true\"\ninput_remapping_directory = \"room/input-devices\"\n"));
 assert(!read("auto_remaps_enable = \"false\"\n"));
 puts("actualParser=true duplicateFalseThenTrue=false uniqueTrue=true unrelatedFalse=false cases=3");
}
'''
 source=OUT/'parser-qualification.cpp';source.write_text(raw.decode().split('#include <stdlib.h>')[0]+header+'\n'+'\n'.join(bodies.values())+'\n'+tail,encoding='utf-8')
 compiler=Path('C:/Program Files/LLVM/bin/clang++.exe');binary=OUT/'parser-qualification.exe'
 p=subprocess.run([str(compiler),'-std=c++17','-I'+str(UP/'libretro-common/include'),str(source),'-o',str(binary)],capture_output=True,text=True,timeout=180);assert p.returncode==0,p.stderr
 p=subprocess.run([str(binary)],capture_output=True,text=True,timeout=30);assert p.returncode==0,p.stdout+p.stderr
 prior=json.loads((R/'publication-app/integration/snes-multitap-delivery-r142-20261013/evidence/host-control-reader.json').read_text())
 prior.update(schema='station.r143.parser-and-control-reader.qualification.v1',configParserExecuted=True,duplicateFlagConfirmedDisabled=True,uniqueFlagConfirmedEnabled=True,parserExecutedCases=3,configFileSourceSha256=sha(raw),parserBodiesSha256={s:sha(b.encode()) for s,b in bodies.items()},parserFixtureSourceSha256=sha(source.read_bytes()),parserFixtureBinarySha256=sha(binary.read_bytes()),parserCompilerSha256=sha(compiler.read_bytes()),parserStdout=p.stdout.strip(),actualAndroidVariablesMeasured=False,physicalGameplayValidated=False)
 prior['limitations'].append('Parser bodies and hash map real; include/reference branches stubbed to fail and never entered. Room fixture reproduces R142 duplicate flag, not a phone-private config read.')
 (OUT/'receipt.json').write_text(json.dumps(prior,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:prior[k] for k in ['passed','configParserExecuted','duplicateFlagConfirmedDisabled','uniqueFlagConfirmedEnabled','parserExecutedCases']}))
if __name__=='__main__':main()
