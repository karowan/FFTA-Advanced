#include "action-snapshot.h"
#include "viking-state.h"

/* Caller establishes a direct HP stage, excluding fixed/percentage, recovery,
 * self-costs, items and combos before applying this common denominator1000. */
unsigned ffta_viking_outgoing_numerator(const uint8_t *actor,const uint8_t *target,unsigned action) {
    (void)action;
    if(!actor || !target || ffta_action_origin()==FFTA_ACTION_NATIVE_REACTION)return 1000;
    unsigned a=ffta_action_unit_flags_masked(actor,0x180u|FFTA_ACTION_FLAG_OPPORTUNIST|FFTA_VIK_CHALLENGER_MASK),t=ffta_action_unit_flags_masked(target,24u);
    /* Damage to MP is a resource interception, not direct HP damage. Known
     * native selection is authoritative. Prediction uses the same positive-HP
     * admission subset as Poise, without recursively evaluating magnitude. */
    if((t&8u) && (t&16u))return 1000;
    if(!(t&8u) && actor!=target && action!=265 &&
       ((unsigned (*)(const uint8_t *))0x0812e6a5u)(target)==13 &&
       ((unsigned (*)(const uint8_t *,unsigned))0x080c7ea5u)(target,0x15) &&
       (!action || !((unsigned (*)(unsigned,unsigned))0x080ccd51u)(action,17)))return 1000;
    if(a&FFTA_ACTION_FLAG_OPPORTUNIST)t|=ffta_action_unit_flags_masked(target,0x80u|FFTA_ACTION_FLAG_HARMFUL);
    unsigned opportunist=(a&FFTA_ACTION_FLAG_OPPORTUNIST) && (t&FFTA_ACTION_FLAG_HARMFUL) &&
        (((a>>7)^(a>>8))&1u)!=((t>>7)&1u);
    unsigned challenger=(a&FFTA_VIK_CHALLENGER_MASK)>>FFTA_VIK_CHALLENGER_SHIFT;
    unsigned challenged=challenger && ffta_job_origin(target)!=challenger;
    return (opportunist?13u:10u)*(challenged?7u:10u)*10u;
}
