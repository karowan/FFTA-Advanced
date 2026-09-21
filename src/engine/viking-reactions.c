#include <stdint.h>
#include "registry.h"
#include "action-snapshot.h"
#include "job-state.h"
#include "viking-state.h"
#include "reaction-queue.h"
#include "reaction-ids.h"
#include "viking-native.h"
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
unsigned ffta_viking_reaction_ready(const uint8_t *unit) {
    return unit && !((unsigned (*)(const uint8_t *))0x080c8281u)(unit) &&
        ((unsigned (*)(const uint8_t *,unsigned))0x08133addu)(unit+0xe8,5);
}
unsigned ffta_viking_action_category(const uint8_t *actor,unsigned action) {
    (void)actor;action=(uint16_t)action;
    if(!action)return FFTA_ACTION_PHYSICAL;
    if(action>=FFTA_GLOBAL_ACTION_COUNT)return FFTA_ACTION_UNCLASSIFIED;
    unsigned physical=((unsigned (*)(unsigned,unsigned))0x080ccd51u)(action,29);
    unsigned magical=((unsigned (*)(unsigned,unsigned))0x080ccd51u)(action,28);
    if(!physical && !magical)return FFTA_ACTION_UNCLASSIFIED;
    const uint8_t *row=*(const uint8_t *const *)0x080ccd84u+action*28u;
    for(unsigned i=12;i<16;i++) {
        const uint8_t *d=(const uint8_t *)0x09260000u+4u*row[i];
        if(d[1]>=93 || ((const uint8_t *)0x083a87b0u)[12u*d[1]+4]!=1)continue;
        unsigned selector=d[3];
        if(physical && (selector==12 || selector==24 || selector==30 || selector==31 || selector==39 || selector==43 || selector==44 ||
           (action==148 && selector==36) || (action==211 && selector==38)))return FFTA_ACTION_PHYSICAL;
        if(magical && (selector==30 || selector==39 || selector==43))return FFTA_ACTION_MAGICAL;
    }
    return FFTA_ACTION_UNCLASSIFIED;
}
static const uint8_t *recipient_row(const uint8_t *object,const uint8_t *unit) {
    if(!object || object[0x2c0]>15)return 0;
    for(unsigned i=0;i<object[0x2c0];i++) {
        const uint8_t *row=object+0x20+44u*i;
        const uint8_t *wrapper=*(const uint8_t *const *)row;
        if(wrapper && *(const uint8_t *const *)wrapper==unit)return row;
    }
    return 0;
}
extern void ffta_viking_tsunami_hp_loss(uint8_t *);
void ffta_viking_hp_loss(uint8_t *unit,unsigned before,unsigned after) {
    if(before>after && ffta_action_phase()==FFTA_ACTION_RESULT &&
       ffta_action_origin()==FFTA_ACTION_NATIVE_PRIMARY && ffta_action_id()==FFTA_VIK_A8)
        ffta_viking_tsunami_hp_loss(unit);
    if(before<=after || !ffta_action_reactions_enabled() ||
       ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY)return;
    const uint8_t *actor=ffta_action_actor();
    unsigned a=ffta_action_unit_flags(actor),t=ffta_action_unit_flags(unit);
    if(!actor || actor==unit || (((a>>7)^(a>>8))&1u)==((t>>7)&1u))return;
    /* Absorb is triggered by actual direct HP loss, including fixed and
     * percentage attacks. Action categories classify scaling formulas and
     * must not narrow this loss-triggered reaction. The native-primary scope
     * above excludes costs, turn-end damage and recursive reactions. */
    if(t&FFTA_VIK_FLAG_ABSORB_READY)ffta_action_claim(unit,FFTA_VIK_CLAIM_ABSORB);
    if(!(t&FFTA_VIK_FLAG_GIL_READY) || ffta_action_category()!=FFTA_ACTION_PHYSICAL)return;
    const uint8_t *row=recipient_row(ffta_action_result_object(),unit);
    /* Native critical path A29DE..A29E8 sets row+C bit0x20 after the
     * critical formula. Do not infer critical from high damage or RNG. */
    if(!row || !(half(row+0xc)&0x20u))return;
    uint8_t *record=ffta_job_state(unit);if(!record)return;
    unsigned amount=record[7]+before-after;record[7]=(uint8_t)(amount>100?100:amount);
    ffta_action_claim(unit,FFTA_VIK_CLAIM_GIL);
}
void ffta_viking_action_event(const uint8_t *actor,unsigned action,unsigned event) {
    (void)action;
    if(event!=0 && event!=3)return;
    uint8_t *peers[36];unsigned count=ffta_job_peers((uint8_t *)actor,peers,36);
    for(unsigned i=0;i<count;i++) {
        uint8_t *unit=peers[i],*record=ffta_job_state(unit);if(!record)continue;
        record[7]=0;
    }
}
static unsigned gil_available(const uint8_t *unit,unsigned amount) {
    const uint8_t *record=ffta_job_state((uint8_t *)unit);
    unsigned origin=ffta_job_origin(unit);
    if(!record || !origin || origin>24 || (unit[0x29]&128u) || record[6]>=50)return 0;
    unsigned remaining=50u-record[6];if(amount>remaining)amount=remaining;
    unsigned money=*(const volatile uint32_t *)0x02001f64u;
    unsigned capacity=money<99999999u?99999999u-money:0;
    return amount<capacity?amount:capacity;
}
void ffta_viking_reaction_queue(unsigned *frame) {
    if(ffta_action_phase()!=FFTA_ACTION_COMPLETING || ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY)return;
    for(unsigned i=0;i<64;i++) {
        uint8_t *unit=(uint8_t *)ffta_action_unit_at(i);if(!unit)break;
        if(!half(unit+0x18) || !ffta_viking_reaction_ready(unit))continue;
        if(ffta_action_claimed(unit,FFTA_VIK_CLAIM_ABSORB) && !ffta_action_claimed(unit,FFTA_ABSORB_QUEUED)) {
            unsigned amount=ffta_action_hp_lost(unit)*3u/10u,cap=half(unit+0x1a)*15u/100u;
            if(amount>cap)amount=cap;
            unsigned missing=half(unit+0x1a)>half(unit+0x18)?half(unit+0x1a)-half(unit+0x18):0;
            if(amount>missing)amount=missing;
            if(amount && ffta_reaction_queue_append(frame,unit,unit,FFTA_ABSORB_ACTION,FFTA_ABSORB_KIND,amount))
                ffta_action_claim(unit,FFTA_ABSORB_QUEUED);
        }
        if(ffta_action_claimed(unit,FFTA_VIK_CLAIM_GIL) && !ffta_action_claimed(unit,FFTA_GIL_SNAPPER_QUEUED)) {
            const uint8_t *record=ffta_job_state(unit);
            unsigned amount=gil_available(unit,record?record[7]/2u:0);
            if(amount && ffta_reaction_queue_append(frame,unit,unit,FFTA_GIL_SNAPPER_ACTION,FFTA_GIL_SNAPPER_KIND,amount))
                ffta_action_claim(unit,FFTA_GIL_SNAPPER_QUEUED);
        }
    }
}
unsigned ffta_viking_reaction_eligibility(const uint8_t *context) {
    if(!context || (context[0x26]&16u))return 0;
    unsigned action=half(context+12),kind=ffta_action_reaction_kind();
    const uint8_t *actor=*(const uint8_t *const *)context,*target=*(const uint8_t *const *)(context+4);
    if(!actor || actor!=target || !half(actor+0x18) || !ffta_viking_reaction_ready(actor))return 0;
    return (action==FFTA_ABSORB_ACTION && kind==FFTA_ABSORB_KIND) ||
        (action==FFTA_GIL_SNAPPER_ACTION && kind==FFTA_GIL_SNAPPER_KIND);
}
int ffta_viking_zero_magnitude(const uint8_t *context) {
    if(context && half(context+12)==FFTA_ABSORB_ACTION)
        return ffta_viking_reaction_eligibility(context)?(int)ffta_action_reaction_value():0;
    return ((int (*)(const uint8_t *))VIK_NATIVE_ZERO_MAGNITUDE)(context);
}
uint8_t *ffta_viking_gil_reaction_apply(uint8_t *context) {
    if(!ffta_viking_reaction_eligibility(context) || half(context+12)!=FFTA_GIL_SNAPPER_ACTION)return context;
    uint8_t *unit=*(uint8_t **)context;
    unsigned amount=gil_available(unit,ffta_action_reaction_value());
    if(!amount)return context;
    *(volatile uint32_t *)0x02001f64u+=amount;
    uint8_t *record=ffta_job_state(unit);record[6]=(uint8_t)(record[6]+amount);
    /* Native Steal Gil publishes abs(amount)+1 at context+18. A34B4 copies
     * this to row+28/+2A and sets row+C bit1000 for the ordinary presentation.
     * Only the player's award changes: no enemy inventory/gil is debited. */
    context[0x18]=(uint8_t)(amount+1u);context[0x19]=0;
    return context;
}
