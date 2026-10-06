"""Execute the patched client branch and unchanged native host verifier with synthetic packets."""
from pathlib import Path
import argparse, hashlib, json, subprocess

p = argparse.ArgumentParser()
p.add_argument('--source', required=True)
p.add_argument('--output', required=True)
p.add_argument('--cc', default='cc')
a = p.parse_args()
src = Path(a.source).resolve()
out = Path(a.output).resolve()
if out.exists():
    raise SystemExit('Use a new test output directory')
out.mkdir(parents=True)
path = src / 'network/netplay/netplay_frontend.c'
text = path.read_text()

def function(marker):
    start = text.index(marker)
    brace = text.index('{', start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

sender = function('static bool netplay_handshake_password_send(')
verifier = function('static bool netplay_handshake_pre_password(')
anchor = text.index('/* Station already obtained the private room secret')
start = text.rfind('   if (!netplay->is_server)', 0, anchor)
end = text.index('   /* Move on to the next mode */', anchor)
branch = text[start:end]
assert 'Host expects NICK before PASSWORD' in branch
prefix = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <lrc_hash.h>
#define ANDROID 1
#define HAVE_MENU 1
#define NETPLAY_PASS_LEN 128
#define NETPLAY_PASS_HASH_LEN 64
#define NETPLAY_CMD_PASSWORD 0x0021
#define NETPLAY_CONN_FLAG_CAN_PLAY 1
#define NETPLAY_CONNECTION_PRE_INFO 4
#define MSG_NETPLAY_ENTER_PASSWORD 0
#define RARCH_ERR(...) ((void)0)
#define RARCH_WARN(...) ((void)0)
struct socket_buffer { int unused; };
struct netplay_connection { uint32_t salt; int fd,flags,mode; struct socket_buffer send_packet_buffer,recv_packet_buffer; };
typedef struct { bool is_server; } netplay_t;
typedef struct { struct { char netplay_password[128],netplay_spectate_password[128]; } paths; } settings_t;
typedef struct { const char *label,*label_setting; void (*cb)(void*,const char*); } menu_input_ctx_line_t;
struct password_buf_s { uint32_t cmd[2]; char password[64]; };
static settings_t config;
static bool automatic,send_ok=true,flush_ok=true;
static unsigned prompts,checks,seq_len;
static char sequence[8];
static unsigned char packet[72];
static size_t packet_size;
static settings_t *config_get_ptr(void){return &config;}
static bool station_android_netplay_autopassword(void){return automatic;}
static bool string_is_empty(const char *s){return !s||!*s;}
static size_t strlcpy(char *dst,const char *src,size_t size){size_t n=strlen(src);if(size){size_t k=n<size-1?n:size-1;memcpy(dst,src,k);dst[k]=0;}return n;}
static bool netplay_send(struct socket_buffer *b,int fd,const void *data,size_t size){sequence[seq_len++]='P';packet_size=size;assert(size<=sizeof(packet));memcpy(packet,data,size);return send_ok;}
static bool netplay_send_flush(struct socket_buffer *b,int fd,bool block){return flush_ok;}
static void netplay_recv_flush(struct socket_buffer *b){}
static bool netplay_handshake_nick(netplay_t *n,struct netplay_connection *c){sequence[seq_len++]='N';return true;}
static bool netplay_handshake_info(netplay_t *n,struct netplay_connection *c){return true;}
static void retroarch_menu_running(void){}
static const char *msg_hash_to_str(int id){return "password";}
static void handshake_password(void *ctx,const char *value){}
static bool menu_input_dialog_start(menu_input_ctx_line_t *line){prompts++;return true;}
#define RECV(buf,size) recvd=packet_size; memcpy(buf,packet,size); if(false)
static void check(bool value){assert(value);checks++;}
static void reset(const char *secret){memset(&config,0,sizeof(config));strlcpy(config.paths.netplay_password,secret,sizeof(config.paths.netplay_password));prompts=seq_len=0;packet_size=0;send_ok=flush_ok=true;}
'''
main = r'''
int main(void){
    char secret[65];memset(secret,'a',64);secret[64]=0;
    const uint32_t salts[]={1,0x1234,0x12345678,0x80000000,0xffffffff};
    for(unsigned i=0;i<sizeof(salts)/sizeof(salts[0]);i++){
        reset(secret);automatic=true;
        netplay_t client={false},host={true};struct netplay_connection c={0},h={0};uint32_t header[6]={0};header[3]=htonl(salts[i]);
        check(run_client(&client,&c,header));
        check(prompts==0);check(seq_len==2&&sequence[0]=='N'&&sequence[1]=='P');
        check(packet_size==72);
        struct password_buf_s wire;memcpy(&wire,packet,sizeof(wire));
        check(ntohl(wire.cmd[0])==NETPLAY_CMD_PASSWORD&&ntohl(wire.cmd[1])==64);
        char input[73],digest[65];snprintf(input,sizeof(input),"%08X%s",salts[i],secret);sha256_hash(digest,(const uint8_t*)input,strlen(input));
        check(memcmp(wire.password,digest,64)==0);
        h.salt=salts[i];bool had_input=false;
        check(netplay_handshake_pre_password(&host,&h,&had_input));
        check((h.flags&NETPLAY_CONN_FLAG_CAN_PLAY)&&had_input&&h.mode==NETPLAY_CONNECTION_PRE_INFO);
        config.paths.netplay_password[0]='b';h.flags=0;had_input=false;
        check(!netplay_handshake_pre_password(&host,&h,&had_input));check(!(h.flags&NETPLAY_CONN_FLAG_CAN_PLAY));
    }
    const char *bad[]={"", "short", "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaag"};
    for(unsigned i=0;i<sizeof(bad)/sizeof(bad[0]);i++){
        reset(bad[i]);automatic=true;netplay_t n={false};struct netplay_connection c={0};uint32_t header[6]={0};header[3]=htonl(42);
        check(!run_client(&n,&c,header));check(prompts==0&&packet_size==0);
    }
    reset(secret);automatic=false;netplay_t n={false};struct netplay_connection c={0};uint32_t header[6]={0};header[3]=htonl(42);
    check(run_client(&n,&c,header));check(prompts==1&&seq_len==1&&sequence[0]=='N');
    reset(secret);automatic=true;send_ok=false;check(!run_client(&n,&c,header));check(prompts==0);
    reset(secret);automatic=true;flush_ok=false;check(!run_client(&n,&c,header));check(prompts==0);
    reset(secret);automatic=true;header[3]=0;check(run_client(&n,&c,header));check(prompts==0&&packet_size==0);
    printf("{\"passed\":true,\"checks\":%u,\"realClientBranch\":true,\"unchangedHostVerifier\":true,\"androidExecuted\":false}\n",checks);
    return 0;
}
'''
harness = prefix + sender + '\n' + verifier + '\nstatic bool run_client(netplay_t *netplay,struct netplay_connection *connection,uint32_t *header)\n{\n' + branch + '\n return true;\n}\n' + main
(out / 'test.c').write_text(harness)
cmd = [a.cc, '-std=c99', '-O1', '-ffunction-sections', '-Wl,--gc-sections', '-I' + str(src / 'libretro-common/include'),
       str(out / 'test.c'), str(src / 'libretro-common/hash/lrc_hash.c'), '-o', str(out / 'test')]
r = subprocess.run(cmd, capture_output=True, text=True)
(out / 'compile.log').write_text(r.stdout + r.stderr)
if r.returncode:
    raise SystemExit(r.stderr)
r = subprocess.run([str(out / 'test')], capture_output=True, text=True)
print(r.stdout + r.stderr)
r.check_returncode()
result = json.loads(r.stdout)
result['sourceSHA256'] = hashlib.sha256(path.read_bytes()).hexdigest()
result['scope'] = 'Actual client branch, password sender, SHA256 and unchanged host verifier; synthetic transport/menu stubs, no Android/gameplay'
(out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
