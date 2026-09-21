#include <stdint.h>
#include "registry.h"
#include "action-snapshot.h"
#include "reaction-queue.h"
#include "reaction-ids.h"
#include "samurai-state.h"
#include "bard.h"
extern unsigned ffta_primary_weapon(const uint8_t *);
extern unsigned ffta_viking_reaction_ready(const uint8_t *);
extern unsigned ffta_integrated_direct_kind(const uint8_t *);
extern unsigned ffta_integrated_physical_eligibility(const uint8_t *);
extern int ffta_drk_zero_magnitude(const uint8_t *);
extern int ffta_viking_zero_magnitude(const uint8_t *);
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
static unsigned katana(const uint8_t *unit) {
    unsigned item=ffta_primary_weapon(unit);
    return item && ((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(item,3)==9;
}
static unsigned alive(const uint8_t *unit) { return unit && half(unit+0x18) && !(unit[0xe8]&64u); }
static unsigned adjacent(const uint8_t *a,const uint8_t *t) {
    int dx=(int)a[0xf6]-t[0xf6],dy=(int)a[0xf7]-t[0xf7];
    return (unsigned)(dx<0?-dx:dx)+(unsigned)(dy<0?-dy:dy)==1;
}
static unsigned hostile(const uint8_t *a,const uint8_t *t) {
    if(!a || !t || a==t)return 0;
    unsigned af=ffta_action_unit_flags(a),tf=ffta_action_unit_flags(t);
    return !(tf&4u) && ((((af>>7)^(af>>8))&1u)!=((tf>>7)&1u));
}
unsigned ffta_counter_draw_flags(const uint8_t *unit) {
    return alive(unit) && katana(unit) && ffta_viking_reaction_ready(unit) &&
        ((unsigned (*)(const uint8_t *))0x080cd4d5u)(unit)==FFTA_SAM_R2?FFTA_COUNTER_DRAW_READY:0;
}
void ffta_counter_draw_hp_loss(uint8_t *unit,unsigned before,unsigned after) {
    const uint8_t *actor=ffta_action_actor();
    if(before<=after || !actor)return;
    if(ffta_action_reaction_kind()==FFTA_COUNTER_DRAW_KIND && ffta_action_id()==FFTA_COUNTER_DRAW_ACTION) {
        if(actor!=unit && alive(actor) && katana(actor))ffta_centered_grant((uint8_t *)actor,0);
        return;
    }
    if(ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY || !ffta_action_reactions_enabled() ||
       !(ffta_action_unit_flags(unit)&FFTA_COUNTER_DRAW_READY) || !hostile(actor,unit) || !adjacent(actor,unit))return;
    const uint8_t *context=(const uint8_t *)0x0200f3f0u;
    unsigned kind=!ffta_action_id()?1:half(context+12)==ffta_action_id()?ffta_integrated_direct_kind(context):0;
    if(kind==1)ffta_action_claim(unit,FFTA_COUNTER_DRAW_CLAIM);
}
void ffta_counter_draw_queue(unsigned *frame) {
    const uint8_t *actor=ffta_action_actor();
    if(ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY || !alive(actor))return;
    for(unsigned i=0;i<64;i++) {
        uint8_t *unit=(uint8_t *)ffta_action_unit_at(i);if(!unit)break;
        if(!ffta_action_claimed(unit,FFTA_COUNTER_DRAW_CLAIM) || ffta_action_claimed(unit,FFTA_COUNTER_DRAW_QUEUED) ||
           !alive(unit) || !katana(unit) || !ffta_viking_reaction_ready(unit) || !hostile(actor,unit) || !adjacent(actor,unit))continue;
        if(ffta_reaction_queue_append(frame,unit,actor,FFTA_COUNTER_DRAW_ACTION,FFTA_COUNTER_DRAW_KIND,0))
            ffta_action_claim(unit,FFTA_COUNTER_DRAW_QUEUED);
    }
}
unsigned ffta_counter_draw_eligibility(const uint8_t *context) {
    if(!context || (context[0x26]&16u) || ffta_action_reaction_kind()!=FFTA_COUNTER_DRAW_KIND)return 0;
    const uint8_t *actor=*(const uint8_t *const *)context,*target=*(const uint8_t *const *)(context+4);
    return alive(actor) && alive(target) && adjacent(actor,target) && katana(actor) &&
        ffta_integrated_physical_eligibility(context);
}
int ffta_integrated_zero_magnitude(const uint8_t *context) {
    if(half(context+12)>=FFTA_BARD_ENCOURAGE_ACTION && half(context+12)<=FFTA_BARD_ENCORE_ACTION)return ffta_bard_reaction_magnitude(context);
    return half(context+12)==FFTA_ABSORB_ACTION?ffta_viking_zero_magnitude(context):ffta_drk_zero_magnitude(context);
}
