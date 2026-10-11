"""Generate a pinned Mupen online source overlay; never edit the offline tree.

Apply the resulting relative files to a separately copied upstream build tree.
Only those files are replacements. Every unmatched upstream hash is rejected.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
from pathlib import Path

PINS = {
    "mupen64plus-core/upstream/src/main/main.c": "649e6a9908dd2df978c0d7169fd3e824a578e7da4026bcfc75f22ecb5d98b2c0",
    "mupen64plus-core/upstream/src/main/netplay.c": "cac5253c1f2fe2a4bbd415b8cd459e2f5410db4162e32a11089c3989ac153022",
    "mupen64plus-core/upstream/src/main/netplay.h": "19f494cd89d23de3584ab0bfa828132f97a37f2b6b3a1479ac7a268edd5f9f6f",
    "mupen64plus-core/mupen64plus-core.mk": "190e8d0e3dcc6d3887a0afd260d115d22db1a77b4fa717efd2899d859f4dd922",
    "mupen64plus-core/upstream/src/api/api_export.ver": "784b70a7bb4a1a250425947808d9998d941048a612fab64b10b7a7c3157a971c",
}

def replace(text: str, before: str, after: str) -> str:
    if text.count(before) != 1:
        raise ValueError(f"Expected one patch anchor, found {text.count(before)}: {before[:80]!r}")
    return text.replace(before, after, 1)

TCP_HELPERS = r'''
/* Station-only IO. SDL_net's TCP prefix is ready + channel (SDL_net 2.x).
 * Verify the descriptor against the public peer API before any IO. Source:
 * https://github.com/libsdl-org/SDL_net/blob/release-2.2.0/SDLnetTCP.c
 * Transient WSS loss leaves this local proxy socket alive. EOF is a failed
 * preparation/pipe, never an infinite recv loop or automatic emulator STOP. */
static int station_tcp_fd = -1;
static int station_validate_tcp_fd(TCPsocket sock)
{
#if !defined(WIN32)
    int fd, type = 0;
    socklen_t size = sizeof(type);
    struct sockaddr_in peer;
    socklen_t peer_size = sizeof(peer);
    IPaddress *sdl_peer = SDLNet_TCP_GetPeerAddress(sock);
    if (!sock || !sdl_peer) return -1;
    memcpy(&fd, (const char*)sock + sizeof(int), sizeof(fd));
    if (getsockopt(fd, SOL_SOCKET, SO_TYPE, &type, &size) || type != SOCK_STREAM ||
        getpeername(fd, (struct sockaddr*)&peer, &peer_size) ||
        peer.sin_family != AF_INET || peer.sin_addr.s_addr != sdl_peer->host ||
        peer.sin_port != sdl_peer->port) return -1;
    return fd;
#else
    (void)sock; return -1; /* Online fork targets Android; offline untouched. */
#endif
}

static int station_tcp_transfer(void *data, int size, int writing)
{
#if !defined(WIN32)
    int total = 0;
    if (size < 0 || station_tcp_fd < 0) { station_mupen_fail(); return 0; }
    while (total < size)
    {
        if (station_mupen_cancelled() || station_mupen_failed()) return 0;
        struct pollfd p = {station_tcp_fd, writing ? POLLOUT : POLLIN, 0};
        int ready = poll(&p, 1, 20);
        if (ready < 0) { if (errno == EINTR) continue; station_mupen_fail(); return 0; }
        if (!ready) continue;
        /* Read pending bytes even when HUP accompanies readable EOF. */
        if (!(p.revents & (writing ? POLLOUT : POLLIN)))
        { station_mupen_fail(); return 0; }
        ssize_t n = writing ?
            send(station_tcp_fd, (char*)data + total, (size_t)(size - total), MSG_DONTWAIT | MSG_NOSIGNAL) :
            recv(station_tcp_fd, (char*)data + total, (size_t)(size - total), MSG_DONTWAIT);
        if (n < 0 && (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK)) continue;
        if (n <= 0) { station_mupen_fail(); return 0; }
        total += (int)n;
    }
    return 1;
#else
    (void)data; (void)size; (void)writing; station_mupen_fail(); return 0;
#endif
}

static int netplay_tcp_send(TCPsocket sock, const void *data, int size)
{
    if (!station_mupen_enabled()) return SDLNet_TCP_Send(sock, data, size);
    return station_tcp_transfer((void*)data, size, 1) ? size : -1;
}

void netplay_station_pump(void) { if (l_netplay_is_init && l_cin_compats) netplay_process(); }

void netplay_station_release_inputs(void)
{
    if (!station_mupen_enabled() || !l_cin_compats) return;
    for (int i = 0; i < 4; ++i)
    {
        struct netplay_event *event = l_cin_compats[i].event_first;
        while (event) { struct netplay_event *next = event->next; free(event); event = next; }
        l_cin_compats[i].event_first = NULL;
    }
    l_cin_compats = NULL; /* stack-owned main_run cin_compats is about to end. */
}
'''

def patch_main(s: str) -> str:
    s = replace(s, '#include "netplay.h"', '#include "netplay.h"\n#include "n64-station-recovery.h"')
    s = replace(s, 'void main_advance_one(void)\n{',
                'void main_advance_one(void)\n{\n    if (station_mupen_enabled()) return; /* no unilateral frame step */')
    s = replace(s, 'm64p_error main_reset(int do_hard_reset)\n{',
                'm64p_error main_reset(int do_hard_reset)\n{\n    if (station_mupen_enabled()) return M64ERR_INVALID_STATE; /* no unilateral state reset */')
    s = replace(s, 'void new_vi(void)\n{', 'void new_vi(void)\n{\n    if (!station_mupen_gate(netplay_station_pump)) return;')
    s = replace(s, 'm64p_error main_run(void)\n{', 'm64p_error main_run(void)\n{\n    station_mupen_begin();')
    s = replace(s, '    if (setjmp(jump_exit) == 0)\n        run_device(&g_dev);',
                '    if (setjmp(jump_exit) == 0)\n    {\n        if (station_mupen_gate(netplay_station_pump)) run_device(&g_dev);\n    }')
    s = replace(s, '    // clean up\n    g_EmulatorRunning = 0;',
                '    // clean up\n    netplay_station_release_inputs();\n    g_EmulatorRunning = 0;')
    s = replace(s, '    StateChanged(M64CORE_EMU_STATE, M64EMU_STOPPED);\n\n    return M64ERR_SUCCESS;',
                '    StateChanged(M64CORE_EMU_STATE, M64EMU_STOPPED);\n    station_mupen_emulator_end();\n\n    return M64ERR_SUCCESS;')
    s = replace(s, '    return M64ERR_PLUGIN_FAIL;\n}\n\nvoid main_stop(void)',
                '    netplay_station_release_inputs();\n    station_mupen_emulator_end();\n    return M64ERR_PLUGIN_FAIL;\n}\n\nvoid main_stop(void)')
    s = replace(s, 'void main_stop(void)\n{',
                'void main_stop(void)\n{\n    if (station_mupen_enabled() && !station_mupen_cancelled()) return; /* explicit human Quit must precede STOP */\n    StationMupenRequestQuit();')
    return s

def patch_netplay(s: str) -> str:
    # Replace sends before adding helper to keep the offline delegate original.
    s = s.replace('SDLNet_TCP_Send(', 'netplay_tcp_send(')
    s = replace(s, '#include "netplay.h"', '#include "netplay.h"\n#include "n64-station-recovery.h"')
    s = replace(s, '#include <netinet/ip.h>', '#include <netinet/ip.h>\n#include <poll.h>\n#include <errno.h>\n#include <unistd.h>')
    s = replace(s, '#define EF 46', '#define EF 46\nstatic void netplay_process(void);\n' + TCP_HELPERS)
    s = replace(s, 'm64p_error netplay_stop()\n{',
                'm64p_error netplay_stop()\n{\n    if (station_mupen_executing())\n    {\n        return M64ERR_INVALID_STATE; /* no implicit Quit; join EXECUTE before closing/freeing */\n    }')
    s = replace(s, 'uint8_t netplay_register_player(uint8_t player, uint8_t plugin, uint8_t rawdata, uint32_t reg_id)\n{',
                'uint8_t netplay_register_player(uint8_t player, uint8_t plugin, uint8_t rawdata, uint32_t reg_id)\n{\n    if (station_mupen_enabled() && !station_mupen_registration(player, &plugin, &rawdata))\n    { station_mupen_fail(); return 0; }')
    s = replace(s, '    for (int i = 0; i < 4; ++i)\n    {\n        l_netplay_control[i] = -1;',
                '    if (station_mupen_enabled())\n    {\n        station_tcp_fd = station_validate_tcp_fd(l_tcpSocket);\n        if (station_tcp_fd < 0)\n        {\n            station_mupen_fail();\n            SDLNet_TCP_Close(l_tcpSocket); SDLNet_UDP_Close(l_udpSocket);\n            l_tcpSocket = NULL; l_udpSocket = NULL;\n            return M64ERR_SYSTEM_FAIL;\n        }\n    }\n\n    for (int i = 0; i < 4; ++i)\n    {\n        l_netplay_control[i] = -1;')
    s = replace(s, '        l_netplay_is_init = 0;\n        SDLNet_Quit();',
                '        l_netplay_is_init = 0;\n        l_cin_compats = NULL; station_tcp_fd = -1;\n        station_mupen_finish();\n        SDLNet_Quit();')
    s = replace(s, 'static void netplay_process()\n{', 'static void netplay_process(void)\n{')
    s = replace(s, '    UDPpacket *packet = SDLNet_AllocPacket(512);',
                '    UDPpacket *packet = SDLNet_AllocPacket(512);\n    if (station_mupen_enabled() && !packet) { station_mupen_fail(); return; }')
    s = replace(s, '        switch (packet->data[0])',
                '        if (station_mupen_enabled() && packet->len < 1) { station_mupen_fail(); break; }\n        switch (packet->data[0])')
    s = replace(s, '            case UDP_RECEIVE_KEY_INFO:\n                player = packet->data[1];',
                '            case UDP_RECEIVE_KEY_INFO:\n                if (station_mupen_enabled() && (packet->len < 5 || packet->data[1] >= 4 ||\n                    (int)packet->data[4] > (packet->len - 5) / 9))\n                { station_mupen_fail(); break; }\n                player = packet->data[1];')
    s = replace(s, '                current_status = packet->data[2];',
                '                current_status = packet->data[2];\n                if (station_mupen_enabled() && (current_status & 0x1)) station_mupen_fail();')
    s = replace(s, '                    new_event->count = count;',
                '                    if (station_mupen_enabled() && !new_event) { station_mupen_fail(); break; }\n                    new_event->count = count;')
    s = replace(s, '                DebugMessage(M64MSG_ERROR, "Netplay: received unknown message from server");',
                '                if (station_mupen_enabled()) station_mupen_fail();\n                DebugMessage(M64MSG_ERROR, "Netplay: received unknown message from server");')
    s = replace(s, 'static int netplay_ensure_valid(uint8_t control_id)\n{', r'''static int netplay_ensure_valid(uint8_t control_id)
{
    if (station_mupen_enabled())
    {
        while (1)
        {
            if (station_mupen_cancelled()) return 0;
            if (!station_mupen_gate(netplay_station_pump)) return 0;
            if (check_valid(control_id, l_cin_compats[control_id].netplay_count))
            { station_mupen_input_wait(0); return 1; }
            station_mupen_input_wait(1);
            netplay_request_input(control_id);
            netplay_process();
            SDL_Delay(5); /* no busy-spin, worker thread, 10s timeout or STOP */
        }
    }''')
    s = replace(s, '        main_core_state_set(M64CORE_EMU_STATE, M64EMU_STOPPED);',
                '        if (!station_mupen_enabled()) main_core_state_set(M64CORE_EMU_STATE, M64EMU_STOPPED);')
    s = replace(s, '    size_t recv = 0;\n    while (recv < 2)\n        recv += SDLNet_TCP_Recv(l_tcpSocket, &response[recv], 2 - recv);',
                '    if (station_mupen_enabled())\n    {\n        if (!station_tcp_transfer(response, 2, 0)) return 0;\n    }\n    else\n    {\n        size_t recv = 0;\n        while (recv < 2) recv += SDLNet_TCP_Recv(l_tcpSocket, &response[recv], 2 - recv);\n    }')
    s = replace(s, '        while (recv < size)\n            recv += SDLNet_TCP_Recv(l_tcpSocket, data_array + recv, size - recv);',
                '        if (station_mupen_enabled())\n        {\n            if (size > INT_MAX || !station_tcp_transfer(data, (int)size, 0))\n            { free(output_data); return file_read_error; }\n        }\n        else\n        {\n            while (recv < size) recv += SDLNet_TCP_Recv(l_tcpSocket, data_array + recv, size - recv);\n        }')
    s = replace(s, '#include <SDL_net.h>', '#include <SDL_net.h>\n#include <limits.h>')
    s = replace(s, '        while (recv < 24)\n            recv += SDLNet_TCP_Recv(l_tcpSocket, &output_data[recv], 24 - recv);',
                '        if (station_mupen_enabled())\n        {\n            if (!station_tcp_transfer(output_data, 24, 0)) return;\n        }\n        else\n        {\n            while (recv < 24) recv += SDLNet_TCP_Recv(l_tcpSocket, &output_data[recv], 24 - recv);\n        }')
    s = replace(s, '    size_t recv = 0;\n    while (recv < 24)\n        recv += SDLNet_TCP_Recv(l_tcpSocket, &input_data[recv], 24 - recv);\n    uint32_t curr = 0;',
                '    if (station_mupen_enabled())\n    {\n        if (!station_tcp_transfer(input_data, 24, 0)) return;\n    }\n    else\n    {\n        size_t recv = 0;\n        while (recv < 24) recv += SDLNet_TCP_Recv(l_tcpSocket, &input_data[recv], 24 - recv);\n    }\n    unsigned station_mask = 0; int station_slot = -1;\n    uint32_t curr = 0;')
    s = replace(s, '        reg_id = SDLNet_Read32(&input_data[curr]);',
                '        reg_id = SDLNet_Read32(&input_data[curr]);\n        if (reg_id) station_mask |= 1u << i;\n        if (reg_id && reg_id == l_reg_id) station_slot = i;')
    s = replace(s, '\nstatic void netplay_send_raw_input(struct pif* pif)',
                '\nstatic void netplay_send_raw_input(struct pif* pif)')
    # Exact function boundary: attach real roster only after complete parsing.
    s = replace(s, '    }\n}\n\nstatic void netplay_send_raw_input(struct pif* pif)',
                '    }\n    if (station_mupen_enabled()) station_mupen_set_roster(station_mask, station_slot, station_slot >= 0);\n}\n\nstatic void netplay_send_raw_input(struct pif* pif)')
    s = replace(s, '        netplay_send_raw_input(pif);',
                '        if (!station_mupen_gate(netplay_station_pump)) return;\n        netplay_send_raw_input(pif);')
    s = replace(s, '        int recv = 0;\n        while (recv < size)',
                '        if (station_mupen_enabled())\n            return station_tcp_transfer(data, size, 0) ? M64ERR_SUCCESS : M64ERR_SYSTEM_FAIL;\n        int recv = 0;\n        while (recv < size)')
    return s

def generate(upstream: Path) -> dict[str, bytes]:
    original = {}
    for name, expected in PINS.items():
        raw = (upstream / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError(f"Wrong upstream hash: {name}")
        original[name] = raw.decode("utf-8").replace("\r\n", "\n")
    outputs = dict(original)
    main, netplay, header, makefile, exports = PINS
    outputs[main] = patch_main(outputs[main])
    outputs[netplay] = patch_netplay(outputs[netplay])
    outputs[header] = replace(outputs[header], '#define NETPLAY_CORE_VERSION 1',
                             '#define NETPLAY_CORE_VERSION 1\nvoid netplay_station_pump(void);\nvoid netplay_station_release_inputs(void);')
    outputs[makefile] = replace(outputs[makefile], '    $(SRCDIR)/main/netplay.c',
                               '    $(SRCDIR)/main/n64-station-recovery.c                    ' + '\\' + '\n' +
                               '    $(SRCDIR)/main/netplay.c')
    outputs[exports] = replace(outputs[exports], 'CoreDoCommand;',
                              'CoreDoCommand;\nStationMupenConfigure;\nStationMupenControl;\nStationMupenStatus;\nStationMupenStalled;\nStationMupenRequestQuit;')
    diff = "".join("".join(difflib.unified_diff(original[n].splitlines(True), outputs[n].splitlines(True),
                    fromfile="a/" + n, tofile="b/" + n)) for n in PINS)
    result = {n: s.encode("utf-8") for n, s in outputs.items()}
    for name in ("n64-station-recovery.c", "n64-station-recovery.h"):
        result["mupen64plus-core/upstream/src/main/" + name] = (Path(__file__).parent / name).read_bytes()
    result["station-native.patch"] = diff.encode("utf-8")
    result["station-native-manifest.json"] = (json.dumps({
        "upstreamCommit": "33bf7021549d7873e976884370fbd1a8e7333bc7",
        "upstreamHashes": PINS,
        "outputs": {n: hashlib.sha256(raw).hexdigest() for n, raw in result.items()},
        "offlineSourcesModifiedInPlace": False,
        "transportRecoveryIsRollback": False,
    }, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return result

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    source, target = args.upstream.resolve(), args.out.resolve()
    if source == target or source in target.parents or target in source.parents:
        raise SystemExit("Overlay must be outside the unchanged upstream tree")
    outputs = generate(source)
    # Complete validation before the first write; existing different files rejected.
    for name, raw in outputs.items():
        path = target / name
        if path.exists() and path.read_bytes() != raw:
            raise SystemExit(f"Refusing to replace different overlay file: {name}")
    for name, raw in outputs.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    print(json.dumps({"generatedFiles": len(outputs), "output": str(target), "upstreamUnchanged": True}))

if __name__ == "__main__":
    main()
