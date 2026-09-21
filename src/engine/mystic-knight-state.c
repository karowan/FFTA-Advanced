#include "mystic-knight.h"
#include "registry.h"
#include "job-state.h"
#include "action-snapshot.h"
#include "bard.h"
extern unsigned ffta_primary_weapon(const uint8_t *);
extern unsigned ffta_viking_reaction_ready(const uint8_t *);
extern unsigned ffta_integrated_action_category(const uint8_t *,unsigned);
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static void put(uint8_t *p,unsigned n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static unsigned alive(const uint8_t *u){return u && half(u+0x18) && !(u[0xe8]&64u);}
static unsigned support(const uint8_t *u){return u?((unsigned (*)(const uint8_t *))0x080cd50du)(u):0;}
static unsigned reaction(const uint8_t *u){return u?((unsigned (*)(const uint8_t *))0x080cd4d5u)(u):0;}
unsigned ffta_myk_action(unsigned id){return id>=FFTA_MYK_A1 && id<=FFTA_MYK_A14;}
unsigned ffta_myk_strike(unsigned id){return id>=FFTA_MYK_A1 && id<=FFTA_MYK_A12;}
unsigned ffta_myk_weapon(unsigned item){
 if(!item || item>460)return 0;
 unsigned type=((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(item,3);
 return type==8 || type==3; /* Rapier or saber; knives belong to Dance. */
}
unsigned ffta_myk_enchantment(const uint8_t *u){
 const uint8_t *s=ffta_job_state((uint8_t *)u);if(!alive(u)||!s)return 0;
 unsigned v=half(s+FFTA_JOB_MYK_BLADE),kind=v&15u;
 if(!kind || kind>11)return 0;
 unsigned item=ffta_primary_weapon(u);
 return ffta_myk_weapon(item) && ((v>>4)&511u)==item?kind:0;
}
unsigned ffta_myk_sequence(const uint8_t *u){
 const uint8_t *s=ffta_job_state((uint8_t *)u);
 unsigned v=alive(u)&&s&&support(u)==FFTA_MYK_S1?(half(s+FFTA_JOB_MYK_BLADE)>>13)&3u:0;
 return v<=2?v:0;
}
void ffta_myk_clear(uint8_t *u){
 uint8_t *s=ffta_job_state(u);if(s)put(s+FFTA_JOB_MYK_BLADE,half(s+FFTA_JOB_MYK_BLADE)&0x6000u);
}
void ffta_myk_grant(uint8_t *u,unsigned kind){
 uint8_t *s=ffta_job_state(u);unsigned item=ffta_primary_weapon(u);
 if(!s||!alive(u)||!kind||kind>11||!ffta_myk_weapon(item))return;
 put(s+FFTA_JOB_MYK_BLADE,(half(s+FFTA_JOB_MYK_BLADE)&0x6000u)|(item<<4)|kind);
}
void ffta_myk_event(uint8_t *u,unsigned event){
 uint8_t *s=ffta_job_state(u);if(!s)return;
 if(event>=2 && event<=5){put(s+FFTA_JOB_MYK_BLADE,0);return;}
 if(event==7 || (event==8 && !ffta_myk_enchantment(u)))ffta_myk_clear(u);
 if(event==8 && support(u)!=FFTA_MYK_S1)put(s+FFTA_JOB_MYK_BLADE,half(s+FFTA_JOB_MYK_BLADE)&0x1fffu);
}
unsigned ffta_additional_extension_snapshot_flags(const uint8_t *u){
 if(!alive(u))return 0;
 unsigned kind=ffta_myk_enchantment(u),f=kind;
 unsigned s=support(u),r=reaction(u);
 if(s==FFTA_MYK_S1)f|=FFTA_MYK_WEAVE|(ffta_myk_sequence(u)<<FFTA_MYK_SEQUENCE_SHIFT);
 if(s==FFTA_MYK_S2 && half(u+0x1c) && 2u*half(u+0x1c)>=half(u+0x1e))f|=FFTA_MYK_WARD;
 if((r==FFTA_MYK_R1 || (r==FFTA_MYK_R2 && kind)) && ffta_viking_reaction_ready(u)){
  if(r==FFTA_MYK_R1)f|=FFTA_MYK_SHELL_READY;
  if(r==FFTA_MYK_R2 && kind)f|=FFTA_MYK_PARRY_READY;
 }
 return f;
}
/* Unsnapshotted native AI forecasts are frequent. A support-only query must
 * not resolve enchantment ownership or reaction readiness on every candidate.
 * Inside a live action, the accessor above still returns the frozen flags. */
unsigned ffta_additional_extension_support_flags(const uint8_t *u){
 if(!alive(u))return 0;
 unsigned s=support(u);
 if(s==FFTA_MYK_S2)return half(u+0x1c) && 2u*half(u+0x1c)>=half(u+0x1e)?FFTA_MYK_WARD:0;
 if(s!=FFTA_MYK_S1)return 0;
 const uint8_t *state=ffta_job_state((uint8_t *)u);
 unsigned previous=state?(half(state+FFTA_JOB_MYK_BLADE)>>13)&3u:0;
 return FFTA_MYK_WEAVE|((previous<=2?previous:0)<<FFTA_MYK_SEQUENCE_SHIFT);
}
unsigned ffta_additional_extension_reaction_flags(const uint8_t *u){
 if(!alive(u))return 0;
 unsigned r=reaction(u);
 if(r!=FFTA_MYK_R1 && r!=FFTA_MYK_R2)return 0;
 if(!ffta_viking_reaction_ready(u))return 0;
 if(r==FFTA_MYK_R1)return FFTA_MYK_SHELL_READY;
 return ffta_myk_enchantment(u)?FFTA_MYK_PARRY_READY:0;
}
unsigned ffta_myk_sequence_category(const uint8_t *u,unsigned id){
 if(ffta_myk_action(id))return id==FFTA_MYK_A12?FFTA_ACTION_PHYSICAL:FFTA_ACTION_MAGICAL;
 if(id==265)return 0;
 unsigned kind=ffta_integrated_action_category(u,id);
 if(kind==FFTA_ACTION_PHYSICAL || kind==FFTA_ACTION_MAGICAL)return kind;
 if(kind)return 0;
 /* Original spell families include nondamaging entries whose native field28
  * is zero. Explicit tags avoid treating First Aid, Nurse or MP-cost martial
  * techniques as magic.33 is the Doublecast selector, not a subcast;37 and
  *66 are empty,67 is Item. Actual racial command access stays native. */
 return ((id>=1 && id<=21) || (id>=23 && id<=32) ||
         (id>=34 && id<=36) || (id>=38 && id<=65) ||
         (id>=68 && id<=75))?FFTA_ACTION_MAGICAL:0;
}
unsigned ffta_myk_weave_factor(const uint8_t *u,unsigned id){
 unsigned f=ffta_action_unit_extension_support_flags(u),previous=(f>>FFTA_MYK_SEQUENCE_SHIFT)&3u;
 if(!(f&FFTA_MYK_WEAVE) || !previous || previous>2)return 20;
 if(ffta_action_origin()==FFTA_ACTION_NATIVE_REACTION || ffta_action_origin()==FFTA_ACTION_EXPLICIT_COMBO ||
    (ffta_action_unit_extra_flags(u)&FFTA_BARD_FORCED))return 20;
 unsigned next=ffta_myk_sequence_category(u,id);
 return next && next!=previous?27:20;
}
unsigned ffta_myk_ward_factor(const uint8_t *u){return (ffta_action_unit_extension_support_flags(u)&FFTA_MYK_WARD)?3:4;}
unsigned ffta_myk_element_kind(unsigned kind){
 static const uint8_t elements[12]={0,1,5,6,0,0,0,0,0,0,0,7};
 return kind<12?elements[kind]:0;
}
unsigned ffta_myk_release_kind(unsigned kind){return kind==1||kind==2||kind==3||kind==8||kind==11;}
void ffta_myk_action_event(const uint8_t *u,unsigned id,unsigned event){
 if(ffta_myk_doublecast_event(u,id,event))return;
 if(!u || ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY || (id&&!ffta_action_paid_count()))return;
 unsigned f=ffta_action_unit_extension_flags(u);
 if(event==1 && id==FFTA_MYK_A13 && ffta_myk_release_kind(f&15u))ffta_myk_clear((uint8_t *)u);
 if(event==2){
  if(id>=FFTA_MYK_A1 && id<=FFTA_MYK_A11 && ffta_action_claim_extension((uint8_t *)u,FFTA_MYK_ENCHANTED))
   ffta_myk_grant((uint8_t *)u,id-FFTA_MYK_A1+1u);
  if((f&FFTA_MYK_WEAVE) && !(ffta_action_unit_extra_flags(u)&FFTA_BARD_FORCED)){
   unsigned category=ffta_myk_sequence_category(u,id);
   if(category)ffta_action_claim_extension((uint8_t *)u,category==1?FFTA_MYK_SEEN_PHYSICAL:FFTA_MYK_SEEN_MAGIC);
  }
 }
 if(event==3 && (f&FFTA_MYK_WEAVE) && !(ffta_action_unit_extra_flags(u)&FFTA_BARD_FORCED)){
  unsigned seen=(f>>16)&3u;if(!seen)return;
  uint8_t *s=ffta_job_state((uint8_t *)u);
  if(s)put(s+FFTA_JOB_MYK_BLADE,(half(s+FFTA_JOB_MYK_BLADE)&0x1fffu)|((seen==3?0:seen)<<13));
 }
}
