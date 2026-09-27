#include <stdint.h>
#include "blade-wound.h"
#include "samurai-state.h"
#include "chemist-progression.h"

/* The native periodic renderer is idle when an actor finishes its turn.
 * Reuse its explicit context, not a mutable static or an inferred owner. */
#define PERIODIC ((uint8_t *)0x0200f770u)
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
static void put(uint8_t *p,unsigned v) { p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8); }

unsigned ffta_samurai_turn_end(uint8_t *unit,uint8_t *battle) {
#if FFTA_CHEMIST_PROGRESSION
    /* Installed pulse calls this complete lifecycle chain, not the earlier
     * standalone Samurai timer. Preserve that composition when recompiling. */
    extern void ffta_drk_lifecycle_turn_end(uint8_t *);
    ffta_cp_fuse_prepare(unit,battle);
    ffta_drk_lifecycle_turn_end(unit);
#else
    ffta_centered_turn_end(unit);
#endif
    uint8_t *record=ffta_owned_wound(unit);
    if(!record)goto next;
    if(!half(unit+0x18) || (unit[0xe8]&0x40)) {
        ffta_wound_record_clear(record);goto next;
    }
    uint8_t *wrapper=*(uint8_t **)(battle+4);
    if(!wrapper || *(uint8_t **)wrapper!=unit)goto next;
    unsigned pulse=ffta_wound_record_tick(record);
    if(!pulse)goto next;
    for(unsigned i=0;i<0x114;++i)PERIODIC[i]=0;
    *(uint8_t **)PERIODIC=wrapper;
    put(PERIODIC+0x5e,pulse);
    /* Native phase35 waits for damage animation, then phase6 owns KO and
     * phase39 finishes. No native Poison/Regen/timer stages are scheduled. */
    put(PERIODIC+0xcc,42);put(PERIODIC+0xce,2);
    put(PERIODIC+0xd0,39);put(PERIODIC+0xd2,6);
    *(uint8_t **)(battle+0x5c)=PERIODIC;
    return 1;
next:
#if FFTA_CHEMIST_PROGRESSION
    return ffta_cp_fuse_next(battle);
#else
    return 0;
#endif
}
unsigned ffta_wound_advance(uint8_t *battle) {
    uint8_t *context=*(uint8_t **)(battle+0x5c);
    unsigned busy=((unsigned (*)(uint8_t *))0x0809f9c1u)(context);
    if(!busy) {
        uint8_t *wrapper=*(uint8_t **)context;
        uint8_t *unit=*(uint8_t **)wrapper;
        if(!half(unit+0x18))ffta_wound_record_clear(ffta_owned_wound(unit));
        ((void (*)(uint8_t *))0x08098131u)(wrapper);
        *(uint8_t **)(battle+0x5c)=0;
#if FFTA_CHEMIST_PROGRESSION
        return ffta_cp_fuse_next(battle);
#endif
    }
    return busy;
}
