#include <stdint.h>
#include "registry.h"
#include "viking-native.h"
#include "viking-state.h"
#include "action-snapshot.h"
#include "reaction-ids.h"
extern unsigned ffta_viking_reaction_eligibility(const uint8_t *);

unsigned ffta_sea_legs(const uint8_t *unit) {
    return unit && ((unsigned (*)(const uint8_t *))0x080cd50du)(unit)==FFTA_VIK_S1;
}

extern unsigned ffta_original_viking_compatibility(uint8_t *,unsigned);
unsigned ffta_viking_compatibility(uint8_t *unit,unsigned effect) {
    /* Native Aim Legs/Goo/Wood Veil use effect24 (Immobilize, status30).
     * Rush and Body Slam displacement use effect26. Reject their effect only;
     * the preceding damage stage, Slow51 and native movement remain intact.
     * Future custom displacement uses the same exported Sea Legs predicate.
     * This is an explicitly supplied evaluated recipient, not a live lookup.
     */
    if((effect==24 || effect==26) && ffta_sea_legs(unit))return 0;
    if((effect==93 || effect==94) && !ffta_job_state(unit))return 0;
    if(effect==94 && ((unsigned (*)(const uint8_t *))0x080cd50du)(unit)==11)return 0;
    return ffta_original_viking_compatibility(unit,effect);
}

static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
static unsigned reaving_strike(unsigned action) { return action==FFTA_VIK_A3 || action==FFTA_VIK_A6; }
extern unsigned ffta_primary_weapon(const uint8_t *);
extern unsigned ffta_previous_physical_eligibility(const uint8_t *);
extern int ffta_previous_physical_magnitude(const uint8_t *);
extern int ffta_viking_shared_final(int,unsigned,const uint8_t *,const uint8_t *);
extern unsigned ffta_exposed_incoming_numerator(int,const uint8_t *);
extern unsigned ffta_poise_hp_factor(const uint8_t *,const uint8_t *,unsigned);
extern unsigned ffta_blade_ward_factor(const uint8_t *,const uint8_t *);
extern int ffta_previous_exposed_native_stage(int,const uint8_t *);

static unsigned axe(const uint8_t *unit) {
    unsigned weapon=ffta_primary_weapon(unit);
    return weapon && ((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(weapon,3)==31;
}
/* Added rider prediction restores both native scratch context and RNG. The
 * actual result path uses the authenticated exact-recipient HP ledger. */
unsigned ffta_viking_rider_eligible(const uint8_t *context) {
    const uint8_t *actor=*(const uint8_t *const *)context;
    const uint8_t *target=*(const uint8_t *const *)(context+4);
    const uint8_t *recipient=*(const uint8_t *const *)(context+8);
    unsigned action=half(context+12);
    if(!actor || !target || !ffta_previous_physical_eligibility(context))return 0;
    if(!(context[0x26]&0x10) && ffta_action_phase()==FFTA_ACTION_RESULT && ffta_action_id()==action)
        return recipient && ffta_action_hp_lost(recipient)>0;
    uint8_t query[0x34],saved_context[0x34];
    volatile uint8_t *native_context=(volatile uint8_t *)0x0200f3f0u;
    for(unsigned i=0;i<sizeof(query);i++) { query[i]=context[i];saved_context[i]=native_context[i]; }
    query[0x26]|=0x10;query[0x28]=0;
    *(const uint8_t **)(query+0x30)=(const uint8_t *)0x09260000u+63*4;
    volatile uint32_t *rng=(volatile uint32_t *)0x030034b0u;uint32_t saved=*rng;
    unsigned damages=ffta_previous_physical_magnitude(query)>0;
    if(damages && ((unsigned (*)(const uint8_t *))0x0812e6a5u)(target)==13 &&
       ((unsigned (*)(const uint8_t *,const uint8_t *,unsigned,unsigned))0x0812e6e1u)(actor,target,action,13))damages=0;
    *rng=saved;
    for(unsigned i=0;i<sizeof(saved_context);i++)native_context[i]=saved_context[i];
    return damages;
}
unsigned ffta_viking_physical_eligibility(const uint8_t *context) {
    unsigned action=half(context+12);
    if(action==FFTA_ABSORB_ACTION || action==FFTA_GIL_SNAPPER_ACTION)return ffta_viking_reaction_eligibility(context);
    if((action==FFTA_VIK_A5 || action==FFTA_VIK_A8) && context[0x28])return ffta_viking_rider_eligible(context);
    if(reaving_strike(action) && !axe(*(const uint8_t *const *)context))return 0;
    if(action==FFTA_VIK_A4 || action==FFTA_VIK_A9) {
        const uint8_t *actor=*(const uint8_t *const *)context;
        const uint8_t *target=*(const uint8_t *const *)(context+4);
        if(!actor || !target)return 0;
        unsigned enemy=((actor[0x29]>>7)^((actor[0xeb]>>5)&1u))!=(target[0x29]>>7);
        if((action==FFTA_VIK_A4 && enemy) || (action==FFTA_VIK_A9 && !enemy))return 0;
    }
    return ffta_previous_physical_eligibility(context);
}
int ffta_viking_physical_magnitude(const uint8_t *context) {
    if(reaving_strike(half(context+12)) && !axe(*(const uint8_t *const *)context))return 0;
    return ffta_previous_physical_magnitude(context);
}
extern unsigned ffta_viking_outgoing_numerator(const uint8_t *,const uint8_t *,unsigned);
extern int ffta_viking_direct_stage(int,const uint8_t *);
int ffta_viking_physical_final(int reference,unsigned action,const uint8_t *actor,const uint8_t *target) {
    if(!reaving_strike(action))return ffta_viking_shared_final(reference,action,actor,target);
    int64_t signed_reference=reference;
    uint64_t magnitude=(uint64_t)(reference<0?-signed_reference:signed_reference);
    unsigned numerator=action==FFTA_VIK_A3?85:100;
    unsigned incoming=reference>0?ffta_exposed_incoming_numerator(reference,target):5;
    unsigned poise=reference>0?ffta_poise_hp_factor(actor,target,action):4;
    unsigned ward=reference>0?ffta_blade_ward_factor(actor,target):20;
    magnitude=magnitude*numerator*incoming*poise*ward*(reference>0?ffta_viking_outgoing_numerator(actor,target,action):1000)/40000000u;
    if(magnitude>0x7fffffffu)magnitude=0x7fffffffu;
    return reference<0?-(int)magnitude:(int)magnitude;
}
int ffta_viking_exposed_native_stage(int damage,const uint8_t *context) {
    if(context && reaving_strike(half(context+12)))return damage;
    return ffta_viking_direct_stage(damage,context);
}

/* Each native theft stage executes with the ORIGINAL Steal action ID for
 * its independent accuracy, item slot/protection and depletion transaction.
 * Restore the calling action after the callback; later HP damage sees the
 * actual resulting equipment and its own ordinary A accuracy. No generic S
 * roll, invented loot, refunded miss or replayed depleted item is added.
 */
static unsigned theft(uint8_t *context,uintptr_t callback) {
    unsigned action=half(context+12);
    unsigned mapped=reaving_strike(action) && context[0x28]==0;
    if(mapped) {
        unsigned donor=action==FFTA_VIK_A3?165:163;
        context[12]=(uint8_t)donor;context[13]=(uint8_t)(donor>>8);
    }
    unsigned result=((unsigned (*)(uint8_t *))callback)(context);
    if(mapped) { context[12]=(uint8_t)action;context[13]=(uint8_t)(action>>8); }
    return result;
}
unsigned ffta_viking_theft_eligibility(uint8_t *context) {
    if(reaving_strike(half(context+12)) && !axe(*(const uint8_t *const *)context))return 0;
    return theft(context,VIK_NATIVE_THEFT_ELIGIBILITY);
}
unsigned ffta_viking_theft_accuracy(uint8_t *context) { return theft(context,VIK_NATIVE_THEFT_ACCURACY); }
unsigned ffta_viking_theft_accessory(uint8_t *context) { return theft(context,VIK_NATIVE_THEFT_ACCESSORY); }
unsigned ffta_viking_theft_armor(uint8_t *context) { return theft(context,VIK_NATIVE_THEFT_ARMOR); }
unsigned ffta_viking_theft_apply(uint8_t *context) { return theft(context,VIK_NATIVE_THEFT_APPLY); }
