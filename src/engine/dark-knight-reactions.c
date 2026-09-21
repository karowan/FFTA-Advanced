#include <stdint.h>
#include "action-snapshot.h"
#include "dark-knight-state.h"
#define TBN_CLAIM 32u
#define DARK_WARD_CLAIM 64u
#define VENGEANCE_CLAIM 128u
/* Shared queue prerequisite supplies immutable authenticated request metadata. */
extern const uint8_t *ffta_action_unit_at(unsigned);
extern unsigned ffta_action_reaction_kind(void);
extern unsigned ffta_action_reaction_value(void);
extern unsigned ffta_reaction_queue_append(unsigned *,const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned);
extern unsigned ffta_drk_direct_kind(const uint8_t *);
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
static unsigned alive(const uint8_t *p) { return p && half(p+0x18) && !(p[0xe8]&0x40u); }
static unsigned ready(const uint8_t *p) {
    return alive(p) && !((unsigned (*)(const uint8_t *))0x080c8281u)(p) &&
        ((unsigned (*)(const uint8_t *,unsigned))0x08133addu)(p+0xe8,5);
}
static unsigned retaliation_range(const uint8_t *a,const uint8_t *t) {
    /* Completion only: these are the exact current recipient and initiator
     * positions also copied into the native queue request. This is never a
     * prospective AI/Move query or a live-unit lookup by source identity. */
    int dx=(int)a[0xf6]-(int)t[0xf6],dy=(int)a[0xf7]-(int)t[0xf7];
    return (unsigned)(dx<0?-dx:dx)+(unsigned)(dy<0?-dy:dy)<=3u;
}
static unsigned hostile(const uint8_t *a,const uint8_t *t) {
    unsigned af=ffta_action_unit_flags(a),tf=ffta_action_unit_flags(t);
    return a && t && a!=t && !(tf&4u) && ((((af>>7)^(af>>8))&1u)!=((tf>>7)&1u));
}
void ffta_drk_hp_loss(uint8_t *unit,unsigned before,unsigned after) {
    const uint8_t *actor=ffta_action_actor();
    if(before<=after || ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY || !hostile(actor,unit))return;
    unsigned flags=ffta_action_unit_flags(unit);
    const uint8_t *context=(const uint8_t *)0x0200f3f0u;
    /* Fight's dedicated executor does not initialize the global descriptor
     * context. Its direct writer is independently authenticated upstream. */
    unsigned kind=!ffta_action_id()?1:
        (half(context+12)==ffta_action_id()?ffta_drk_direct_kind(context):0);
    if(kind && (flags&FFTA_DRK_TBN))ffta_action_claim(unit,TBN_CLAIM);
    if(!ffta_action_reactions_enabled())return;
    if(kind==2 && (flags&(1u<<27)))ffta_action_claim(unit,DARK_WARD_CLAIM);
    /* Unlike damage supports, this reaction's approved direct HP-loss trigger
     * is not restricted to scaling formulas. Scope excludes poison/selfcosts,
     * combo and recursive/reflected/reaction objects independently. */
    if(flags&(1u<<28))ffta_action_claim(unit,VENGEANCE_CLAIM);
}
void ffta_drk_reaction_queue(unsigned *frame) {
    const uint8_t *actor=ffta_action_actor();
    if(ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY)return;
    for(unsigned index=0;index<64;++index) {
        uint8_t *unit=(uint8_t *)ffta_action_unit_at(index);if(!unit)break;
        if(ffta_action_claimed(unit,TBN_CLAIM)) {
            uint8_t *state=ffta_job_state(unit);if(state) { state[1]=0;state[2]=0; }
        }
        if(!ready(unit) || !hostile(actor,unit))continue;
        if(ffta_action_claimed(unit,DARK_WARD_CLAIM) && !ffta_action_claimed(unit,FFTA_DRK_DARK_WARD_QUEUED)) {
            if(ffta_reaction_queue_append(frame,unit,unit,433,130,0))ffta_action_claim(unit,FFTA_DRK_DARK_WARD_QUEUED);
        }
        if(ffta_action_claimed(unit,VENGEANCE_CLAIM) && !ffta_action_claimed(unit,FFTA_DRK_VENGEANCE_QUEUED) && alive(actor) && retaliation_range(unit,actor)) {
            unsigned amount=ffta_action_hp_lost(unit)/2u,cap=half(unit+0x1a)/4u;
            if(amount>cap)amount=cap;
            if(amount && ffta_reaction_queue_append(frame,unit,actor,434,131,amount))ffta_action_claim(unit,FFTA_DRK_VENGEANCE_QUEUED);
        }
    }
}
int ffta_drk_reaction_magnitude(const uint8_t *context) {
    if(half(context+12)!=434 || ffta_action_reaction_kind()!=131)return 0;
    const uint8_t *target=*(const uint8_t *const *)(context+4);
    if(!alive(target))return 0;
    unsigned value=ffta_action_reaction_value();
    unsigned affinity=((unsigned (*)(const uint8_t *,unsigned))0x080c7ea5u)(target,0x12);
    unsigned equipment=((unsigned (*)(const uint8_t *,unsigned,unsigned))0x0812fa91u)(target,8,0);
    if(equipment)affinity=((unsigned (*)(unsigned))0x0812fc75u)(equipment);
    /* Native physical elemental dispatch130022:0 weak,1 normal,2 immune,
     *3 absorb,4 half. Fixed retaliation does not repeat offensive supports,
     * weapon attack, defense, Protect/Shell, criticals or random variance. */
    if(affinity==2)return 0;
    if(affinity==3)return -(int)value;
    if(affinity==0)return (int)(value*3u/2u);
    if(affinity==4)return (int)(value/2u);
    return (int)value;
}
