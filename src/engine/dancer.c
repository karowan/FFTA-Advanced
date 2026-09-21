#include "native-unit.h"
#include "dancer.h"
#include "registry.h"
#include "job-state.h"
#include "action-snapshot.h"
#include "reaction-queue.h"
#include "bard.h"
#include "curable-status.h"
#include "geomancer.h"
#include "mystic-knight.h"
#include "custom-laws.h"
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static void put_half(uint8_t *p,unsigned n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static unsigned alive(const uint8_t *u){return u && half(u+0x18) && !(u[0xe8]&64u);}
static unsigned support(const uint8_t *u){return u?((unsigned (*)(const uint8_t *))0x080cd50du)(u):0;}
static unsigned reaction(const uint8_t *u){return u?((unsigned (*)(const uint8_t *))0x080cd4d5u)(u):0;}
static unsigned hostile(const uint8_t *a,const uint8_t *t){return a && t && a!=t && (((a[0x29]>>7)^((a[0xeb]>>5)&1u))!=(t[0x29]>>7));}
static unsigned own_turn(const uint8_t *u){const uint8_t *m=*(const uint8_t *const *)0x0200f438u;return m && *(const uint8_t *const *)(m+24)==u;}
extern unsigned ffta_primary_weapon(const uint8_t *);
extern unsigned ffta_viking_reaction_ready(const uint8_t *);
extern unsigned ffta_integrated_direct_kind(const uint8_t *);
extern unsigned ffta_integrated_action_category(const uint8_t *,unsigned);
extern unsigned ffta_chemist_prevent_custom(const uint8_t *,unsigned);
unsigned ffta_dancer_virtual(unsigned id){return id==FFTA_DNC_A1 || id==FFTA_DNC_A4 || id==FFTA_DNC_A5 || id==FFTA_DNC_A7 || id==FFTA_DNC_A9;}
unsigned ffta_dancer_physical(unsigned id){return ffta_dancer_virtual(id)||id==FFTA_DNC_A8;}
static unsigned gear_power(const uint8_t *u){
 /* Native12F5E0 excludes every weapon returned by12F0D8 before summing
  * nonweapon gear. Replace its primary term, retaining its Frog exclusion. */
 if(((unsigned (*)(const uint8_t *))0x080cd95du)(u))return 0;
 unsigned level=u[9],v=12u+3u*level/5u;if(v>35)v=35;
 for(unsigned i=0;i<5;i++){
  unsigned item=half(u+0x2a+2*i);if(!item || item>460)continue;
  unsigned hands=((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(item,6);
  unsigned type=((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(item,3);
  if((hands==1||hands==2)&&type!=20)continue;
  v+=((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(item,10);
 }
 return v;
}
int ffta_dancer_attack(const uint8_t *u,unsigned action,unsigned item,int base){
 if(action==FFTA_GEO_A3 || action==FFTA_GEO_A8)item=0; /* Cast choice is not equipment. */
 if(!ffta_dancer_virtual(action))return ((int (*)(const uint8_t *,unsigned,unsigned,int))0x0812f691u)(u,action,item,base);
 return (int16_t)(base+(int)gear_power(u));
}
unsigned ffta_dancer_power(const uint8_t *u,unsigned item,unsigned stat,unsigned action){
 return ffta_dancer_virtual(action)&&stat==10?gear_power(u):((unsigned (*)(const uint8_t *,unsigned,unsigned))0x0812f5e1u)(u,item,stat);
}
/* Last Resort's command record remains weapon-free for its self mode. Its
 * hostile physical formula still uses the same primary power term as Fight,
 * rather than the record's zero magical coefficient. Keep the action ID. */
unsigned ffta_dancer_coefficient(unsigned action,const uint8_t *u,unsigned item){
 if(action==FFTA_DRK_A5)return ((unsigned (*)(const uint8_t *,unsigned,unsigned))0x0812f5e1u)(u,item,10);
 return ((unsigned (*)(unsigned,unsigned))0x080ccd51u)(action,33);
}
unsigned ffta_dancer_eligibility(const uint8_t *c){
 if(!c)return 0;
 const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+4);
 unsigned id=half(c+12);
 if(!alive(a)||!alive(t)||!hostile(a,t)||(a[0xeb]&16u))return 0;
 if(id==FFTA_DNC_A8){unsigned item=ffta_primary_weapon(a),type=((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(item,3);return item&&(type==7||type==8);}
 return id>=FFTA_DNC_A1 && id<=FFTA_DNC_A9;
}
int ffta_dancer_magnitude(const uint8_t *c){
 if(!ffta_dancer_eligibility(c))return 0;
 const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+4);unsigned id=half(c+12);
 return ((int (*)(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned,unsigned,unsigned))0x0812fe39u)
  (a,t,id,ffta_dancer_virtual(id)?0:ffta_primary_weapon(a),0,(c[0x26]&16u)?2:0,0);
}
int ffta_dancer_witch_hunt(const uint8_t *c){
 if(!ffta_dancer_eligibility(c))return 0;
 const uint8_t *t=*(const uint8_t *const *)(c+4);unsigned amount=half(t+0x1e)/5;
 if(amount<8)amount=8;
 if(amount>24)amount=24;
 return (int)(amount<half(t+0x1c)?amount:half(t+0x1c));
}
unsigned ffta_dancer_debuff(const uint8_t *u,unsigned magic){
 const uint8_t *s=ffta_job_state((uint8_t *)u);unsigned n=s?(s[FFTA_JOB_DNC_FLAGS]>>(magic?3:0))&7u:0;
 return alive(u)&&(n&3u)&&(n&3u)<=2;
}
/* Native resource/status AI rows include a fixed benefit even for an empty
 * resource pool or an existing ailment. Suppress only these no-op dances;
 * retain normal native values, prevention, probability and damage forecasts.
 * No second forecast or live-unit mutation belongs inside area placement. */
unsigned ffta_dancer_ai_redundant(const uint8_t *t,unsigned action){
 return t && ((action==FFTA_DNC_A2 && !half(t+0x1c)) ||
              (action==FFTA_DNC_A3 && (t[0xea]&64u)));
}
unsigned ffta_dancer_flags(const uint8_t *u){
 if(!alive(u))return 0;
 unsigned f=(ffta_dancer_debuff(u,0)?FFTA_DNC_POLKA:0)|(ffta_dancer_debuff(u,1)?FFTA_DNC_FROLIC:0),r=reaction(u);
 const uint8_t *s=ffta_job_state((uint8_t *)u);
 if(r==FFTA_DNC_R1 && s && (s[FFTA_JOB_DNC_FLAGS]&64u))f|=FFTA_DNC_CHARGED;
 if(ffta_viking_reaction_ready(u))f|=r==FFTA_DNC_R1?FFTA_DNC_FURY_READY:r==FFTA_DNC_R2?FFTA_DNC_RHYTHM_READY:0;
 return f;
}
uint64_t ffta_dancer_scaled(uint64_t product,uint64_t denominator,const uint8_t *a,const uint8_t *t,unsigned action,unsigned physical){
 if(!a||!t)return product/denominator;
 unsigned n=1,d=1,flags=ffta_action_unit_extra_flags(a),tf=ffta_action_unit_flags(t);
 unsigned direct=action!=265;
 if((tf&24u)==24u)direct=0;
 if(!(tf&8u)&&a!=t&&((unsigned (*)(const uint8_t *))0x0812e6a5u)(t)==13&&
    ((unsigned (*)(const uint8_t *,unsigned))0x080c7ea5u)(t,0x15)&&(!action||!((unsigned (*)(unsigned,unsigned))0x080ccd51u)(action,17)))direct=0;
 unsigned eligible=direct&&ffta_action_origin()!=FFTA_ACTION_NATIVE_REACTION&&ffta_action_origin()!=FFTA_ACTION_EXPLICIT_COMBO;
 if(direct && physical){n*=ffta_myk_parry_factor(a,t,action);d*=2;}
 if(direct && !physical){
  n*=ffta_myk_ward_factor(t);d*=4;
  unsigned incoming=ffta_action_unit_extra_flags(t);
  if(incoming&(FFTA_GEO_WISP|FFTA_GEO_WISP_STRONG)){n*=incoming&FFTA_GEO_WISP_STRONG?25:23;d*=20;}
  if(action==FFTA_GEO_A1 && (ffta_geo_affinity(a)&FFTA_GEO_ROCK)){n*=6;d*=5;}
 }
 /* Refuge is incoming protection, so the outgoing-bonus reaction exclusion
  * below does not remove it from an enemy's direct magical retaliation. */
 if(direct && !physical && (ffta_action_unit_extra_flags(t)&FFTA_GEO_REFUGE) &&
    a!=t && !(tf&4u) && ((((ffta_action_unit_flags(a)>>7)^(ffta_action_unit_flags(a)>>8))&1u)!=((tf>>7)&1u))){n*=4;d*=5;}
 if(eligible){
  n*=ffta_myk_weave_factor(a,action);d*=20;
  n*=ffta_geo_factor(a,t,action,physical);d*=16;
  if(flags&(physical?FFTA_DNC_POLKA:FFTA_DNC_FROLIC)){n*=13;d*=20;}
  if(physical && (flags&FFTA_DNC_CHARGED) && !(flags&FFTA_BARD_FORCED)){n*=27;d*=20;}
 }
 /* Keep every factor in the same final rounding step, including Ward and
  * Spellweave. Neither denominator*d nor the full numerator must wrap. */
 return ffta_damage_ratio(product,denominator,n,d);
}
static unsigned tick(unsigned t){return (t&3u)>2?0:(t&4u)?t&3u:t?t-1:0;}
void ffta_dancer_event(uint8_t *u,unsigned event){
 uint8_t *s=ffta_job_state(u);if(!s)return;
 if(event>=2&&event<=5)s[FFTA_JOB_DNC_FLAGS]=0;
 else if(event==6)s[FFTA_JOB_DNC_FLAGS]&=192u;
 else if(event==7 || (event==8 && reaction(u)!=FFTA_DNC_R1))s[FFTA_JOB_DNC_FLAGS]&=63u;
}
void ffta_dancer_turn_end(uint8_t *u){
 uint8_t *s=ffta_job_state(u);if(!s)return;unsigned v=s[FFTA_JOB_DNC_FLAGS];
 s[FFTA_JOB_DNC_FLAGS]=(uint8_t)(tick(v&7u)|(tick((v>>3)&7u)<<3)|((v&128u)?64u:0));
}
void ffta_dancer_action_event(const uint8_t *u,unsigned id,unsigned event){
 /* Fight has no MP-payment callback, but its authenticated completion is
  * still one executed physical attempt. Paid command failures stay excluded. */
 if(!u||event!=3||ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY||(id&&!ffta_action_paid_count())||(ffta_action_unit_extra_flags(u)&FFTA_BARD_FORCED))return;
 /* Damage classification is independent of future Spellweave sequencing. */
 if(!id||ffta_dancer_physical(id)||ffta_integrated_action_category(u,id)==FFTA_ACTION_PHYSICAL){uint8_t *s=ffta_job_state((uint8_t *)u);if(s)s[FFTA_JOB_DNC_FLAGS]&=63u;}
}
void ffta_dancer_hp_loss(uint8_t *u,unsigned before,unsigned after){
 const uint8_t *a=ffta_action_actor();unsigned id=ffta_action_id();
 if(before<=after||!alive(u)||ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY||!hostile(a,u))return;
 const uint8_t *c=(const uint8_t *)0x0200f3f0u;
 /* The actual positive HP ledger admits the rider after damage. Custom
  * immunity and Chemist prevention cannot erase the preceding HP damage. */
 if(id==FFTA_DNC_A4||id==FFTA_DNC_A5){
  uint8_t *s=ffta_job_state(u);
  if(s && support(u)!=11 && !ffta_chemist_prevent_custom(c,id==FFTA_DNC_A4?FFTA_CURABLE_POLKA:FFTA_CURABLE_HEATHEN_FROLIC)){
   unsigned shift=id==FFTA_DNC_A5?3:0,v=2u|(own_turn(u)?4u:0u);
   s[FFTA_JOB_DNC_FLAGS]=(uint8_t)((s[FFTA_JOB_DNC_FLAGS]&~(7u<<shift))|(v<<shift));
   ffta_custom_law_applied(u);
  }
 }
 if(!ffta_action_reactions_enabled())return;
 unsigned f=ffta_action_unit_extra_flags(u),kind=!id?1:half(c+12)==id?ffta_integrated_direct_kind(c):0;
 if((f&FFTA_DNC_FURY_READY)||(kind==1&&(f&FFTA_DNC_RHYTHM_READY)))ffta_action_claim_extra(u,FFTA_DNC_ADMITTED);
}
void ffta_dancer_queue(unsigned *frame){
 const uint8_t *a=ffta_action_actor();if(ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY)return;
 for(unsigned i=0;i<64;i++){
  uint8_t *u=(uint8_t *)ffta_action_unit_at(i);if(!u)break;
  unsigned f=ffta_action_unit_extra_flags(u),r=reaction(u);
  if(!(f&FFTA_DNC_ADMITTED)||(f&FFTA_DNC_QUEUED)||!ffta_viking_reaction_ready(u)||!hostile(a,u))continue;
  unsigned id=r==FFTA_DNC_R1?FFTA_DNC_FURY_ACTION:r==FFTA_DNC_R2?FFTA_DNC_RHYTHM_ACTION:0;
  int dx=(int)u[0xf6]-a[0xf6],dy=(int)u[0xf7]-a[0xf7];
  if(id==FFTA_DNC_RHYTHM_ACTION && (!alive(a)||(unsigned)(dx<0?-dx:dx)+(unsigned)(dy<0?-dy:dy)>3))continue;
  if(id&&ffta_reaction_queue_append(frame,u,id==FFTA_DNC_FURY_ACTION?u:(uint8_t *)a,id,id==FFTA_DNC_FURY_ACTION?FFTA_DNC_FURY_KIND:FFTA_DNC_RHYTHM_KIND,0))ffta_action_claim_extra(u,FFTA_DNC_QUEUED);
 }
}
unsigned ffta_dancer_reaction_eligibility(const uint8_t *c){
 if(!c||(c[0x26]&16u))return 0;
 const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+4);unsigned id=half(c+12);
 if(!alive(a)||!alive(t)||!ffta_viking_reaction_ready(a))return 0;
 if(id==FFTA_DNC_FURY_ACTION)return a==t && reaction(a)==FFTA_DNC_R1 && ffta_action_reaction_kind()==FFTA_DNC_FURY_KIND;
 int dx=(int)a[0xf6]-t[0xf6],dy=(int)a[0xf7]-t[0xf7];
 return id==FFTA_DNC_RHYTHM_ACTION && hostile(a,t) && reaction(a)==FFTA_DNC_R2 && ffta_action_reaction_kind()==FFTA_DNC_RHYTHM_KIND && (unsigned)(dx<0?-dx:dx)+(unsigned)(dy<0?-dy:dy)<=3;
}
uint8_t *ffta_dancer_fury_apply(uint8_t *c){
 if(ffta_dancer_reaction_eligibility(c)){uint8_t *u=*(uint8_t **)c,*s=ffta_job_state(u);if(s)s[FFTA_JOB_DNC_FLAGS]=(uint8_t)((s[FFTA_JOB_DNC_FLAGS]&63u)|64u|(own_turn(u)?128u:0u));}
 return c;
}
void ffta_dancer_drain(uint8_t *t,unsigned before,uint8_t *object){
 if(!t||!object||half(object+16)!=FFTA_DNC_A7||before<=half(t+0x18))return;
 uint8_t *a=**(uint8_t ***)object;if(!hostile(a,t))return;
 unsigned n=(before-half(t+0x18))/2,cap=half(a+0x1a)/4;if(n>cap)n=cap;
 unsigned missing=half(a+0x1a)>half(a+0x18)?half(a+0x1a)-half(a+0x18):0;
 if(!ffta_native_undead(t)&&n>missing)n=missing;
 int delta=ffta_native_undead(t)?(int)n:-(int)n;
 put_half(object+6,(unsigned)((int16_t)half(object+6)+delta));
}

extern unsigned ffta_drk_law_weapons(const uint8_t *,uint16_t *,unsigned);
unsigned ffta_dancer_law_weapons(const uint8_t *u,uint16_t *weapons,unsigned action){
 if(ffta_myk_action(action)){
  if(action==FFTA_MYK_A13)return 0;
  unsigned item=ffta_primary_weapon(u);if(item)weapons[0]=(uint16_t)item;return item!=0;
 }
 if(action>=FFTA_GEO_A1 && action<=FFTA_GEO_A9)return 0;
 if(action>=FFTA_DNC_A1&&action<=FFTA_DNC_A9){
  if(action!=FFTA_DNC_A8)return 0;
  unsigned item=ffta_primary_weapon(u);if(item)weapons[0]=(uint16_t)item;return item!=0;
 }
 return ffta_drk_law_weapons(u,weapons,action);
}
extern unsigned ffta_viking_status_accuracy(const uint8_t *);
extern unsigned ffta_original_viking_status_accuracy(const uint8_t *);
extern unsigned ffta_viking_status_adjust(const uint8_t *,unsigned);
unsigned ffta_dancer_status_accuracy(const uint8_t *c){
 if(c && half(c+12)==FFTA_GEO_A2 && (ffta_geo_affinity(*(const uint8_t *const *)c)&FFTA_GEO_VEGETATION)){
  unsigned chance=ffta_original_viking_status_accuracy(c);
  const uint8_t *t=*(const uint8_t *const *)(c+4);
  if(!chance || ((unsigned (*)(const uint8_t *))0x080cd8fdu)(t))return chance;
  chance=chance<80?chance+15:95;
  return ffta_viking_status_adjust(c,chance);
 }
 unsigned chance=ffta_viking_status_accuracy(c);
 if((c && half(c+12)==FFTA_MYK_A5 && c[0x28]) || ffta_myk_fight_sleep(c)){
  /* Native Astra uses guaranteed admission to consume its interception,
   * rather than rolling the underlying ailment. Preserve that protocol. */
  const uint8_t *t=*(const uint8_t *const *)(c+4);
  return ((unsigned (*)(const uint8_t *))0x080cd8fdu)(t)?chance:chance/2u;
 }
 if(!c||half(c+12)!=FFTA_DNC_RHYTHM_ACTION)return chance;
 const uint8_t *t=*(const uint8_t *const *)(c+4);
 if(((unsigned (*)(const uint8_t *))0x080cd8fdu)(t))return chance;
 return chance<75?chance+20:95;
}
