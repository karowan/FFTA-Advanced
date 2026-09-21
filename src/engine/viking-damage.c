#include <stdint.h>
#include "action-snapshot.h"
#include "viking-state.h"
#include "registry.h"
extern unsigned ffta_exposed_native_physical(const uint8_t *);
extern unsigned ffta_exposed_incoming_numerator(int,const uint8_t *);
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
/* Caller establishes a direct HP stage, excluding fixed/percentage, recovery,
 * self-costs, items and combos before applying this common denominator1000. */
unsigned ffta_viking_outgoing_numerator(const uint8_t *actor,const uint8_t *target,unsigned action) {
    (void)action;
    if(!actor || !target || ffta_action_origin()==FFTA_ACTION_NATIVE_REACTION)return 1000;
    unsigned a=ffta_action_unit_flags(actor),t=ffta_action_unit_flags(target);
    /* Damage to MP is a resource interception, not direct HP damage. Known
     * native selection is authoritative. Prediction uses the same positive-HP
     * admission subset as Poise, without recursively evaluating magnitude. */
    if((t&8u) && (t&16u))return 1000;
    if(!(t&8u) && actor!=target && action!=265 &&
       ((unsigned (*)(const uint8_t *))0x0812e6a5u)(target)==13 &&
       ((unsigned (*)(const uint8_t *,unsigned))0x080c7ea5u)(target,0x15) &&
       (!action || !((unsigned (*)(unsigned,unsigned))0x080ccd51u)(action,17)))return 1000;
    unsigned opportunist=(a&FFTA_ACTION_FLAG_OPPORTUNIST) && (t&FFTA_ACTION_FLAG_HARMFUL) &&
        (((a>>7)^(a>>8))&1u)!=((t>>7)&1u);
    unsigned challenger=(a&FFTA_VIK_CHALLENGER_MASK)>>FFTA_VIK_CHALLENGER_SHIFT;
    unsigned challenged=challenger && ffta_job_origin(target)!=challenger;
    return (opportunist?13u:10u)*(challenged?7u:10u)*10u;
}
static int physical(int damage,const uint8_t *actor,const uint8_t *target,unsigned action) {
    if(damage<=0)return damage;
    uint64_t product=(uint64_t)(unsigned)damage*ffta_exposed_incoming_numerator(damage,target)*
        ffta_poise_hp_factor(actor,target,action)*ffta_blade_ward_factor(actor,target)*
        ffta_viking_outgoing_numerator(actor,target,action)/400000u;
    return product>999u?999:(int)product;
}
static unsigned custom(unsigned action) {
    return (action>=347 && action<=355) || action==357 || action==358 ||
        action==FFTA_VIK_A3 || action==FFTA_VIK_A6 || (action>=424 && action<=431);
}
int ffta_viking_direct_stage(int damage,const uint8_t *context) {
    if(damage<=0 || !context)return damage;
    unsigned action=half(context+12);
    if(custom(action))return damage;
    const uint8_t *actor=*(const uint8_t *const *)context;
    const uint8_t *target=*(const uint8_t *const *)(context+8);
    if(ffta_exposed_native_physical(context))return physical(damage,actor,target,action);
    const uint8_t *d=*(const uint8_t *const *)(context+0x30);
    if(!d || ((const uint8_t *)0x083a87b0u)[d[1]*12u+4]!=1 ||
       !((unsigned (*)(unsigned,unsigned))0x080ccd51u)(action,28) ||
       (d[3]!=30 && d[3]!=39 && d[3]!=43))return damage;
    return (int)((uint64_t)(unsigned)damage*ffta_poise_hp_factor(actor,target,action)*
        ffta_viking_outgoing_numerator(actor,target,action)/4000u);
}
extern int ffta_viking_original_exposed_preview(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned,unsigned);
int ffta_viking_exposed_preview(const uint8_t *actor,const uint8_t *target,unsigned action,
    unsigned item,unsigned index,unsigned mode) {
    FFTA_ActionSnapshot snapshot;
    unsigned opened=ffta_snapshot_begin(&snapshot,actor,target,0);
    int damage=ffta_viking_original_exposed_preview(actor,target,action,item,index,mode);
    if((uint16_t)action==0)damage=physical(damage,actor,target,(uint16_t)action);
    if(opened)ffta_snapshot_end(&snapshot);
    return damage;
}
