#include <assert.h>
#include <stdio.h>
#include "station_recovery.h"
int main(void)
{
    assert(!station_recovery_active());
    station_recovery_request(1,true,true);
    assert(!station_recovery_waiting()); /* v1 remains inactive */
    station_recovery_configure(true);
    assert(station_recovery_waiting() && station_recovery_status()==-1);
    station_recovery_confirm(true,false);
    assert(station_recovery_status()==9); /* real thread acknowledged pause, epoch 1 */
    station_recovery_confirm(true,true);
    assert(station_recovery_status()==11);
    station_recovery_request(2,false,true);
    assert(station_recovery_status()==-1 && !station_recovery_waiting());
    station_recovery_confirm(false,true);
    assert(station_recovery_status()==18);
    station_recovery_request(1,true,false);
    assert(station_recovery_status()==18); /* stale JNI event cannot rewind epoch */
    station_recovery_mark_stalled();
    assert(station_recovery_is_stalled());
    station_recovery_request(3,true,false);
    assert(station_recovery_waiting() && !station_recovery_is_stalled());
    station_recovery_confirm(true,true);
    assert(station_recovery_status()==27);
    station_recovery_fail();
    station_recovery_request(4,false,true);
    station_recovery_confirm(false,true);
    assert(station_recovery_waiting() && station_recovery_status()==38);
    station_recovery_configure(false);
    assert(!station_recovery_waiting());
    puts("PASS 13 native control assertions; host test, not Android emulation");
}
