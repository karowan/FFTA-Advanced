#include "viking-state.h"
#include "job-state.h"
#include "registry.h"
#include "viking-native.h"

/* Owned byte4: two remaining subsequent turns plus application-turn skip4.
 * Byte5: explicit challenger token1..36. Byte6: awarded gil0..50 this battle.
 * Byte7 is the transient critical HP tally (saturated100), cleared at primary
 * action start/completion and terminating lifecycle events. */
static uint8_t *state(const uint8_t *unit) {
    return ffta_job_state((uint8_t *)unit);
}
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
static unsigned alive(const uint8_t *unit) {
    return unit && half(unit+0x18) && !(unit[0xe8]&0x40u);
}
static unsigned hostile(const uint8_t *actor,const uint8_t *target) {
    return actor && target && actor!=target &&
        (((actor[0x29]>>7)^((actor[0xeb]>>5)&1u))!=(target[0x29]>>7));
}
unsigned ffta_viking_war_cry(const uint8_t *unit) {
    uint8_t *s=state(unit);
    return s && (s[4]&3u) && (s[4]&3u)<=2 && s[4]<=6;
}
unsigned ffta_viking_challenger(const uint8_t *unit) {
    uint8_t *s=state(unit);
    return s && s[5]<=36 ? s[5] : 0;
}
void ffta_viking_grant_war_cry(uint8_t *unit,unsigned own_turn) {
    uint8_t *s=state(unit);
    if(s && alive(unit))s[4]=(uint8_t)(2u|(own_turn?4u:0u));
}
unsigned ffta_viking_grant_challenge(uint8_t *unit,const uint8_t *challenger) {
    uint8_t *s=state(unit);
    unsigned token=ffta_job_origin(challenger);
    if(!s || !alive(unit) || !alive(challenger) || !token || token>36)return 0;
    s[5]=(uint8_t)token;
    return 1;
}
void ffta_viking_turn_end(uint8_t *unit) {
    uint8_t *s=state(unit);
    if(!s)return;
    unsigned value=s[4];
    if((value&3u)>2 || value>6)s[4]=0;
    else if(value&4u)s[4]=(uint8_t)(value&3u);
    else if(value)s[4]=(uint8_t)(value-1);
    /* Provoke has no application-turn exemption: the marked target's next
     * completed turn is its explicit expiry boundary. */
    s[5]=0;
}
void ffta_viking_event(uint8_t *unit,unsigned event) {
    uint8_t *s=state(unit);
    if(!s)return;
    if((event>=2 && event<=5) || event==7)s[4]=0;
    if(event>=2 && event<=6)s[5]=0;
    if(event>=2 && event<=5)s[7]=0;
    /* Losing HP, changing job or being revived cannot reset the gil cap. */
    if(event==4)s[6]=0;
    if(event<2 || event>5)return;
    unsigned token=ffta_job_origin(unit);
    /* Complete strict same-owner cohort, never a live fallback. Duplicate
     * origins in a manager are represented separately and both clear. */
    uint8_t *peers[36];
    unsigned count=ffta_job_peers(unit,peers,36);
    for(unsigned i=0;i<count;i++) {
        uint8_t *other=state(peers[i]);
        if(other && other[5]==token)other[5]=0;
    }
}
unsigned ffta_viking_snapshot_flags(const uint8_t *unit) {
    if(!unit)return 0;
    unsigned result=0;
    /* Poison9, Blind10, Slow22, Sleep26, Silence27, Confuse28,
     * Immobilize30 and Disable31. Other jobs OR their explicit custom tags
     * into harmful bit9 at the common provider composition point. */
    if((unit[0xe9]&6u) || (unit[0xea]&0x40u) ||
       (unit[0xeb]&0xdcu) || ffta_viking_challenger(unit))result|=1u<<9;
    if(((unsigned (*)(const uint8_t *))0x080cd50du)(unit)==FFTA_VIK_S2)
        result|=1u<<10;
    if(ffta_viking_reaction_ready(unit)) {
        unsigned reaction=((unsigned (*)(const uint8_t *))0x080cd4d5u)(unit);
        if(reaction==FFTA_VIK_R1)result|=FFTA_VIK_FLAG_ABSORB_READY;
        if(reaction==FFTA_VIK_R2)result|=FFTA_VIK_FLAG_GIL_READY;
    }
    result|=ffta_viking_challenger(unit)<<FFTA_VIK_CHALLENGER_SHIFT;
    return result;
}
unsigned ffta_viking_gil_award(uint8_t *unit,unsigned actual_hp_lost) {
    uint8_t *s=state(unit);
    if(!s || !alive(unit) || s[6]>=50)return 0;
    unsigned award=actual_hp_lost/2u,remaining=50u-s[6];
    if(award>remaining)award=remaining;
    s[6]=(uint8_t)(s[6]+award);
    return award;
}

/* Native application wrappers are called only after ordinary eligibility,
 * accuracy and compatibility. The dispatcher owns native cure masks. */
uint8_t *ffta_viking_war_cry_apply(uint8_t *context) {
    if(!context || (context[0x26]&0x10u))return context;
    uint8_t *target=*(uint8_t **)(context+8);
    const uint8_t *actor=*(const uint8_t *const *)context;
    if(!actor || !target || hostile(actor,target))return context;
    unsigned origin=ffta_job_origin(actor);
    ffta_viking_grant_war_cry(target,origin && origin==ffta_job_origin(target));
    return context;
}
extern unsigned ffta_chemist_prevent_custom(const uint8_t *,unsigned) __attribute__((weak));
uint8_t *ffta_viking_challenged_apply(uint8_t *context) {
    if(!context)return context;
    uint8_t *target=*(uint8_t **)(context+8);
    const uint8_t *actor=*(const uint8_t *const *)context;
    if(!hostile(actor,target) || !alive(target) ||
       ((unsigned (*)(const uint8_t *))0x080cd50du)(target)==11)return context;
    /* Inoculation precedes Auto-Cureall inside the Chemist provider; native
     * query calls may predict prevention but cannot spend stock or charges. */
    if(ffta_chemist_prevent_custom && ffta_chemist_prevent_custom(context,2))return context;
    if(!(context[0x26]&0x10u))ffta_viking_grant_challenge(target,actor);
    return context;
}

extern void ffta_previous_centered_event(uint8_t *,unsigned);
extern void ffta_previous_centered_turn_end(uint8_t *);
void ffta_viking_lifecycle_event(uint8_t *unit,unsigned event) {
    ffta_previous_centered_event(unit,event);
    ffta_viking_event(unit,event);
}
void ffta_viking_lifecycle_turn_end(uint8_t *unit) {
    ffta_previous_centered_turn_end(unit);
    ffta_viking_turn_end(unit);
}
extern unsigned ffta_original_viking_status_accuracy(const uint8_t *);
unsigned ffta_viking_status_adjust(const uint8_t *context,unsigned chance) {
    if(!chance || !context)return chance;
    const uint8_t *actor=*(const uint8_t *const *)context;
    const uint8_t *target=*(const uint8_t *const *)(context+4);
    const uint8_t *descriptor=*(const uint8_t *const *)(context+0x30);
    if(!hostile(actor,target) || !descriptor || !ffta_viking_war_cry(target))return chance;
    /* Native status4 interception deliberately returns100 for a consuming
     * application, and0 in preview. Preserve that protocol, not just its roll. */
    if(((unsigned (*)(const uint8_t *))0x080cd8fdu)(target))return chance;
    unsigned kind=descriptor[1];
    const uint8_t *application=(const uint8_t *)VIK_APPLICATION_BANK+12u*kind;
    /* Native status application kinds have resource category0 and harmful
     * sign+1. Beneficial Sure effects and original theft are not S attempts. */
    if(kind>=100 || application[4]!=0 || application[8]!=1)return chance;
    return chance>25 ? chance-25 : 0;
}
unsigned ffta_viking_status_accuracy(const uint8_t *context) {
    return ffta_viking_status_adjust(context,ffta_original_viking_status_accuracy(context));
}
