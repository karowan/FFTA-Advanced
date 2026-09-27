#ifndef FFTA_UNIT_SLOT_H
#define FFTA_UNIT_SLOT_H
#include <stdint.h>

/* Exact native-record membership, without ARM7 software division. Callers
 * supply a bounded cohort (at most 36 records), never an arbitrary divisor.
 * For delta < 36*264, v=delta/8 is at most 1187. floor(v*1986/65536)
 * equals floor(v/33) throughout that domain. The final multiplication checks
 * exact membership, rejecting every interior byte and both range boundaries.
 * Keep this bounded proof and the exhaustive ARM regression when changing it.
 */
static inline int ffta_unit_slot(uintptr_t delta,unsigned count) {
    if(count>36 || delta>=count*264u)return -1;
    unsigned slot=((delta>>3)*1986u)>>16;
    return delta==slot*264u ? (int)slot : -1;
}
#endif
