#include <stdint.h>
#include "action-snapshot.h"
#include "registry.h"
#include "dark-knight-state.h"
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
extern unsigned ffta_drk_hp_cost(const uint8_t *,unsigned);
static unsigned low(const uint8_t *unit,unsigned cost) {
    if(!unit || half(unit+0x18)<=cost)return 0;
    return (half(unit+0x18)-cost)*100u<=half(unit+0x1a)*35u;
}
unsigned ffta_drk_snapshot_flags(const uint8_t *unit) {
    if(!unit)return 0;
    unsigned result=0;
    if(((unsigned (*)(const uint8_t *))0x080cd50du)(unit)==FFTA_DRK_S1)
        result=FFTA_ACTION_FLAG_DESPERATION|(low(unit,0)?FFTA_ACTION_FLAG_DESPERATION_ACTIVE:0);
    if(ffta_drk_last_resort(unit))result|=FFTA_DRK_LAST_RESORT;
    if(ffta_drk_tbn(unit))result|=FFTA_DRK_TBN;
    unsigned reaction=((unsigned (*)(const uint8_t *))0x080cd4d5u)(unit);
    if((reaction==FFTA_DRK_R1 || reaction==FFTA_DRK_R2) &&
       !((unsigned (*)(const uint8_t *))0x080c8281u)(unit) &&
       ((unsigned (*)(const uint8_t *,unsigned))0x08133addu)(unit+0xe8,5))
        result|=1u<<(reaction==FFTA_DRK_R1?27:28);
    return result;
}
void ffta_drk_action_event(const uint8_t *actor,unsigned action,unsigned event) {
    if(event==1 && (ffta_action_unit_flags(actor)&FFTA_ACTION_FLAG_DESPERATION))
        ffta_action_set_actor_flags(FFTA_ACTION_FLAG_DESPERATION_ACTIVE,
            low(actor,0)?FFTA_ACTION_FLAG_DESPERATION_ACTIVE:0);
    if(event==3 && action==FFTA_DRK_A5 && ffta_action_paid_count() &&
       ffta_action_origin()==FFTA_ACTION_NATIVE_PRIMARY)
        ffta_drk_grant_last_resort((uint8_t *)actor,1);
}
/* Caller has established a positive direct HP stage. Preserve native MP
 * interception unscaled, including its already-resolved actual selection. */
static unsigned hp_payable(const uint8_t *actor,const uint8_t *target,unsigned action) {
    unsigned flags=ffta_action_unit_flags(target);
    if(flags&8u)return !(flags&16u);
    return !(actor && target && actor!=target && action!=265 &&
        ((unsigned (*)(const uint8_t *))0x0812e6a5u)(target)==13 &&
        ((unsigned (*)(const uint8_t *,unsigned))0x080c7ea5u)(target,0x15) &&
        (!action || !((unsigned (*)(unsigned,unsigned))0x080ccd51u)(action,17)));
}
unsigned ffta_drk_outgoing_numerator(const uint8_t *actor,const uint8_t *target,unsigned action,unsigned physical) {
    if(!actor || !target || ffta_action_origin()==FFTA_ACTION_NATIVE_REACTION ||
       !hp_payable(actor,target,action))return 8;
    unsigned flags=ffta_action_unit_flags(actor),active=0;
    if(flags&FFTA_ACTION_FLAG_DESPERATION) {
        active=flags&FFTA_ACTION_FLAG_DESPERATION_ACTIVE;
        if(ffta_action_phase()==FFTA_ACTION_QUERY)active=low(actor,ffta_drk_hp_cost(actor,action));
    }
    return (active?3u:2u)*((physical && (flags&FFTA_DRK_LAST_RESORT))?5u:4u);
}
unsigned ffta_drk_incoming_effects(const uint8_t *actor,const uint8_t *target,unsigned action,unsigned physical,unsigned removed) {
    if(!actor || !target || !hp_payable(actor,target,action))return 40;
    unsigned a=ffta_action_unit_flags(actor),t=ffta_action_unit_flags(target)&~removed;
    unsigned reaction=ffta_action_origin()==FFTA_ACTION_NATIVE_REACTION;
    unsigned enemy=actor!=target && !(t&4u) && ((((a>>7)^(a>>8))&1u)!=((t>>7)&1u));
    unsigned last=physical && (t&FFTA_DRK_LAST_RESORT)?6u:5u;
    unsigned ward=!reaction && enemy && (t&FFTA_DRK_TBN)?1u:2u;
    unsigned dark=!physical && !reaction && enemy && (t&(1u<<27)) &&
        (ffta_action_phase()!=FFTA_ACTION_RESULT || ffta_action_reactions_enabled())?3u:4u;
    return last*ward*dark;
}
unsigned ffta_drk_incoming_numerator(const uint8_t *actor,const uint8_t *target,unsigned action,unsigned physical) {
    return ffta_drk_incoming_effects(actor,target,action,physical,0);
}
