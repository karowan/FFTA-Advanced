#include "geomancer.h"
#include "registry.h"
#include "action-snapshot.h"
#include "reaction-queue.h"
#include "bard.h"
#include "battle-state.h"
#include "evaluated-units.h"
extern unsigned ffta_primary_weapon(const uint8_t *);
extern unsigned ffta_viking_reaction_ready(const uint8_t *);
extern unsigned ffta_integrated_direct_kind(const uint8_t *);
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static void put_half(uint8_t *p,unsigned n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static unsigned alive(const uint8_t *u){return u && half(u+0x18) && !(u[0xe8]&64u);}
static unsigned support(const uint8_t *u){return u?((unsigned (*)(const uint8_t *))0x080cd50du)(u):0;}
static unsigned reaction(const uint8_t *u){return u?((unsigned (*)(const uint8_t *))0x080cd4d5u)(u):0;}
static unsigned enemy(const uint8_t *a,const uint8_t *t){
 unsigned af=ffta_action_unit_flags(a),tf=ffta_action_unit_flags(t);
 return a&&t&&a!=t&&!(tf&4u)&&((((af>>7)^(af>>8))&1u)!=((tf>>7)&1u));
}
static unsigned range(const uint8_t *a,const uint8_t *t){
 int dx=(int)a[0xf6]-t[0xf6],dy=(int)a[0xf7]-t[0xf7];
 return (unsigned)(dx<0?-dx:dx)+(unsigned)(dy<0?-dy:dy)<=4;
}
unsigned ffta_geo_flags(const uint8_t *u){
 if(!alive(u))return 0;
 unsigned f=support(u)==FFTA_GEO_S1?FFTA_GEO_ATTUNEMENT:0,r=reaction(u);
 if(ffta_viking_reaction_ready(u))f|=r==FFTA_GEO_R1?FFTA_GEO_STONE_READY:r==FFTA_GEO_R2?FFTA_GEO_WRATH_READY:0;
 unsigned wisp=ffta_geo_wisp(u);
 return f|(ffta_geo_refuge(u)?FFTA_GEO_REFUGE:0)|(wisp==2?FFTA_GEO_WISP_STRONG:wisp?FFTA_GEO_WISP:0);
}
unsigned ffta_geo_weakness(const uint8_t *a,const uint8_t *t,unsigned action){
 if(!a||!t)return 0;
 unsigned primary=ffta_primary_weapon(a);
 if(action==FFTA_GEO_A8){
  const uint8_t *c=(const uint8_t *)0x0200f3f0u;
  primary=half(c+12)==action && *(const uint8_t *const *)c==a?half(c+14):0;
 }
 unsigned element=((unsigned (*)(const uint8_t *,unsigned,unsigned))0x0812f8a5u)(a,action,primary);
 if(!element||element>8)return 0;
 uint8_t affinity[9];
 for(unsigned i=0;i<9;i++)affinity[i]=(uint8_t)((unsigned (*)(const uint8_t *,unsigned))0x080c7ea5u)(t,10+i);
 unsigned gear=((unsigned (*)(const uint8_t *,unsigned,unsigned))0x0812fa91u)(t,element,0);
 if(gear)affinity[element]=(uint8_t)((unsigned (*)(unsigned))0x0812fc75u)(gear);
 /* Native offensive equipment can change the effective affinity. Native
  * weakness laws apply only to the player side while the rule is enabled. */
 ((void (*)(const uint8_t *,uint8_t *))0x0812fafdu)(a,affinity);
 if(!((unsigned (*)(const uint8_t *))0x080c8241u)(a) &&
    !((unsigned (*)(unsigned))0x080c95a9u)(13) &&
    ((unsigned (*)(unsigned))0x080d2cc5u)(element))
  affinity[element]=(uint8_t)((unsigned (*)(unsigned))0x0812f8e9u)(affinity[element]);
 return affinity[element]==0;
}
unsigned ffta_geo_factor(const uint8_t *a,const uint8_t *t,unsigned action,unsigned physical){
 unsigned n=4,d=4,origin=ffta_action_origin(),f=ffta_action_unit_extra_flags(a);
 if(action!=265 && origin!=FFTA_ACTION_NATIVE_REACTION && origin!=FFTA_ACTION_EXPLICIT_COMBO &&
    (f&FFTA_GEO_ATTUNEMENT) && ffta_geo_weakness(a,t,action))n=5;
 if(physical && enemy(a,t) && (ffta_action_unit_extra_flags(t)&FFTA_GEO_STONE_READY) &&
    origin!=FFTA_ACTION_NATIVE_REACTION && origin!=FFTA_ACTION_EXPLICIT_COMBO &&
    (ffta_action_phase()!=FFTA_ACTION_RESULT || ffta_action_reactions_enabled()))d=3;
 return n*d; /* denominator16, one division with the other final factors */
}
void ffta_geo_hp_loss(uint8_t *u,unsigned before,unsigned after){
 ffta_geo_wisp_hp_loss(u,before,after);
 const uint8_t *a=ffta_action_actor();unsigned action=ffta_action_id();
 if(before<=after||ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY||!enemy(a,u))return;
 const uint8_t *c=(const uint8_t *)0x0200f3f0u;
 unsigned kind=!action?1:half(c+12)==action?ffta_integrated_direct_kind(c):0;
 if(kind && (ffta_action_unit_extra_flags(a)&FFTA_GEO_ATTUNEMENT) &&
    !(ffta_action_unit_extra_flags(a)&FFTA_BARD_FORCED) && ffta_action_mp_spent() && ffta_geo_weakness(a,u,action))
  ffta_action_claim_extra((uint8_t *)a,FFTA_GEO_REFUND);
 if(!alive(u)||!ffta_action_reactions_enabled())return;
 unsigned flags=ffta_action_unit_extra_flags(u);
 if((flags&FFTA_GEO_WRATH_READY)||(kind==1&&(flags&FFTA_GEO_STONE_READY)))
  ffta_action_claim_extra(u,FFTA_GEO_ADMITTED);
}
void ffta_geo_action_event(const uint8_t *u,unsigned action,unsigned event){
 ffta_geo_field_action(u,action,event);
 if(event!=3||!alive(u)||ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY||
    !(ffta_action_unit_extra_flags(u)&FFTA_GEO_REFUND) ||
    !ffta_action_claim_extra((uint8_t *)u,FFTA_GEO_REFUNDED))return;
 unsigned refund=ffta_action_mp_spent()/4,mp=half(u+0x1c),max=half(u+0x1e);
 if(mp>=max)return;
 if(refund>max-mp)refund=max-mp;
 put_half((uint8_t *)u+0x1c,mp+refund);
}
void ffta_geo_queue(unsigned *frame){
 const uint8_t *a=ffta_action_actor();if(ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY)return;
 for(unsigned i=0;i<64;i++){
  uint8_t *u=(uint8_t *)ffta_action_unit_at(i);if(!u)break;
  unsigned f=ffta_action_unit_extra_flags(u),r=reaction(u);
  if(!(f&FFTA_GEO_ADMITTED)||(f&FFTA_GEO_QUEUED)||!ffta_viking_reaction_ready(u)||!enemy(a,u))continue;
  unsigned id=r==FFTA_GEO_R1?FFTA_GEO_STONE_ACTION:r==FFTA_GEO_R2?FFTA_GEO_WRATH_ACTION:0;
  if(id==FFTA_GEO_WRATH_ACTION && (!alive(a)||!range(u,a)))continue;
  if(id&&ffta_reaction_queue_append(frame,u,id==FFTA_GEO_STONE_ACTION?u:(uint8_t *)a,id,
      id==FFTA_GEO_STONE_ACTION?FFTA_GEO_STONE_KIND:FFTA_GEO_WRATH_KIND,0))ffta_action_claim_extra(u,FFTA_GEO_QUEUED);
 }
}
unsigned ffta_geo_reaction_eligibility(const uint8_t *c){
 if(!c||(c[0x26]&16u))return 0;
 const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+4);
 unsigned action=half(c+12),kind=ffta_action_reaction_kind();
 if(!alive(a)||!alive(t)||!ffta_viking_reaction_ready(a))return 0;
 if(action==FFTA_GEO_STONE_ACTION)return a==t && reaction(a)==FFTA_GEO_R1 && kind==FFTA_GEO_STONE_KIND;
 return action==FFTA_GEO_WRATH_ACTION && a!=t &&
  (((a[0x29]>>7)^((a[0xeb]>>5)&1u))!=(t[0x29]>>7)) &&
  reaction(a)==FFTA_GEO_R2 && kind==FFTA_GEO_WRATH_KIND && range(a,t);
}
extern unsigned ffta_snapshotted_evaluated_init(void *,const uint8_t *);
extern void ffta_snapshotted_evaluated_close(void *);
int ffta_geo_magnitude(const uint8_t *c){
 if(half(c+12)!=FFTA_GEO_WRATH_ACTION)return ((int (*)(const uint8_t *))0x0813189du)(c);
 if(!ffta_geo_reaction_eligibility(c))return 0;
 /* Preserve equipment, job, Magic Power and native incoming resistance.
  * Disable outgoing support damage only on this explicitly owned temporary
  * actor. Accuracy still uses the original actor and its native A path. */
 FFTA_EvaluatedUnit copy;uint8_t local[0x34];
 if(!ffta_snapshotted_evaluated_init(&copy,*(const uint8_t *const *)c))return 0;
 for(unsigned i=0;i<sizeof(local);i++)local[i]=c[i];
 copy.unit[0x3b]=0;*(uint8_t **)local=copy.unit;
 int result=((int (*)(const uint8_t *))0x0813189du)(local);
 ffta_snapshotted_evaluated_close(&copy);return result;
}
extern void ffta_geo_original_mobility(uint8_t *);
void ffta_geo_mobility(uint8_t *u){
 ffta_geo_original_mobility(u);
 unsigned add=(support(u)==FFTA_GEO_S2)+ffta_geo_updraft(u,1);
 int jump=(int8_t)u[0xfe]+(int)add;if(jump>127)jump=127;
 u[0xfe]=(uint8_t)jump;u[0xff]=(uint8_t)~u[0xfe];
}
extern void ffta_geo_original_tile(uint8_t *,int,int,const uint8_t *);
void ffta_geo_tile(uint8_t *grid,int x,int y,const uint8_t *wrapper){
 ffta_geo_original_tile(grid,x,y,wrapper);
 if(x<0||x>=16||y<0||y>=16||!wrapper)return;
 const uint8_t *u=*(const uint8_t *const *)wrapper;
 uint8_t *tile=grid+7u*(16u*(unsigned)y+(unsigned)x);
 /* Low nibble is the entering-tile cost. All native blocked/occupancy bits,
  * height and the independent jump-over-gap cost remain untouched. */
 if(!(tile[0]&128u))return;
 unsigned cost=tile[1]&15u;
 if(ffta_geo_grounded(u) && ffta_geo_field_at(u,x,y,1) && cost<15)cost++;
 if(support(u)==FFTA_GEO_S2 && cost>1)cost=1;
 tile[1]=(uint8_t)((tile[1]&240u)|cost);
}
