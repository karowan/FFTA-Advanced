#ifndef FFTA_MISSION_RECOVERY_H
#define FFTA_MISSION_RECOVERY_H
#include <stdint.h>

/* Reserved design range; installation must also verify native text/event use. */
#define FFTA_RECOVERY_FIRST 407u
#define FFTA_RECOVERY_COUNT 64u
#define FFTA_GEAR_RECOVERY_FIRST 471u
#define FFTA_GEAR_RECOVERY_COUNT 6u

typedef struct { uint16_t mission; uint8_t copies; } FFTA_RecoverySource;
typedef struct { uint16_t mission; uint8_t required, consumed, repeatable; } FFTA_RecoveryUse;
typedef struct {
    uint8_t item, source_count, use_count;
    FFTA_RecoverySource sources[3];
    FFTA_RecoveryUse uses[3];
} FFTA_RecoveryRule;
/* Exactly one original opportunity is present; the other isFFFF. */
typedef struct { uint16_t item, original_mission, original_gift; } FFTA_GearRecoveryRule;

unsigned ffta_recovery_needed(unsigned mission);
unsigned ffta_recovery_pub_mask(unsigned mission, unsigned native_mask);
unsigned ffta_recovery_cached_allowed(const uint8_t *cached);
void ffta_recovery_prune_offers(void);
#endif
