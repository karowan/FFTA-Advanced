#ifndef FFTA_NATIVE_UNIT_H
#define FFTA_NATIVE_UNIT_H
#include <stdint.h>

/* Native 1308F4 reads unit flags through C7EA4(field27), tests 0x0800,
 * then checks Zombie(status11) through CD9A4. Auto-Life is status2 and
 * must never serve as a proxy for either kind of undead. The predicate
 * uses the supplied unit, including independent evaluated copies. */
static inline unsigned ffta_native_undead(const uint8_t *u){
 return u && ((unsigned (*)(const uint8_t *))0x081308f5u)(u);
}
#endif
