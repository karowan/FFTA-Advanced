#include "chemist-progression.h"
#include "job-state.h"
#include "action-snapshot.h"
#include "native-unit.h"
#include "chemist-state.h"
#include "blade-wound.h"
#include "viking-state.h"
#include "geomancer.h"
#include "dancer.h"
#include "reaction-queue.h"
#include "unit-query.h"
#include "evaluated-units.h"
#include "curable-status.h"
#include "custom-laws.h"
#include "battle-workspace.h"

static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static unsigned alive(const uint8_t *u){return u && half(u+0x18) && !(u[0xe8]&64u);}
static unsigned hostile(const uint8_t *a,const uint8_t *t){return a && t && a!=t && (((a[0x29]>>7)^((a[0xeb]>>5)&1u))!=(t[0x29]>>7));}
static unsigned support(const uint8_t *u){return u?((unsigned (*)(const uint8_t *))0x080cd50du)(u):0;}
static unsigned reaction(const uint8_t *u){return u?((unsigned (*)(const uint8_t *))0x080cd4d5u)(u):0;}
static unsigned active(unsigned timer){return (timer&3u)==1 || (timer&3u)==2;}
static unsigned tick(unsigned t){return !active(t)?0:(t&4u)?t&3u:t-1;}
static unsigned own_turn(const uint8_t *u){
 const uint8_t *m=*(const uint8_t *const *)0x0200f438u;
 return m && *(const uint8_t *const *)(m+24)==u;
}
static unsigned mutable(const uint8_t *c,uint8_t *u){
 unsigned token=ffta_job_origin(u);if(!token || !ffta_job_state(u))return 0;
 uintptr_t live=token<=24?0x02000080u+(token-1)*264u:0x02002fc4u+(token-25)*264u;
 return !(c[0x26]&16u) || (uintptr_t)u!=live;
}
static unsigned distance(const uint8_t *a,const uint8_t *b){
 int x=(int)a[0xf6]-b[0xf6],y=(int)a[0xf7]-b[0xf7];
 return (unsigned)(x<0?-x:x)+(unsigned)(y<0?-y:y);
}
/* Stable compact mask of the seven native Cureall ailments plus five custom
 * remedies and Fuse. Freeze it before any hit so Triage cannot cure an old
 * ailment merely because the same action damaged this recipient. */
static const uint8_t ailments[7]={6,8,9,10,26,27,28};
unsigned ffta_cp_ailments(const uint8_t *u){
 if(!u)return 0;
 unsigned mask=0;
 for(unsigned i=0;i<7;i++)if(u[0xe8+ailments[i]/8]&(1u<<(ailments[i]%8)))mask|=1u<<i;
 if(ffta_wound_record_remaining(ffta_owned_wound((uint8_t *)u)))mask|=1u<<7;
 if(ffta_viking_challenger(u))mask|=1u<<8;
 if(ffta_geo_wisp(u))mask|=1u<<9;
 if(ffta_dancer_debuff(u,0))mask|=1u<<10;
 if(ffta_dancer_debuff(u,1))mask|=1u<<11;
 const uint8_t *s=ffta_job_state((uint8_t *)u);
 if(s && (s[FFTA_CP_TIMERS]&192u))mask|=1u<<12;
 return mask;
}
static unsigned cure_one(uint8_t *u,unsigned mask){
 mask&=ffta_cp_ailments(u);if(!mask)return 0;
 unsigned bit=0;while(!(mask&(1u<<bit)))bit++;
 if(bit<7){
  ((void (*)(uint8_t *,unsigned,unsigned))0x080cd885u)(u,ailments[bit],0);
  ((void (*)(uint8_t *))0x08131c59u)(u);
  ((void (*)(uint8_t *))0x080ca2e9u)(u);
 }
 else {
  uint8_t *s=ffta_job_state(u);if(!s)return 0;
  if(bit==7)ffta_wound_record_clear(ffta_owned_wound(u));
  if(bit==8)s[5]=0;
  if(bit==9){s[17]&=31u;s[18]&=254u;}
  if(bit==10)s[3]&=248u;
  if(bit==11)s[3]&=199u;
  if(bit==12){s[FFTA_CP_TIMERS]&=63u;s[FFTA_CP_FUSE_OWNER]=0;}
 }
 return bit+1;
}
extern unsigned ffta_viking_reaction_ready(const uint8_t *);
/* Damage/accuracy consumers do not read the ailment history. Resolve only
 * their combat bits during an unsnapshotted AI query. Action snapshots still
 * freeze the complete flags for Triage, cures and after-action reactions. */
unsigned ffta_cp_combat_flags(const uint8_t *u){
 if(!u)return 0;
 unsigned flags=0;
 if(!alive(u))return 0;
 const uint8_t *s=ffta_job_state((uint8_t *)u);
 if(s){
  if(active(s[FFTA_CP_MEDIC]&7u))flags|=FFTA_CP_TRIAGE;
  if(active((s[FFTA_CP_MEDIC]>>3)&7u))flags|=FFTA_CP_WARD;
  if(active(s[FFTA_CP_TIMERS]&7u))flags|=FFTA_CP_SMOKE;
 }
 unsigned sp=support(u),r=reaction(u);
 if(sp==FFTA_PHY_SUPPORT)flags|=FFTA_CP_FOLLOWUP;
 if(sp==FFTA_SAP_SUPPORT)flags|=FFTA_CP_SPOTTER;
 if(u[0xeb]&48u)flags|=FFTA_CP_FORCED;
 if((r==FFTA_PHY_REACTION || r==FFTA_SAP_REACTION) && ffta_viking_reaction_ready(u)){
  if(r==FFTA_PHY_REACTION && s && !(s[FFTA_CP_MEDIC]&64u))flags|=FFTA_CP_DRESSING;
  if(r==FFTA_SAP_REACTION)flags|=FFTA_CP_DUCK;
 }
 return flags;
}
unsigned ffta_cp_flags(const uint8_t *u){return ffta_cp_ailments(u)|ffta_cp_combat_flags(u);}
unsigned ffta_cp_spotter_adjacency(const uint8_t *actor,const uint8_t *target){
 if(!alive(actor)||!alive(target)||!hostile(actor,target))return 0;
 uint8_t *peers[36];unsigned count=ffta_job_peers((uint8_t *)actor,peers,36);
 for(unsigned i=0;i<count;i++)if(peers[i]!=actor && peers[i]!=target && alive(peers[i]) &&
    !hostile(actor,peers[i]) && distance(peers[i],target)==1)return FFTA_CP_ADJACENT;
 return 0;
}
unsigned ffta_cp_eligibility(const uint8_t *c){
 if(!c)return 0;
 const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+4);
 unsigned id=half(c+12);
 if(id==463 || id==464)return (c[0x26]&16u) && alive(a) && alive(t);
 if(id>=FFTA_CP_TRIAGE_ACTION && id<=FFTA_CP_DRESSING_ACTION){
  if((c[0x26]&16u)||a!=t||!alive(t)||ffta_native_undead(t))return 0;
  unsigned kind=ffta_action_reaction_kind();
  return kind==160u+(id-FFTA_CP_TRIAGE_ACTION) &&
   (id!=FFTA_CP_DRESSING_ACTION || (reaction(t)==FFTA_PHY_REACTION && ffta_viking_reaction_ready(t)));
 }
 if(!alive(a)||!t||(a[0xeb]&16u))return 0;
 if(id>=FFTA_PHY_FIRST && id<=FFTA_PHY_LAST){
  if(hostile(a,t)||ffta_native_undead(t))return 0;
  if(id==450)return ((unsigned (*)(const uint8_t *))0x08130a0du)(c);
  return alive(t);
 }
 if(!alive(t))return 0;
 if(id==457 || id==458)return !hostile(a,t) &&
  (id!=458 || (!ffta_query_same_unit(c,a,t) && !(t[0xe8]&0x41u) && !(t[0xeb]&0x70u) && !(t[0xec]&1u)));
 /* Self is only the AI's virtual utility recipient. Player center admission
  * separately requires an empty legal tile; actual placement has no victim. */
 if(id==456)return (c[0x26]&144u) && ffta_query_same_unit(c,a,t);
 if(id==453 && (half(c+14)<1 || half(c+14)>2))return 0;
 return id>=453 && id<=459 && hostile(a,t) && (!c[0x28] || ffta_cp_rider(c));
}
extern unsigned ffta_recuperation_numerator(const uint8_t *,const uint8_t *);
extern unsigned ffta_turn_healing_numerator(const uint8_t *);
int ffta_cp_healing(const uint8_t *c){
 if(!ffta_cp_eligibility(c))return 0;
 const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+4);
 unsigned id=half(c+12),maximum=half(t+0x1a),hp=half(t+0x18),missing=maximum>hp?maximum-hp:0;
 unsigned base=id==446?(maximum*4u+missing*5u)/20u:maximum/4u;
 if(id>=460 && id<=462)base=ffta_action_reaction_value()&1023u;
 else base=base*ffta_recuperation_numerator(a,t)*ffta_turn_healing_numerator(a)/40u;
 return (int)(base<missing?base:missing);
}
int ffta_cp_revive(const uint8_t *c){
 if(!ffta_cp_eligibility(c)||half(c+12)!=450)return 0;
 const uint8_t *t=*(const uint8_t *const *)(c+4);
 return (int)(half(t+0x1a)*35u/100u);
}
uint8_t *ffta_cp_apply(uint8_t *c){
 if(!ffta_cp_eligibility(c))return c;
 uint8_t *u=*(uint8_t **)(c+8);if(!mutable(c,u))return c;
 uint8_t *s=ffta_job_state(u);unsigned id=half(c+12),timer=2u|(own_turn(u)?4u:0u);
 if(id==447)s[FFTA_CP_MEDIC]=(uint8_t)((s[FFTA_CP_MEDIC]&248u)|timer);
 if(id==452)s[FFTA_CP_MEDIC]=(uint8_t)((s[FFTA_CP_MEDIC]&199u)|(timer<<3));
 if(id==457)s[FFTA_CP_TIMERS]=(uint8_t)((s[FFTA_CP_TIMERS]&248u)|timer);
 if(id==448){
  while(cure_one(u,FFTA_CP_AILMENTS)){}
  ffta_inoculated_grant(u,own_turn(u));
 }
 if(id>=460 && id<=462){
  unsigned cure=ffta_action_reaction_value()>>10;
  if(cure && cure<=13)cure_one(u,1u<<(cure-1));
  if(id==462)s[FFTA_CP_MEDIC]|=64u;
 }
 if(id==455 && c[0x28] && ffta_cp_rider(c)){
  const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+4);
  int dx=(int)t[0xf6]-a[0xf6],dy=(int)t[0xf7]-a[0xf7];
  unsigned ax=(unsigned)(dx<0?-dx:dx),ay=(unsigned)(dy<0?-dy:dy),direction;
  direction=ax>=ay?(dx>=0?2:4):(dy>=0?3:1);
  uint8_t x=0,y=0;
  if(ffta_geo_push_destination(t,direction,&x,&y)){
   c[0x26]|=8u;u[0xf6]=x;u[0xf7]=y;
   ffta_cp_position_changed(u,x,y);
  }
 }
 if(id==459 && c[0x28] && ffta_cp_rider(c) && support(u)!=11 &&
    !ffta_chemist_prevent_custom(c,FFTA_CURABLE_TIMED_FUSE)){
  const uint8_t *a=*(const uint8_t *const *)c;unsigned token=ffta_job_origin(a);
  if(token && u[0xf6]<16 && u[0xf7]<16){
   s[FFTA_CP_TIMERS]=(uint8_t)((s[FFTA_CP_TIMERS]&63u)|(own_turn(u)?128u:64u));
   s[FFTA_CP_FUSE_OWNER]=(uint8_t)token;s[FFTA_CP_FUSE_TILE]=(uint8_t)(u[0xf6]|(u[0xf7]<<4));
   ffta_custom_law_applied(u);
  }
 }
 return c;
}
extern unsigned ffta_snapshotted_evaluated_init(void *,const uint8_t *);
extern void ffta_snapshotted_evaluated_close(void *);
int ffta_cp_magnitude(const uint8_t *c){
 unsigned id=half(c+12);
 if(id!=453)return ((int (*)(const uint8_t *))0x0813189du)(c);
 if(!ffta_cp_eligibility(c))return 0;
 /* Only the selected defense changes on an owned forecast copy. Fire
  * resistance, equipment and all other native formula inputs survive. */
 FFTA_EvaluatedUnit target;uint8_t local[0x34];
 if(!ffta_snapshotted_evaluated_init(&target,*(const uint8_t *const *)(c+4)))return 0;
 for(unsigned i=0;i<sizeof(local);i++)local[i]=c[i];
 unsigned bit=half(c+14)==1?25:24;target.unit[0xe8+bit/8]&=(uint8_t)~(1u<<(bit%8));
 *(uint8_t **)(local+4)=*(uint8_t **)(local+8)=target.unit;
 int result=((int (*)(const uint8_t *))0x0813189du)(local);
 ffta_snapshotted_evaluated_close(&target);return result;
}
unsigned ffta_cp_rider(const uint8_t *c){
 const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+8);
 if(!alive(a)||!alive(t))return 0;
 if(!(c[0x26]&16u) && ffta_action_phase()==FFTA_ACTION_RESULT && ffta_action_id()==half(c+12))
  return ffta_action_hp_lost(t)>0;
 uint8_t copy[0x34],saved[0x34];volatile uint8_t *scratch=(volatile uint8_t *)0x0200f3f0u;
 for(unsigned i=0;i<sizeof(copy);i++){copy[i]=c[i];saved[i]=scratch[i];}
 const uint8_t *descriptors=*(const uint8_t *const *)0x0812f2a0u;
 *(const uint8_t **)(copy+0x30)=descriptors+63u*4u;copy[0x28]=0;copy[0x26]|=16u;
 volatile uint32_t *rng=(volatile uint32_t *)0x030034b0u;unsigned previous=*rng;
 int damage=ffta_cp_magnitude(copy);
 const uint8_t *original=*(const uint8_t *const *)(c+4);
 if(damage>0 && ((unsigned (*)(const uint8_t *))0x0812e6a5u)(original)==13 &&
    ((unsigned (*)(const uint8_t *,const uint8_t *,unsigned,unsigned))0x0812e6e1u)(a,original,half(c+12),13))damage=0;
 *rng=previous;for(unsigned i=0;i<sizeof(copy);i++)scratch[i]=saved[i];return damage>0;
}
static unsigned spotter(const uint8_t *a,const uint8_t *t,unsigned id){
 unsigned f=ffta_action_cp_combat_flags(a),origin=ffta_action_origin();
 if((f&(FFTA_CP_SPOTTER|FFTA_CP_FORCED))!=FFTA_CP_SPOTTER)return 0;
 if(!a||!t||!hostile(a,t)||distance(a,t)<=1||id>=460 || id==265 ||
    origin==FFTA_ACTION_NATIVE_REACTION || origin==FFTA_ACTION_EXPLICIT_COMBO ||
    (ffta_action_category()&FFTA_ACTION_ITEM))return 0;
 unsigned area=id && ((unsigned (*)(unsigned,unsigned))0x080ccd51u)(id,7)>1;
 return !area && (f&(FFTA_CP_SPOTTER|FFTA_CP_FORCED))==FFTA_CP_SPOTTER &&
  (ffta_action_cp_flags(t)&FFTA_CP_ADJACENT);
}
unsigned ffta_cp_accuracy(const uint8_t *c,unsigned native){
 if(!c || !native)return native;
 const uint8_t *descriptor=*(const uint8_t *const *)(c+0x30);
 /* Descriptor accuracy slot10 is ordinary attack accuracy. Status slots
  * keep their native roll and a zero chance never becomes an automatic hit. */
 if(!descriptor || descriptor[2]!=10 || !spotter(*(const uint8_t *const *)c,*(const uint8_t *const *)(c+4),half(c+12)))return native;
 return native>=90?100:native+10;
}
unsigned ffta_cp_empty_tile(const uint8_t *u,unsigned x,unsigned y){
 if(!alive(u)||x>=16||y>=16||!((unsigned (*)(unsigned,unsigned))0x0801cc7du)(x,y))return 0;
 /* Ordinary Move commits displayed wrappers before unit F6/F7. Read that
  * actual occupancy so the just-vacated tile is legal and the actor's new
  * tile cannot receive a trap under its feet. */
 uint8_t *wrappers[36];void *manager=ffta_owned_battle_manager();if(!manager)return 0;
 unsigned n=((unsigned (*)(void *,uint8_t **))0x08099cddu)(manager,wrappers);
 if(!n || n>36)return 0;
 for(unsigned i=0;i<n;i++){
  const uint8_t *w=wrappers[i],*peer=*(const uint8_t *const *)w;
  if(half(peer+0x18) && (half(w+8)>>5)==x && (half(w+12)>>5)==y)return 0;
 }
 return 1;
}
void ffta_cp_action_event(const uint8_t *u,unsigned action,unsigned event){
 if(action!=456 || event!=2 || ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY || !ffta_action_paid_count())return;
 const uint8_t *o=ffta_action_result_object();uint8_t *s=ffta_job_state((uint8_t *)u);
 if(!o || !s || half(o+16)!=456 || !ffta_cp_empty_tile(u,o[10],o[11]))return;
 s[FFTA_CP_TRAP_TILE]=(uint8_t)(o[10]|(o[11]<<4));
 s[FFTA_CP_TIMERS]=(uint8_t)((s[FFTA_CP_TIMERS]&199u)|((2u|(own_turn(u)?4u:0u))<<3));
}
unsigned ffta_cp_trap_at(const uint8_t *u,unsigned x,unsigned y){
 if(!u||x>=16||y>=16)return 0;
 uint8_t *peers[36];unsigned n=ffta_job_peers((uint8_t *)u,peers,36);
 for(unsigned i=0;i<n;i++){
  const uint8_t *s=ffta_job_state(peers[i]);
  if(s && alive(peers[i]) && hostile(peers[i],u) && active((s[23]>>3)&7u) && s[25]==(x|(y<<4)))return ffta_job_origin(peers[i]);
 }
 return 0;
}
void ffta_cp_position_changed(uint8_t *u,unsigned x,unsigned y){
 uint8_t *s=ffta_job_state(u);
 if(s && (s[23]&192u) && (x>=16 || y>=16 || s[26]!=(x|(y<<4)))){s[23]&=63u;s[24]=0;}
}
void ffta_cp_event(uint8_t *u,unsigned event){
 uint8_t *s=ffta_job_state(u);if(!s)return;
 if(event>=2 && event<=5)for(unsigned i=22;i<27;i++)s[i]=0;
 else if(event==1)s[FFTA_CP_MEDIC]&=191u;
 else if(event==6){s[FFTA_CP_TIMERS]&=63u;s[FFTA_CP_FUSE_OWNER]=0;}
 else if(event==7){s[FFTA_CP_MEDIC]&=64u;s[FFTA_CP_TIMERS]&=248u;}
}
void ffta_cp_turn_end(uint8_t *u){
 uint8_t *s=ffta_job_state(u);if(!s)return;
 s[FFTA_CP_MEDIC]=(uint8_t)((s[FFTA_CP_MEDIC]&64u)|tick(s[FFTA_CP_MEDIC]&7u)|(tick((s[FFTA_CP_MEDIC]>>3)&7u)<<3));
 s[FFTA_CP_TIMERS]=(uint8_t)((s[FFTA_CP_TIMERS]&192u)|tick(s[FFTA_CP_TIMERS]&7u)|(tick((s[FFTA_CP_TIMERS]>>3)&7u)<<3));
}
/* Denominator 500. These are HP-only factors and are combined with the
 * existing rational finalizer before its single rounding operation. */
unsigned ffta_cp_damage_factor(const uint8_t *a,const uint8_t *t,unsigned id){
 unsigned tf=ffta_action_cp_combat_flags(t);
 unsigned base=ffta_action_unit_flags_masked(t,24u);
 if(!a||!t||!hostile(a,t)||(base&24u)==24u || id>=460 ||
    ffta_action_origin()==FFTA_ACTION_NATIVE_REACTION || ffta_action_origin()==FFTA_ACTION_EXPLICIT_COMBO)return 500;
 unsigned area=id && ((unsigned (*)(unsigned,unsigned))0x080ccd51u)(id,7)>1;
 unsigned ranged=distance(a,t)>1;
 unsigned bonus=spotter(a,t,id);
 unsigned duck=area && (tf&FFTA_CP_DUCK) && ffta_action_reaction_forecast_enabled();
 return (bonus?6u:5u)*((tf&FFTA_CP_WARD)?3u:5u)*
  (ranged && (tf&FFTA_CP_SMOKE)?3u:4u)*(duck?3u:5u);
}
void ffta_cp_hp_loss(uint8_t *u,unsigned before,unsigned after){
 if(before<=after||ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY||!hostile(ffta_action_actor(),u))return;
 ffta_action_cp_claim(u,FFTA_CP_DAMAGED);
 if(ffta_action_id()==453){
  const uint8_t *c=(const uint8_t *)0x0200f3f0u;unsigned choice=half(c+14);
  if(half(c+12)==453 && choice>=1 && choice<=2){
   unsigned bit=choice==1?25:24;
   ((void (*)(uint8_t *,unsigned,unsigned))0x080cd885u)(u,bit,0);
   ((void (*)(uint8_t *))0x08131c59u)(u);
   ((void (*)(uint8_t *))0x080ca2e9u)(u);
  }
 }
 if(alive(u) && ffta_action_reactions_enabled() && (ffta_action_cp_flags(u)&FFTA_CP_DRESSING))
  ffta_action_cp_claim(u,FFTA_CP_DRESSING_ADMITTED);
}
void ffta_cp_candidate(const uint8_t *a,const uint8_t *t,unsigned id,unsigned positive){
 if(ffta_action_phase()!=FFTA_ACTION_RESULT || ffta_action_id()!=id)return;
 const uint8_t *c=(const uint8_t *)0x0200f3f0u;
 if(id && (half(c+12)!=id || (c[0x26]&16u)))return;
 if(id==453 && *(const uint8_t *const *)c==a)t=*(const uint8_t *const *)(c+4);
 ffta_action_cp_candidate(t,positive && hostile(a,t));
}
/* Only the authenticated direct-HP writer calls this, after native hit and
 * immunity admission. A one-point hit rounded to zero still spends Ward;
 * MP shield, misses, healing and prediction never use this boundary. */
void ffta_cp_direct_hit(uint8_t *u,unsigned damage){
 if(ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY || !hostile(ffta_action_actor(),u))return;
 unsigned f=ffta_action_cp_flags(u);uint8_t *s=ffta_job_state(u);
 if((f&FFTA_CP_WARD) && (damage || (f&FFTA_CP_WARD_CANDIDATE)) &&
    s && ffta_action_cp_claim(u,FFTA_CP_WARD_USED))s[FFTA_CP_MEDIC]&=199u;
 ffta_action_cp_candidate(u,0);
}
static unsigned first_cure(unsigned mask){unsigned n=0;if(mask)while(!(mask&(1u<<n)))n++;return mask?n+1:0;}
void ffta_cp_queue(unsigned *frame){
 if(ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY)return;
 const uint8_t *a=ffta_action_actor();
 for(unsigned i=0;i<64;i++){
  uint8_t *u=(uint8_t *)ffta_action_unit_at(i);if(!u)break;
  unsigned f=ffta_action_cp_flags(u),action=0,claim=0,cure=0,percent=25;
  uint8_t *s=ffta_job_state(u);if(!alive(u)||!s||ffta_native_undead(u))continue;
  if((f&FFTA_CP_DAMAGED) && hostile(a,u)){
   if((f&FFTA_CP_TRIAGE) && !(f&FFTA_CP_TRIAGE_QUEUED)){
    action=460;claim=FFTA_CP_TRIAGE_QUEUED;cure=first_cure(ffta_cp_ailments(u)&~f);
   }else if((f&FFTA_CP_DRESSING_ADMITTED) && !(f&FFTA_CP_DRESSING_QUEUED) &&
      !(s[FFTA_CP_MEDIC]&64u) && half(u+0x18)*2u<=half(u+0x1a) &&
      reaction(u)==FFTA_PHY_REACTION && ffta_viking_reaction_ready(u)){
    action=462;claim=FFTA_CP_DRESSING_QUEUED;percent=20;cure=first_cure(ffta_cp_ailments(u));
   }
  }
  if(!action && (f&FFTA_CP_CURED) && !(f&FFTA_CP_FOLLOWUP_QUEUED)){
   action=461;claim=FFTA_CP_FOLLOWUP_QUEUED;
  }
  if(!action)continue;
  unsigned amount=half(u+0x1a)*percent/100u*ffta_recuperation_numerator(u,u)/2u;
  if(amount>999)amount=999;
  if(ffta_reaction_queue_append(frame,u,u,action,160u+action-460u,amount|(cure<<10))){
   ffta_action_cp_claim(u,claim);
   if(action==460)s[FFTA_CP_MEDIC]&=248u;
   return;
  }
 }
}
/* The original callback address is selected by the bounded builder from the
 * installed table, preserving its existing Bard observer and native timers. */
extern uint8_t *ffta_cp_original_application(uint8_t *,unsigned);
uint8_t *ffta_cp_application_observer(uint8_t *c){
 const uint8_t *a=*(const uint8_t *const *)c,*d=*(const uint8_t *const *)(c+0x30);
 uint8_t *u=*(uint8_t **)(c+8);unsigned before=ffta_cp_ailments(u);
 uint8_t *result=ffta_cp_original_application(c,d[1]);
 if(!(c[0x26]&16u) && ffta_action_phase()==FFTA_ACTION_RESULT &&
    ffta_action_origin()==FFTA_ACTION_NATIVE_PRIMARY && ffta_action_paid_count() &&
    a!=u && alive(u) && !hostile(a,u) && !ffta_native_undead(u) &&
    (ffta_action_cp_flags(a)&(FFTA_CP_FOLLOWUP|FFTA_CP_FORCED))==FFTA_CP_FOLLOWUP &&
    (before&~ffta_cp_ailments(u)))ffta_action_cp_claim(u,FFTA_CP_CURED);
 return result;
}
unsigned ffta_cp_status_icon(const uint8_t *u,unsigned key){
 const uint8_t *s=ffta_job_state((uint8_t *)u);if(!alive(u)||!s)return 0;
 if(key==56)return active(s[22]&7u)?key:0;
 if(key==57)return active((s[22]>>3)&7u)?key:0;
 if(key==58)return active(s[23]&7u)?key:0;
 if(key==59)return (s[23]&192u)?key:0;
 return 0;
}
/* Marginal beneficial value uses the original recipient, after native range,
 * affordability and willingness admission. Never reward refreshing a full
 * timer or cure an ailment in a live unit merely to calculate its value. */
unsigned ffta_cp_ai_buff(unsigned id){return id==447 || id==448 || id==452 || id==456 || id==457 || id==458;}
int ffta_cp_ai_value(int native,const uint8_t *a,const uint8_t *t,unsigned id){
 if(!ffta_cp_ai_buff(id))return native;
 if(!alive(a)||!alive(t)||hostile(a,t)||(a[0xeb]&16u)||(id!=457 && ffta_native_undead(t)))return 0;
 unsigned f=ffta_cp_flags(t),value=0;
 if(id==456 || id==458){
  const uint8_t *s=ffta_job_state((uint8_t *)a);
  if(id==456 && (a!=t || !s || active((s[23]>>3)&7u)))return 0;
  if(id==458 && (a==t || half(t+0x18)*2u>half(t+0x1a) ||
     (t[0xe8]&0x41u) || (t[0xeb]&0x70u) || (t[0xec]&1u)))return 0;
  uint8_t *peers[36];unsigned n=ffta_job_peers((uint8_t *)a,peers,36);
  for(unsigned i=0;i<n;i++)if(alive(peers[i]) && hostile(a,peers[i]) &&
     distance(t,peers[i])<=(id==456?6u:2u))return id==456?-16:-24;
  return 0;
 }
 if(id==447)value=(f&FFTA_CP_TRIAGE)?0:25;
 if(id==452)value=(f&FFTA_CP_WARD)?0:25;
 if(id==457)value=(f&FFTA_CP_SMOKE)?0:20;
 if(id==448){
  value=ffta_inoculated_active(t)?0:20;
  for(unsigned ailments=f&FFTA_CP_AILMENTS;ailments;ailments>>=1)if(ailments&1u)value+=20;
 }
 return -(int)value;
}
void ffta_cp_ai_row(uint8_t *row,const uint8_t *a,const uint8_t *t,unsigned id){
 if(!ffta_cp_ai_buff(id))return;
 int value=half(row+10)?ffta_cp_ai_value((int16_t)half(row+12),a,t,id):0;
 if(!value){for(unsigned i=4;i<20;i++)row[i]=0;return;}
 /* Native candidate filtering recognizes beneficial type82. The executing
  * action still uses its own state callback and exact descriptor vector. */
 row[4]=82;row[5]=row[6]=row[7]=0;row[10]=1;row[11]=0;
 row[12]=(uint8_t)value;row[13]=(uint8_t)(value>>8);row[14]=row[12];row[15]=row[13];
}
