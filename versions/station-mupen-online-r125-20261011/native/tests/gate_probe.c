/* Isolated real gate test: no ROM, emulator, gameplay or server. */
#include "../n64-station-recovery.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#ifdef _WIN32
#include <windows.h>
#define THREAD_RESULT DWORD WINAPI
#define SLEEP(ms) Sleep(ms)
typedef HANDLE test_thread;
#else
#include <pthread.h>
#include <time.h>
#define THREAD_RESULT void*
static void sleep_ms(unsigned ms) { struct timespec ts = {ms / 1000, (long)(ms % 1000) * 1000000L}; nanosleep(&ts, NULL); }
#define SLEEP(ms) sleep_ms(ms)
typedef pthread_t test_thread;
#endif
static int checks;
static void require(int condition, const char *label)
{
    ++checks;
    if (!condition) { fprintf(stderr, "FAIL %s\n", label); exit(1); }
}
static THREAD_RESULT run_gate(void *unused)
{
    (void)unused;
    station_mupen_begin();
    station_mupen_gate(NULL);
    return 0;
}
static test_thread launch(void)
{
#ifdef _WIN32
    return CreateThread(NULL, 0, run_gate, NULL, 0, NULL);
#else
    pthread_t thread; pthread_create(&thread, NULL, run_gate, NULL); return thread;
#endif
}
static void join_thread(test_thread thread)
{
#ifdef _WIN32
    require(WaitForSingleObject(thread, 2000) == WAIT_OBJECT_0, "gate cancels promptly");
    CloseHandle(thread);
#else
    pthread_join(thread, NULL); require(1, "gate joined");
#endif
}
static int await_status(int64_t epoch, int required_flags)
{
    for (int i = 0; i < 200; ++i)
    {
        int64_t value = StationMupenStatus();
        if (value >= 0 && value / 8 == epoch && (value & required_flags) == required_flags) return 1;
        SLEEP(1);
    }
    return 0;
}
int main(void)
{
    require(station_mupen_gate(NULL) == 1, "offline gate is passthrough");
    require(StationMupenStatus() == -8, "offline no ACK");
    require(!StationMupenConfigure(-1, 3), "reject negative slot");
    require(!StationMupenConfigure(0, 1), "reject solo online");
    require(!StationMupenConfigure(0, 6), "reject local slot missing");
    require(!StationMupenConfigure(4, 15), "reject fifth N64 slot");
    require(StationMupenConfigure(1, 3), "accept two-player mask");
    unsigned char plugin = 0, rawdata = 255;
    require(station_mupen_registration(1, &plugin, &rawdata), "registration before EMU/input-plugin startup");
    require(plugin == 2 && rawdata == 0, "pinned local MEMPAK/raw profile before Controls initialization");
    require(!station_mupen_registration(0, &plugin, &rawdata), "registration cannot change configured player slot");
    require(!station_mupen_registration(1, NULL, &rawdata), "missing registration output refused");
    require(!StationMupenConfigure(1, 3), "reject live reconfigure");
    StationMupenControl(10, 1, 1);
    require(StationMupenStatus() == -8, "control cannot fabricate ACK");
    require(!station_mupen_gate(NULL), "UI gate cannot fabricate ACK");
    require(StationMupenStatus() == -8, "UI no ACK");
    station_mupen_set_roster(3, 1, 1);
    test_thread thread = launch();
    require(await_status(10, 3), "EMU confirms actual paused roster");
    for (int i = 11; i < 111; ++i)
    {
        StationMupenControl(i, 1, 1);
        require(await_status(i, 3), "revision signaled during wait");
    }
    StationMupenControl(109, 0, 1);
    require(await_status(110, 3), "stale epoch ignored");
    StationMupenControl(110, 0, 1);
    join_thread(thread);
    require((StationMupenStatus() & 3) == 2, "resume acknowledged by EMU");
    station_mupen_finish();
    require(StationMupenStatus() == -8, "finished no stale status");

    require(StationMupenConfigure(0, 15), "four-player mask accepted");
    StationMupenControl(1, 0, 1);
    station_mupen_set_roster(7, 0, 1);
    thread = launch();
    require(await_status(1, 5), "incomplete roster is failed and paused");
    require(!(StationMupenStatus() & 2), "incomplete roster not connected");
    StationMupenControl(2, 0, 1);
    require(await_status(2, 5), "new epoch cannot clear real failure");
    StationMupenRequestQuit(); join_thread(thread); station_mupen_finish();

    require(StationMupenConfigure(0, 3), "reuse after actual teardown");
    StationMupenControl(1, 1, 1); station_mupen_set_roster(3, 0, 1);
    thread = launch(); require(await_status(1, 3), "second launch paused");
    station_mupen_fail(); require(await_status(1, 7), "desync sticky failed gate");
    StationMupenControl(2, 0, 1); require(await_status(2, 7), "desync blocks resume");
    StationMupenRequestQuit(); join_thread(thread); station_mupen_finish();

    require(StationMupenConfigure(0, 3), "visibility launch");
    StationMupenControl(3, 0, 0); station_mupen_set_roster(3, 0, 1);
    thread = launch(); require(await_status(3, 3), "hidden game paused");
    StationMupenRequestQuit(); join_thread(thread); station_mupen_finish();
    require(station_mupen_gate(NULL) == 1, "offline after teardown unaffected");
    printf("{\"checks\":%d,\"isolatedGate\":true,\"gameplay\":false}\n", checks);
    return 0;
}
