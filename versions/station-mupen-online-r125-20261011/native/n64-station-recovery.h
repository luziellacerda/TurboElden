/* Station Mupen online adapter. GPL-2.0-or-later, like the patched core. */
#ifndef N64_STATION_RECOVERY_H
#define N64_STATION_RECOVERY_H
#include <stdint.h>
#ifdef _WIN32
#define STATION_EXPORT __declspec(dllexport)
#else
#define STATION_EXPORT __attribute__((visibility("default")))
#endif
#ifdef __cplusplus
extern "C" {
#endif
/* Configure before NETPLAY_INIT/EXECUTE. Slots are zero based; mask is P1..P4.
 * Returns 0 for invalid inputs or a live launch. No enablement in offline. */
STATION_EXPORT int StationMupenConfigure(int local_slot, int expected_mask);
STATION_EXPORT void StationMupenControl(int64_t epoch, int pause, int visible);
/* (confirmed epoch << 3) | paused:1 | roster connected:2 | failed:4.
 * Epoch -1 means no emulator-thread acknowledgment of this revision. */
STATION_EXPORT int64_t StationMupenStatus(void);
STATION_EXPORT int StationMupenStalled(void);
/* Human exit: cancels IO/gate waits. It does not call STOP from an IO thread. */
STATION_EXPORT void StationMupenRequestQuit(void);

typedef void (*station_mupen_pump)(void);
int station_mupen_enabled(void);
int station_mupen_cancelled(void);
int station_mupen_failed(void);
int station_mupen_executing(void);
/* Core Controls[] is still zero before input InitiateControllers. Supply the
 * pinned local offer before TCP registration; host normalizes remote MEMPAK. */
int station_mupen_registration(unsigned player, unsigned char *plugin, unsigned char *rawdata);
void station_mupen_begin(void);
void station_mupen_emulator_end(void);
void station_mupen_finish(void);
void station_mupen_set_roster(unsigned mask, int self_slot, int self_matches);
void station_mupen_fail(void);
void station_mupen_input_wait(int waiting);
/* Only the EXECUTE/emulator thread may confirm a pause. Pumps network only;
 * never core, frame, VI, audio or render callbacks. Returns 0 on human quit. */
int station_mupen_gate(station_mupen_pump pump);
#ifdef __cplusplus
}
#endif
#endif
