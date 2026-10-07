#include <stdio.h>
#include "station_recovery.h"
#include "upstream_stall_enum.h"
#include "candidate_stall_hook.h"

int main(void)
{
    const enum rarch_netplay_stall_reason reasons[] = {
        NETPLAY_STALL_INPUT_LATENCY, NETPLAY_STALL_SERVER_REQUESTED,
        NETPLAY_STALL_SPECTATOR_WAIT, NETPLAY_STALL_NONE,
        NETPLAY_STALL_RUNNING_FAST
    };
    unsigned checks = 0, enabled, i;
    for (enabled = 0; enabled < 2; enabled++)
    {
        station_recovery_configure(enabled != 0);
        for (i = 0; i < sizeof(reasons) / sizeof(reasons[0]); i++)
        {
            bool expected = enabled && reasons[i] == NETPLAY_STALL_RUNNING_FAST;
            station_recovery_request(1, true, true);
            station_recovery_request(1, false, true);
            candidate_sample_stall(reasons[i]);
            checks++;
            if (station_recovery_is_stalled() != expected)
            {
                printf("FAIL unexpected recovery for native stall enum=%d enabled=%u\n", reasons[i], enabled);
                return 1;
            }
        }
    }
    station_recovery_request(1, true, true);
    station_recovery_request(1, false, true);
    for (i = 0; i < 100; i++)
    {
        candidate_sample_stall(NETPLAY_STALL_INPUT_LATENCY);
        candidate_sample_stall(NETPLAY_STALL_SERVER_REQUESTED);
        if (station_recovery_is_stalled()) return 2;
        checks++;
    }
    candidate_sample_stall(NETPLAY_STALL_RUNNING_FAST);
    if (!station_recovery_is_stalled()) return 3;
    checks++;
    station_recovery_request(2, true, true);
    if (station_recovery_is_stalled()) return 4;
    checks++;
    puts("PASS 112 native stall policy checks; upstream enum and compiled hook, not Android gameplay");
    return checks == 112 ? 0 : 5;
}
