#ifndef FFTA_ACTION_SNAPSHOT_H
#define FFTA_ACTION_SNAPSHOT_H
#include <stdint.h>
typedef struct FFTA_ActionSnapshot FFTA_ActionSnapshot;
typedef struct { const uint8_t *unit; unsigned flags; } FFTA_SnapshotUnit;
struct FFTA_ActionSnapshot {
    uint32_t magic;
    uintptr_t self;
    FFTA_ActionSnapshot *previous;
    unsigned count;
    unsigned reactions_enabled;
    FFTA_SnapshotUnit units[64];
};
unsigned ffta_snapshot_begin(FFTA_ActionSnapshot *,const uint8_t *,const uint8_t *,unsigned);
void ffta_snapshot_end(FFTA_ActionSnapshot *);
void ffta_snapshot_copy(uint8_t *,const uint8_t *);
unsigned ffta_poise_factor(const uint8_t *);
unsigned ffta_poise_hp_factor(const uint8_t *,const uint8_t *,unsigned);
unsigned ffta_poise_beneficial(const uint8_t *);
unsigned ffta_blade_ward_ready(const uint8_t *);
unsigned ffta_blade_ward_factor(const uint8_t *,const uint8_t *);
#endif
