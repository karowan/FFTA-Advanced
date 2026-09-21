#ifndef FFTA_ART_PALETTE_LIMITS_H
#define FFTA_ART_PALETTE_LIMITS_H
#include <stdint.h>
#define FFTA_ART_CLASS_COUNT 10
/* Histories are (class,native-bank) pairs, not hardware palette banks.
 * The installed layout remains ten until a larger reservation is integrated. */
#ifndef FFTA_ART_HISTORY_SLOTS
#define FFTA_ART_HISTORY_SLOTS 10
#endif
#if FFTA_ART_HISTORY_SLOTS < FFTA_ART_CLASS_COUNT || FFTA_ART_HISTORY_SLOTS > 31
#error Unsupported art history capacity
#endif
#if FFTA_ART_HISTORY_SLOTS <= 16
typedef uint16_t FFTA_ArtSlotMask;
#else
typedef uint32_t FFTA_ArtSlotMask;
#endif
#endif
