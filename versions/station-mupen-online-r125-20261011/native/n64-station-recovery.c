/* Station Mupen online adapter. GPL-2.0-or-later.
 * Recovery preserves a stalled deterministic run; it is not state rollback. */
#include "n64-station-recovery.h"
#include <limits.h>
#ifdef _WIN32
#include <windows.h>
static SRWLOCK mutex = SRWLOCK_INIT;
static CONDITION_VARIABLE changed = CONDITION_VARIABLE_INIT;
static void lock(void) { AcquireSRWLockExclusive(&mutex); }
static void unlock(void) { ReleaseSRWLockExclusive(&mutex); }
static void wake(void) { WakeAllConditionVariable(&changed); }
static void wait_tick(void) { SleepConditionVariableSRW(&changed, &mutex, 5, 0); }
static uint64_t now_ms(void) { return GetTickCount64(); }
static DWORD emu_thread;
static int on_emu_thread(void) { return emu_thread == GetCurrentThreadId(); }
#else
#include <pthread.h>
#include <time.h>
static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t changed = PTHREAD_COND_INITIALIZER;
static void lock(void) { pthread_mutex_lock(&mutex); }
static void unlock(void) { pthread_mutex_unlock(&mutex); }
static void wake(void) { pthread_cond_broadcast(&changed); }
static void wait_tick(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_nsec += 5000000L;
    if (ts.tv_nsec >= 1000000000L) { ++ts.tv_sec; ts.tv_nsec -= 1000000000L; }
    pthread_cond_timedwait(&changed, &mutex, &ts);
}
static uint64_t now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000u + (uint64_t)ts.tv_nsec / 1000000u;
}
static pthread_t emu_thread;
static int on_emu_thread(void) { return pthread_equal(emu_thread, pthread_self()); }
#endif

static int enabled, started, quitting, failed, connected;
static int local_slot, expected_mask, requested_pause, visible;
static int acknowledged_pause;
static int64_t epoch = -1, acknowledged_epoch = -1;
static uint64_t revision, acknowledged_revision, input_wait_since;

int StationMupenConfigure(int slot, int mask)
{
    int accepted = 0;
    lock();
    if (!enabled && !started && slot >= 0 && slot < 4 && mask > 0 &&
        mask <= 15 && (mask & (1 << slot)) && (mask & (mask - 1)))
    {
        enabled = 1; local_slot = slot; expected_mask = mask;
        quitting = failed = connected = 0;
        requested_pause = 1; visible = 1;
        epoch = acknowledged_epoch = -1;
        revision = 1; acknowledged_revision = 0; acknowledged_pause = 0;
        input_wait_since = 0;
        accepted = 1;
    }
    unlock();
    return accepted;
}

void StationMupenControl(int64_t next_epoch, int pause, int is_visible)
{
    lock();
    if (enabled && !quitting && next_epoch >= epoch && next_epoch >= 0 &&
        next_epoch <= (INT64_MAX >> 3))
    {
        pause = !!pause; is_visible = !!is_visible;
        if (next_epoch != epoch || requested_pause != pause || visible != is_visible)
        {
            epoch = next_epoch; requested_pause = pause; visible = is_visible;
            ++revision; acknowledged_epoch = -1; acknowledged_pause = 0;
            wake();
        }
    }
    unlock();
}

int64_t StationMupenStatus(void)
{
    int64_t value;
    lock();
    int current = enabled && started && !quitting &&
                  acknowledged_revision == revision && acknowledged_epoch == epoch;
    value = current && acknowledged_epoch >= 0 ? acknowledged_epoch * 8 : -8;
    if (current && acknowledged_pause) value |= 1;
    if (enabled && started && connected && !quitting) value |= 2;
    if (enabled && failed) value |= 4;
    unlock();
    return value;
}

int StationMupenStalled(void)
{
    int value;
    lock();
    /* Ordinary late input never triggers an epoch for each packet. A sustained
     * wait requests a transport barrier; it never discards input or stops CPU. */
    value = enabled && started && connected && !quitting && !failed &&
            !requested_pause && visible && input_wait_since &&
            now_ms() - input_wait_since >= 2000;
    unlock();
    return value;
}

void StationMupenRequestQuit(void)
{
    lock();
    if (enabled) { quitting = 1; acknowledged_epoch = -1; wake(); }
    unlock();
}

int station_mupen_enabled(void)
{
    int value; lock(); value = enabled; unlock(); return value;
}
int station_mupen_cancelled(void)
{
    int value; lock(); value = quitting; unlock(); return value;
}
int station_mupen_failed(void)
{
    int value; lock(); value = enabled && failed; unlock(); return value;
}
int station_mupen_executing(void)
{
    int value; lock(); value = enabled && started; unlock(); return value;
}

int station_mupen_registration(unsigned player, unsigned char *plugin, unsigned char *rawdata)
{
    int accepted;
    lock();
    accepted = enabled && !quitting && !failed && player == (unsigned)local_slot && plugin && rawdata;
    if (accepted)
    {
        /* The Android input plugin has not yet received Controls[]. The fixed
         * local profile offers MEMPAK=2/raw=0; host retains it only on P1 and
         * normalizes guest ports to NONE=1 before native roster synchronization. */
        *plugin = 2; *rawdata = 0;
    }
    unlock();
    return accepted;
}

void station_mupen_begin(void)
{
    lock();
    if (enabled && !started)
    {
#ifdef _WIN32
        emu_thread = GetCurrentThreadId();
#else
        emu_thread = pthread_self();
#endif
        started = 1;
    }
    unlock();
}

void station_mupen_finish(void)
{
    lock();
    enabled = started = connected = 0; quitting = 1;
    acknowledged_epoch = -1; acknowledged_pause = 0; input_wait_since = 0;
    wake();
    unlock();
}

void station_mupen_emulator_end(void)
{
    lock();
    if (enabled && started && on_emu_thread())
    {
        started = connected = 0; quitting = 1;
        acknowledged_epoch = -1; acknowledged_pause = 0;
        wake();
    }
    unlock();
}

void station_mupen_set_roster(unsigned mask, int slot, int self_matches)
{
    lock();
    if (enabled)
    {
        connected = mask == (unsigned)expected_mask && slot == local_slot && self_matches;
        if (!connected) { failed = 1; ++revision; acknowledged_epoch = -1; wake(); }
    }
    unlock();
}

void station_mupen_fail(void)
{
    lock();
    if (enabled && !failed) { failed = 1; ++revision; acknowledged_epoch = -1; wake(); }
    unlock();
}

void station_mupen_input_wait(int waiting)
{
    lock();
    if (enabled)
    {
        if (waiting && !input_wait_since) input_wait_since = now_ms();
        if (!waiting) input_wait_since = 0;
    }
    unlock();
}

int station_mupen_gate(station_mupen_pump pump)
{
    lock();
    if (!enabled) { unlock(); return 1; }
    /* Reject calls from UI/IO threads. Such calls cannot ACK or advance CPU. */
    if (!started || !on_emu_thread()) { unlock(); return 0; }
    for (;;)
    {
        if (quitting) { unlock(); return 0; }
        int pause = requested_pause || !visible || failed || !connected || epoch < 0;
        acknowledged_epoch = epoch; acknowledged_revision = revision;
        acknowledged_pause = pause;
        if (!pause) { unlock(); return 1; }
        uint64_t checked_revision = revision;
        unlock();
        if (pump) pump();
        lock();
        /* Do not sleep across an update received while pumping. This predicate
         * avoids the immediate-signal race that previously affected the pump. */
        if (revision == checked_revision && !quitting) wait_tick();
    }
}
