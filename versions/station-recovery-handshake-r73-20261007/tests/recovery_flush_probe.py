"""Compile exact R71 ring-buffer/pump functions against a controlled transport.

This is NOT an emulator or a full RetroArch protocol test. The handshake producer
is modelled: it enqueues the same raw MODE command as netplay_frontend.c:5021.
The functions under test are extracted verbatim from the frozen native source.
All generated files/binaries are placed on E:. No device or network is accessed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

ROOT = Path(r'E:\R71fixed\RetroArch-69a4f0ea1e8aaf442ae4858f2e7f2b31a1776576')
FRONT_SHA = 'e221e40605aecce5f168fd68ab9f06fda1eb8297a97ba6c1aff3a6e660fa8d22'
PRIVATE_SHA = '1f57454b738475c41a5d142d8e761b103d0e6c35d6bb5495f747311a6ccd6922'
FLUSH = '''   {
      size_t i;
      bool pending = false;
      for (i = 0; i < np->connections_size; i++)
      {
         struct netplay_connection *connection = &np->connections[i];
         if ((connection->flags & NETPLAY_CONN_FLAG_ACTIVE) &&
             !netplay_send_flush(&connection->send_packet_buffer,
                connection->fd, false))
         {
            station_recovery_fail();
            return false;
         }
         if ((connection->flags & NETPLAY_CONN_FLAG_ACTIVE) &&
             buf_used(&connection->send_packet_buffer) != 0)
            pending = true;
      }
      if (pending) return false;
   }
'''

def digest(data):
    return hashlib.sha256(data).hexdigest()

def function(text, name):
    match = re.search(r'^(?:static )?(?:bool|size_t) ' + re.escape(name) + r'\s*\(', text, re.M)
    assert match, name
    start = text.index('{', match.start())
    depth = 1
    end = start + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[match.start():end]

PREAMBLE = r'''
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef ptrdiff_t ssize_t;
static uint32_t probe_htonl(uint32_t x) {
   return (x >> 24) | ((x >> 8) & 0xff00) | ((x << 8) & 0xff0000) | (x << 24);
}
#define htonl probe_htonl
#define NETPLAY_CONN_FLAG_ACTIVE 1
#define NETPLAY_MODUS_INPUT_FRAME_SYNC 0
#define NETPLAY_CONNECTION_SPECTATING 1
#define NETPLAY_CONNECTION_PLAYING 2
/* Model-only netplay object. Actual socket buffer comes from private.h. */
struct netplay_connection {
   struct socket_buffer send_packet_buffer;
   int fd;
   unsigned flags;
};
typedef struct netplay {
   bool is_server;
   unsigned connected_players;
   unsigned self_mode, modus;
   unsigned run_frame_count, self_frame_count;
   struct netplay_connection *connections;
   size_t connections_size;
} netplay_t;
static struct { netplay_t *data; } networking_driver_st;
static bool failed;
static bool sync_ok;
static bool produce_mode;
static unsigned core_run_calls;
static size_t packet_count;
static size_t wire_bytes;
static unsigned char wire[4096];
static int send_budget;
static unsigned send_calls, blocking_calls, sync_calls;
static bool station_recovery_fail(void) { failed = true; return false; }
static ssize_t socket_send_all_nonblocking(int fd, const void *p, size_t n, bool no_signal) {
   (void)fd; (void)no_signal; send_calls++;
   if(send_budget < 0) return -1;
   if(n > (size_t)send_budget) n = (size_t)send_budget;
   if(wire_bytes + n > sizeof(wire)) return -1;
   memcpy(wire + wire_bytes, p, n); wire_bytes += n;
   return (ssize_t)n;
}
static bool socket_send_all_blocking(int fd, const void *p, size_t n, bool no_signal) {
   (void)fd; (void)p; (void)n; (void)no_signal; blocking_calls++; return false;
}
bool netplay_send_flush(struct socket_buffer *sbuf, int fd, bool block);
'''

MODEL = r'''
/* The producer is intentionally a model; it does not claim to exercise auth,
 * CRC negotiation, controllers, savestate deserialization, or a real ROM. */
static bool netplay_sync_pre_frame(netplay_t *np) {
   sync_calls++;
   if(!sync_ok) return false;
   if(produce_mode) {
      const unsigned char payload[] = {9,8,7,6,5,4,3,2,1};
      produce_mode = false;
      np->connected_players = 3;
      packet_count++;
      return netplay_send_raw_cmd(np, &np->connections[0], 0x26, payload, sizeof(payload));
   }
   /* Frozen frame already had local input, so no second producer is invoked. */
   return true;
}
'''

TEST = r'''
static unsigned checks;
#define CHECK(c, message) do { checks++; if(!(c)) { printf("FAIL check %u: %s\n",checks,message); return 2; } } while(0)
static unsigned char buffer[128];
static struct netplay_connection conn;
static netplay_t np;
static void reset(void) {
   memset(&np,0,sizeof(np)); memset(&conn,0,sizeof(conn)); memset(buffer,0,sizeof(buffer));
   memset(wire,0,sizeof(wire)); wire_bytes=0; send_calls=blocking_calls=sync_calls=0;
   failed=false; sync_ok=true; produce_mode=false; core_run_calls=0; packet_count=0;
   send_budget=4096; conn.fd=1; conn.flags=NETPLAY_CONN_FLAG_ACTIVE;
   conn.send_packet_buffer.data=buffer; conn.send_packet_buffer.bufsz=sizeof(buffer);
   np.connections=&conn; np.connections_size=1; np.is_server=true;
   np.self_mode=NETPLAY_CONNECTION_PLAYING; np.connected_players=1;
   networking_driver_st.data=&np;
}
int main(void) {
   unsigned i;
   const unsigned char expected[] = {0,0,0,0x26,0,0,0,9,9,8,7,6,5,4,3,2,1};
   reset(); produce_mode=true;
   for(i=0;i<64;i++) station_netplay_recovery_poll();
   CHECK(wire_bytes==sizeof(expected), "MODE remains buffered while recovery waits; normal post_frame is never called");
   CHECK(!memcmp(wire,expected,sizeof(expected)), "exact MODE order/payload preserved");
   CHECK(packet_count==1 && sync_calls==64, "frozen input frame does not generate repeated commands");
   CHECK(!buf_used(&conn.send_packet_buffer), "full send drained ring");
   CHECK(!blocking_calls && core_run_calls==0, "no blocking flush or retro_run");
   CHECK(np.self_frame_count==0 && np.run_frame_count==0, "no frame advancement");

   reset(); produce_mode=true; send_budget=3;
   CHECK(!station_netplay_recovery_poll(), "partial pending MODE must not be reported ready");
   for(i=0;i<64;i++) station_netplay_recovery_poll();
   CHECK(wire_bytes==sizeof(expected) && !memcmp(wire,expected,sizeof(expected)), "partial writes preserve exact byte stream");
   CHECK(!failed && !blocking_calls && !buf_used(&conn.send_packet_buffer), "partial writes drain asynchronously");

   reset(); produce_mode=true; send_budget=0;
   CHECK(!station_netplay_recovery_poll(), "zero-write pending MODE must not be reported ready");
   for(i=0;i<64;i++) station_netplay_recovery_poll();
   CHECK(wire_bytes==0 && buf_used(&conn.send_packet_buffer)==sizeof(expected), "temporary backpressure keeps pending bytes");
   CHECK(!failed && !blocking_calls, "backpressure neither terminal nor blocking");
   send_budget=2;
   for(i=0;i<64;i++) station_netplay_recovery_poll();
   CHECK(wire_bytes==sizeof(expected) && !memcmp(wire,expected,sizeof(expected)), "resume sends unchanged pending bytes");

   reset(); conn.send_packet_buffer.start=conn.send_packet_buffer.end=120;
   produce_mode=true; send_budget=3;
   for(i=0;i<64;i++) station_netplay_recovery_poll();
   CHECK(wire_bytes==sizeof(expected) && !memcmp(wire,expected,sizeof(expected)), "wrapped ring preserves order and payload");

   reset(); produce_mode=true; send_budget=-1;
   CHECK(!station_netplay_recovery_poll() && failed, "real native send error is not reported ready");
   CHECK(!blocking_calls && wire_bytes==0, "error path does not retry via blocking send");

   reset(); produce_mode=true; conn.flags=0;
   station_netplay_recovery_poll();
   CHECK(send_calls==0 && wire_bytes==0, "inactive connections never flushed");

   reset(); sync_ok=false; produce_mode=true;
   CHECK(!station_netplay_recovery_poll() && failed && send_calls==0, "pre-frame failure preserved");

   reset(); networking_driver_st.data=NULL;
   CHECK(!station_netplay_recovery_poll() && !failed && send_calls==0, "null native session preserved");

   reset(); np.is_server=false; np.self_mode=NETPLAY_CONNECTION_SPECTATING;
   CHECK(!station_netplay_recovery_poll(), "guest readiness still requires PLAYING");
   np.self_mode=NETPLAY_CONNECTION_PLAYING;
   CHECK(station_netplay_recovery_poll(), "guest PLAYING can become ready");
   CHECK(!blocking_calls && core_run_calls==0 && !np.run_frame_count, "all probes preserve paused core");
   printf("PASS %u checks; actual upstream buffering/pump, model handshake, no Android/gameplay\n",checks);
   return 0;
}
'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    work = Path(args.output).resolve()
    assert work.drive.upper() == 'E:' and not work.exists()
    front_bytes = (ROOT/'network/netplay/netplay_frontend.c').read_bytes()
    private_bytes = (ROOT/'network/netplay/netplay_private.h').read_bytes()
    assert digest(front_bytes)==FRONT_SHA
    assert digest(private_bytes)==PRIVATE_SHA
    front=front_bytes.decode('utf8'); private=private_bytes.decode('utf8')
    assert re.search(r'NETPLAY_CMD_MODE\s*=\s*0x0026\s*,',private)
    socket_struct=re.search(r'struct socket_buffer\s*\{.*?\};', private,re.S).group()
    pieces={name:function(front,name) for name in ('buf_used','buf_remaining','netplay_send','netplay_send_flush','netplay_send_raw_cmd','station_netplay_recovery_poll')}
    original=pieces['station_netplay_recovery_poll']
    marker='   return np->modus==NETPLAY_MODUS_INPUT_FRAME_SYNC &&'
    assert original.count(marker)==1
    candidate=original.replace(marker,FLUSH+marker)
    # Guard the factual original path motivating the model producer.
    assert 'netplay_send_raw_cmd(netplay, connection,\n                  NETPLAY_CMD_MODE, &payload, sizeof(payload));' in front
    assert 'if (ptr->have_local)\n      return true;' in front
    assert 'netplay_post_frame' not in original
    work.mkdir(parents=True)
    compiler=Path(r'C:\Program Files\LLVM\bin\clang.exe')
    results={}
    for label,pump,want in [('baseline',original,2),('candidate',candidate,0)]:
        source=socket_struct+'\n'  # primitive types must precede the real struct
        source='#include <stddef.h>\n'+source+PREAMBLE+'\n'
        source+='\n\n'.join(pieces[n] for n in ('buf_used','buf_remaining','netplay_send','netplay_send_flush','netplay_send_raw_cmd'))
        source+='\n'+MODEL+'\n'+pump+'\n'+TEST
        src=work/(label+'.c'); src.write_text(source,encoding='utf8')
        binary=work/(label+'.exe')
        compilation=subprocess.run([str(compiler),'-std=c11','-Wall','-Wextra','-Wno-unused-parameter',str(src),'-o',str(binary)],capture_output=True,text=True)
        (work/(label+'-compile.log')).write_text(compilation.stdout+compilation.stderr,encoding='utf8')
        assert compilation.returncode==0, compilation.stderr
        result=subprocess.run([str(binary)],capture_output=True,text=True)
        assert result.returncode==want,(label,result.stdout,result.stderr)
        results[label]={'expectedExitCode':want,'exitCode':result.returncode,'output':result.stdout.strip(),'harnessSHA256':digest(src.read_bytes())}
    receipt={'nativeSourceSHA256':FRONT_SHA,'nativePrivateSHA256':PRIVATE_SHA,'testRecipeSHA256':digest(Path(__file__).read_bytes()),'extractedFunctionHashes':{name:digest(text.encode()) for name,text in pieces.items()},'candidatePumpSHA256':digest(candidate.encode()),'results':results,'checks':22,'scope':'upstream ring-buffer, command enqueue and recovery pump; modeled handshake producer/transport; no ROM, Android or real multiplayer','baselineFails':True,'candidatePasses':True,'productionNativeModified':False}
    (work/'recovery-flush-probe.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    (work/'candidate-recovery-poll.c').write_text(candidate+'\n',encoding='utf8')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__': main()
