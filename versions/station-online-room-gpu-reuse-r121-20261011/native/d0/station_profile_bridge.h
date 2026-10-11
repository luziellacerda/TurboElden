#pragma once
#include <stddef.h>
#include <stdint.h>
#ifndef __cplusplus
#include <stdbool.h>
#endif
#ifdef __cplusplus
extern "C" {
#endif
// Zero until the first Java catalog/name publication. Unchanged names preserve
// the revision; callers may skip copying while this value is unchanged.
uint64_t StationProfile_nameRevision(void);
// Copies the complete UTF-8 name including NUL and its matching revision.
// Empty name is a valid snapshot. Returns false for invalid arguments or an
// undersized buffer; provided outputs are cleared. No partial UTF-8 is returned.
// The revision may be newer than a preceding nameRevision() call.
bool StationProfile_copyName(char* destination,size_t capacity,uint64_t* revision);
#ifdef __cplusplus
}
#endif
