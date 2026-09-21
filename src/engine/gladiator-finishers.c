#include <stdint.h>
#include "registry.h"

static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }

/* These are exact factors, not an extra rounding phase. The shared physical
 * finalizer must combine this numerator/10 with every applicable modifier. */
unsigned ffta_finisher_numerator(unsigned action,const uint8_t *target) {
    if(action==FFTA_GLD_AX_A4)return 18;
    if(action!=FFTA_GLD_AX_A3)return 10;
    if(!target)return 11;
    unsigned hp=half(target+0x18),maximum=half(target+0x1a);
    return maximum && hp*2u<=maximum ? 18 : 11;
}

unsigned ffta_executioner_chance(unsigned chance,const uint8_t *target) {
    /* Native ordinary A is5..95 or a forced100; zero here represents a
     * preventing eligibility/immunity/reaction result, never ordinary evasion. */
    if(!chance || !target || ffta_finisher_numerator(FFTA_GLD_AX_A3,target)!=18)return chance;
    return chance>=75 ? 95 : chance+20;
}
/* Player preview B55CC uses12E0BC, bypassing the execution/AI dispatcher.
 * Its already evaluated ordinary chance and explicit target are authoritative;
 * never consult shared context, which may contain a different preview stage. */
unsigned ffta_executioner_preview_chance(unsigned chance,unsigned action,const uint8_t *target) {
    return action==FFTA_GLD_AX_A3 ? ffta_executioner_chance(chance,target) : chance;
}

extern unsigned ffta_original_finisher_chance(void);
unsigned ffta_executioner_resolve_chance(unsigned chance) {
    const uint8_t *context=(const uint8_t *)0x0200f3f0u;
    if(half(context+0xc)!=FFTA_GLD_AX_A3)return chance;
    return ffta_executioner_chance(chance,*(const uint8_t *const *)(context+4));
}
unsigned ffta_executioner_chance_dispatch(unsigned caller) {
    unsigned chance=ffta_original_finisher_chance();
    /* The committed executor still adds its own native10-point adjustment.
     * Its separate pre-roll hook applies the new bonus after that adjustment. */
    return caller==0x080a2fe1u ? chance : ffta_executioner_resolve_chance(chance);
}

/* Isolated lifecycle primitive only. No global/native spare bit is borrowed.
 * Caller must supply an explicitly owned, copied and suspend-serialized byte.
 * Event0 applies/refreshes;1 own-turn start;2 KO;3 Petrify;4 battle end;
 * 5 job change;6 broad remedy. Other events leave the state unchanged. */
unsigned ffta_exposed_transition(uint8_t *owned_state,unsigned event,unsigned immunity_cancels) {
    if(!owned_state)return 0;
    if(event==0) {
        if(immunity_cancels)return 0;
        *owned_state|=1;return 1;
    }
    if(event<=6)*owned_state&=(uint8_t)~1u;
    return 1;
}
/* Exact6/5 factor for positive direct physical HP damage, including immediate
 * retaliation. Costs, healing/absorption, MP loss and ticks pass numerator5.
 * Last Resort remains a distinct factor; combining6/5 twice gives36/25. */
unsigned ffta_exposed_numerator(const uint8_t *owned_state,int signed_damage,unsigned direct_physical_hp) {
    return owned_state && (*owned_state&1) && signed_damage>0 && direct_physical_hp ? 6 : 5;
}
