#include "mystic-knight.h"
#include "action-snapshot.h"

/* Readiness is frozen for an incoming action. The claim records its actual
 * successful hit, so misses cannot spend the blade and later hits keep the
 * same reduction after the live enchantment has been consumed. */
static unsigned enemy(const uint8_t *a,const uint8_t *t){
 if(!a || !t || a==t)return 0;
 unsigned af=ffta_action_unit_flags(a),tf=ffta_action_unit_flags(t);
 return !(tf&4u) && ((((af>>7)^(af>>8))&1u)!=((tf>>7)&1u));
}
unsigned ffta_myk_parry_factor(const uint8_t *a,const uint8_t *t,unsigned id){
 /* Original AI evaluates thousands of candidates. Reject the ordinary
  * no-reaction case before resolving both units' expensive job flags. */
 if(id==265 || !(ffta_action_unit_extension_reaction_flags(t)&FFTA_MYK_PARRY_READY) || !enemy(a,t))return 2;
 unsigned origin=ffta_action_origin();
 if(origin==FFTA_ACTION_NATIVE_REACTION || origin==FFTA_ACTION_EXPLICIT_COMBO ||
    !ffta_action_reaction_forecast_enabled())return 2;
 return 1;
}
void ffta_myk_parry_hit(const uint8_t *a,uint8_t *t,unsigned id){
 if(ffta_action_phase()!=FFTA_ACTION_RESULT ||
    ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY ||
    !ffta_action_reactions_enabled() || ffta_myk_parry_factor(a,t,id)!=1)return;
 /* A positive damage requirement would incorrectly preserve fuel on a
  * successful zero-damage hit. The adopted rule spends after accuracy. */
 if(ffta_action_claim_extension(t,FFTA_MYK_PARRY_USED))ffta_myk_clear(t);
}
void ffta_additional_before_fight(const uint8_t *a,uint8_t *t){
 if(ffta_action_id()==0)ffta_myk_parry_hit(a,t,0);
}
