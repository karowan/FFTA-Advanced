#include "native-unit.h"
#include "bard.h"
#include "registry.h"
#include "job-state.h"
#include "action-snapshot.h"
#include "reaction-queue.h"
extern unsigned ffta_viking_reaction_ready(const uint8_t *);
extern unsigned ffta_integrated_direct_kind(const uint8_t *);
extern unsigned ffta_recuperation_numerator(const uint8_t *,const uint8_t *);
extern unsigned ffta_centered_active(const uint8_t *);
extern unsigned ffta_drk_tbn(const uint8_t *);
extern unsigned ffta_drk_last_resort(const uint8_t *);
extern unsigned ffta_viking_war_cry(const uint8_t *);
extern unsigned ffta_inoculated_active(const uint8_t *);
extern uint8_t *ffta_bard_original_application(uint8_t *,unsigned);
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static unsigned support(const uint8_t *u){return u?((unsigned (*)(const uint8_t *))0x080cd50du)(u):0;}
static unsigned reaction(const uint8_t *u){return u?((unsigned (*)(const uint8_t *))0x080cd4d5u)(u):0;}
static unsigned alive(const uint8_t *u){return u && half(u+0x18) && !(u[0xe8]&0x40u);}
static unsigned own_turn(const uint8_t *u){
 const uint8_t *manager=*(const uint8_t *const *)0x0200f438u;
 return manager && *(const uint8_t *const *)(manager+24)==u;
}
static unsigned enemy(const uint8_t *a,const uint8_t *t){
 unsigned af=ffta_action_unit_flags(a),tf=ffta_action_unit_flags(t);
 return a && t && a!=t && !(tf&4u) && ((((af>>7)^(af>>8))&1u)!=((tf>>7)&1u));
}
/* Moogle's legal original incantations: Black Magic23..32 and Time Magic
 *34..42 (37 is empty). Song has seven incanted actions; Hide is excluded.
 * Stunt, Gunmanship, Animism, Item and martial MP techniques are not spells.
 * No cross-race command or lesson access is added by this classification. */
unsigned ffta_bard_incanted(unsigned action){
 return (action>=23 && action<=42 && action!=33 && action!=37) ||
        (action>=FFTA_BRD_A1 && action<=FFTA_BRD_A8 && action!=FFTA_BRD_A6);
}
unsigned ffta_bard_clear_voice(const uint8_t *u){return support(u)==FFTA_BRD_S2;}
unsigned ffta_bard_passive_flags(const uint8_t *u){
 if(!alive(u))return 0;
 unsigned value=support(u)==FFTA_BRD_S1?FFTA_BARD_ENCOURAGEMENT:0,r=reaction(u);
 if(u[0xeb]&0x30u)value|=FFTA_BARD_FORCED;
 const uint8_t *s=ffta_job_state((uint8_t *)u);
 if(r==FFTA_BRD_R1 && s && (s[11]&1u))value|=FFTA_BARD_CHARGED;
 if(ffta_viking_reaction_ready(u)){
  if(r==FFTA_BRD_R1)value|=FFTA_BARD_BOOST_READY;
  if(r==FFTA_BRD_R2 && !(u[0xeb]&8u))value|=FFTA_BARD_ENCORE_READY;
 }
 return value;
}
unsigned ffta_bard_magick_numerator(const uint8_t *a,unsigned action){
 return a && !(ffta_action_unit_extra_flags(a)&FFTA_BARD_FORCED) && ffta_bard_incanted(action) && ffta_action_origin()!=FFTA_ACTION_NATIVE_REACTION &&
  ffta_action_origin()!=FFTA_ACTION_EXPLICIT_COMBO &&
  (ffta_action_unit_extra_flags(a)&FFTA_BARD_CHARGED)?13:10;
}
static void clear_haste(uint8_t *u);
void ffta_bard_passive_event(uint8_t *u,unsigned event){
 uint8_t *s=ffta_job_state(u);if(!s)return;
 if((event>=2 && event<=5)||event==7){if(s[11]&28u)clear_haste(u);s[11]=0;}
 else if(event==8 && reaction(u)!=FFTA_BRD_R1)s[11]&=(uint8_t)~3u;
}
static void clear_haste(uint8_t *u){
 /* Native Haste21 is a single shared status, not a second speed multiplier. */
 u[0xea]&=(uint8_t)~0x20u;
}
void ffta_bard_passive_turn_end(uint8_t *u){
 uint8_t *s=ffta_job_state(u);if(!s)return;
 if(s[11]&2u)s[11]&=(uint8_t)~2u;else s[11]&=(uint8_t)~1u;
 unsigned timer=(s[11]>>2)&7u;
 if(timer&4u)timer&=3u;else if(timer)timer--;
 if(!timer && (s[11]&28u))clear_haste(u);
 s[11]=(uint8_t)((s[11]&~28u)|(timer<<2));
}
void ffta_bard_action_event(const uint8_t *u,unsigned action,unsigned event){
 if(u && !(ffta_action_unit_extra_flags(u)&FFTA_BARD_FORCED) && event==3 && ffta_action_origin()==FFTA_ACTION_NATIVE_PRIMARY && ffta_action_paid_count() && ffta_bard_incanted(action)){
  uint8_t *s=ffta_job_state((uint8_t *)u);if(s)s[11]&=(uint8_t)~3u;
 }
}
void ffta_bard_hp_loss(uint8_t *u,unsigned before,unsigned after){
 const uint8_t *a=ffta_action_actor();
 if(before<=after || !alive(u) || ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY ||
    !ffta_action_reactions_enabled() || !enemy(a,u))return;
 unsigned flags=ffta_action_unit_extra_flags(u),action=ffta_action_id();
 const uint8_t *context=(const uint8_t *)0x0200f3f0u;
 unsigned kind=!action?1:half(context+12)==action?ffta_integrated_direct_kind(context):0;
 if(flags&FFTA_BARD_BOOST_READY)ffta_action_claim_extra(u,FFTA_BARD_BOOST_ADMITTED);
 if(kind==1 && (flags&FFTA_BARD_ENCORE_READY))ffta_action_claim_extra(u,FFTA_BARD_ENCORE_ADMITTED);
}
#include "geomancer.h"
static unsigned tags(const uint8_t *u){
 if(!alive(u))return 0;
 /* Verified persistent native setters: Auto-Life, Regen, Astra, Reflect,
  * Invisible, Defense, Boost, Advice, Haste, Shell, Protect and stat buffs.
  * Immediate Quick/Smile status1 and remedies never appear in this list. */
 static const uint8_t bits[]={2,3,4,5,12,13,14,16,21,24,25,35,37,39,41};
 unsigned value=0;for(unsigned i=0;i<sizeof(bits);i++)if(u[0xe8+bits[i]/8]&(1u<<(bits[i]%8)))value|=1u<<i;
 if(ffta_bard_buff(u,0))value|=1u<<15;
 if(ffta_bard_buff(u,1))value|=1u<<16;
 if(ffta_inoculated_active(u))value|=1u<<17;
 if(ffta_drk_tbn(u))value|=1u<<18;
 if(ffta_viking_war_cry(u))value|=1u<<19;
 if(ffta_centered_active(u))value|=1u<<20;
 if(ffta_drk_last_resort(u))value|=1u<<21;
 if(ffta_geo_updraft(u,0))value|=1u<<22;
 if(ffta_geo_updraft(u,1))value|=1u<<23;
 if(ffta_geo_steady(u))value|=1u<<24;
 return value;
}
uint8_t *ffta_bard_application(uint8_t *c){
 const uint8_t *d=*(const uint8_t *const *)(c+0x30);unsigned application=d[1];
 uint8_t *t=*(uint8_t **)(c+8);const uint8_t *a=*(const uint8_t *const *)c;
 unsigned real=!(c[0x26]&16u) && ffta_action_phase()==FFTA_ACTION_RESULT;
 unsigned eligible=real && ffta_action_origin()==FFTA_ACTION_NATIVE_PRIMARY && ffta_action_paid_count() &&
  (ffta_action_unit_extra_flags(a)&FFTA_BARD_ENCOURAGEMENT) && a!=t &&
  !(ffta_action_unit_flags(t)&4u) && !enemy(a,t) && !(ffta_action_unit_extra_flags(a)&FFTA_BARD_FORCED) && !ffta_native_undead(t);
 unsigned before=eligible?tags(t):0;
 uint8_t *result=ffta_bard_original_application(c,application);
 if(eligible && (tags(t)&~before))ffta_action_claim_extra(t,FFTA_BARD_ENCOURAGE_ADMITTED);
 /* An ordinary Haste refresh replaces Encore's custom expiry with native
  * duration. The hidden Encore callback is separately owned below. */
 if(real && application==52 && (t[0xea]&0x20u)){
  uint8_t *s=ffta_job_state(t);if(s)s[11]&=(uint8_t)~28u;
 }
 return result;
}
void ffta_bard_queue(unsigned *frame){
 const uint8_t *a=ffta_action_actor();
 if(ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY || !a)return;
 for(unsigned i=0;i<64;i++){
  uint8_t *u=(uint8_t *)ffta_action_unit_at(i);if(!u)break;
  unsigned f=ffta_action_unit_extra_flags(u);if(!alive(u))continue;
  if((f&FFTA_BARD_ENCOURAGE_ADMITTED) && !(f&FFTA_BARD_ENCOURAGE_QUEUED)){
   unsigned amount=half(u+0x1a)*15u;if(amount>6000)amount=6000;
   amount=amount*ffta_recuperation_numerator(a,u)/200u;
   /* Recipient owns the separate healing presentation; payload already
    * contains the sole incoming modifier, never an outgoing charge. */
   if(ffta_reaction_queue_append(frame,u,u,FFTA_BARD_ENCOURAGE_ACTION,FFTA_BARD_ENCOURAGE_KIND,amount))
    ffta_action_claim_extra(u,FFTA_BARD_ENCOURAGE_QUEUED);
  }
  if((f&FFTA_BARD_REACTION_QUEUED) || !ffta_viking_reaction_ready(u))continue;
  unsigned action=0,kind=0;
  if((f&FFTA_BARD_BOOST_ADMITTED) && reaction(u)==FFTA_BRD_R1){action=FFTA_BARD_BOOST_ACTION;kind=FFTA_BARD_BOOST_KIND;}
  if((f&FFTA_BARD_ENCORE_ADMITTED) && reaction(u)==FFTA_BRD_R2 && !(u[0xeb]&8u)){action=FFTA_BARD_ENCORE_ACTION;kind=FFTA_BARD_ENCORE_KIND;}
  if(action && ffta_reaction_queue_append(frame,u,u,action,kind,0))ffta_action_claim_extra(u,FFTA_BARD_REACTION_QUEUED);
 }
}
unsigned ffta_bard_reaction_eligibility(const uint8_t *c){
 if(!c || (c[0x26]&16u))return 0;
 const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+4);
 unsigned action=half(c+12),kind=ffta_action_reaction_kind();
 if(a!=t || !alive(t))return 0;
 if(action==FFTA_BARD_ENCOURAGE_ACTION)return kind==FFTA_BARD_ENCOURAGE_KIND && !ffta_native_undead(t);
 if(!ffta_viking_reaction_ready(t))return 0;
 return (action==FFTA_BARD_BOOST_ACTION && kind==FFTA_BARD_BOOST_KIND && reaction(t)==FFTA_BRD_R1) ||
  (action==FFTA_BARD_ENCORE_ACTION && kind==FFTA_BARD_ENCORE_KIND && reaction(t)==FFTA_BRD_R2 && !(t[0xeb]&8u));
}
int ffta_bard_reaction_magnitude(const uint8_t *c){
 if(!ffta_bard_reaction_eligibility(c)||half(c+12)!=FFTA_BARD_ENCOURAGE_ACTION)return 0;
 const uint8_t *t=*(const uint8_t *const *)(c+4);unsigned amount=ffta_action_reaction_value();
 unsigned missing=half(t+0x1a)>half(t+0x18)?half(t+0x1a)-half(t+0x18):0;
 return (int)(amount<missing?amount:missing);
}
uint8_t *ffta_bard_reaction_apply(uint8_t *c){
 if(!ffta_bard_reaction_eligibility(c))return c;
 uint8_t *u=*(uint8_t **)c,*s=ffta_job_state(u);if(!s)return c;
 if(half(c+12)==FFTA_BARD_BOOST_ACTION)s[11]=(uint8_t)((s[11]&~3u)|1u|(own_turn(u)?2u:0));
 else if(half(c+12)==FFTA_BARD_ENCORE_ACTION){
  ((uint8_t *(*)(uint8_t *))0x08132bc5u)(c);
  s[11]=(uint8_t)((s[11]&~28u)|((2u|(own_turn(u)?4u:0u))<<2));
 }
 return c;
}
extern int ffta_drk_mp_cost(const uint8_t *,unsigned);
int ffta_bard_mp_cost(const uint8_t *u,unsigned action){
 int cost=ffta_drk_mp_cost(u,action);
 return cost>0 && ffta_bard_clear_voice(u) && ffta_bard_incanted(action)?(cost*3+3)/4:cost;
}
extern unsigned ffta_viking_compatibility(uint8_t *,unsigned);
unsigned ffta_bard_compatibility(uint8_t *u,unsigned effect){
 if(effect==26 && ffta_geo_steady(u))return 0;
 return effect==56 && ffta_bard_clear_voice(u)?0:ffta_viking_compatibility(u,effect);
}
extern unsigned ffta_chemist_status_gate(const uint8_t *,unsigned,unsigned,unsigned *);
unsigned ffta_bard_status_gate(const uint8_t *c,unsigned status,unsigned caller,unsigned *frame){
 if(status==27 && c && ffta_bard_clear_voice(*(const uint8_t *const *)(c+8))){
  if(caller==0x08132c71u){frame[9]=0x08132c8bu;return 1;}
  if(caller==0x081327d7u){frame[7]=(frame[7]-1u)&255u;frame[9]=0x081327e9u;return 1;}
 }
 return ffta_chemist_status_gate(c,status,caller,frame);
}
