#include "viking-state.h"
#include "registry.h"

unsigned ffta_viking_reaction_ready(const uint8_t *unit) {
    /* Native 133ADC(unit+E8,5) rejects any set status whose permission bit
     * in row5 of 527D5C is zero. The builders authenticate that exact row:
     * statuses 0,6,23,26,31,32,43. This is its intersection test, without
     * iterating all 44 status positions for every otherwise healthy forecast.
     * Retain the native incapacity predicate; do not substitute an HP guess.
     */
    return unit && !((unsigned (*)(const uint8_t *))0x080c8281u)(unit) &&
        !(unit[0xe8]&0x41u) && !(unit[0xea]&0x80u) &&
        !(unit[0xeb]&0x84u) && !(unit[0xec]&1u) && !(unit[0xed]&8u);
}

unsigned ffta_viking_snapshot_flags(const uint8_t *unit) {
    if(!unit)return 0;
    unsigned result=0;
    unsigned challenger=ffta_viking_challenger(unit);
    /* Poison9, Blind10, Slow22, Sleep26, Silence27, Confuse28,
     * Immobilize30 and Disable31. Other jobs OR their explicit custom tags
     * into harmful bit9 at the common provider composition point. */
    if((unit[0xe9]&6u) || (unit[0xea]&0x40u) ||
       (unit[0xeb]&0xdcu) || challenger)result|=1u<<9;
    if(((unsigned (*)(const uint8_t *))0x080cd50du)(unit)==FFTA_VIK_S2)
        result|=1u<<10;
    /* Native readiness scans status masks. Forecasts visit this provider for
     * every job and every candidate: only these two reactions need the scan.
     * Eligibility and status behavior for actual owners remain unchanged. */
    unsigned reaction=((unsigned (*)(const uint8_t *))0x080cd4d5u)(unit);
    if((reaction==FFTA_VIK_R1 || reaction==FFTA_VIK_R2) &&
       ffta_viking_reaction_ready(unit)) {
        if(reaction==FFTA_VIK_R1)result|=FFTA_VIK_FLAG_ABSORB_READY;
        if(reaction==FFTA_VIK_R2)result|=FFTA_VIK_FLAG_GIL_READY;
    }
    result|=challenger<<FFTA_VIK_CHALLENGER_SHIFT;
    return result;
}
