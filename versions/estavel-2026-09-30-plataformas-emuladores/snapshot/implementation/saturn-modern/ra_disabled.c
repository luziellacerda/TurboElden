/* No RetroAchievements client is linked in this embedded build. Preserve the
 * upstream save-state envelope with a zero-length achievement section. */
#include <stddef.h>
#include <stdint.h>
size_t YabauseRA_GetProgressSize(void) { return 0; }
int YabauseRA_SerializeProgress(uint8_t *buffer, size_t size) { return 0; }
int YabauseRA_DeserializeProgress(const uint8_t *buffer, size_t size) { return 0; }
