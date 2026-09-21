#include "native-unit.h"
#include "ai-choice.h"
#include "mystic-knight.h"
#include "registry.h"
#include "action-snapshot.h"
#include "evaluated-units.h"
#include "job-state.h"
#include "dark-knight-state.h"
#include "medicine-ai.h"
#include "chemist-items.h"
/* A synchronous native formula owns this stack scope. It is not saved job
 * state, a guessed current target, or a mutation of the frozen snapshot. */
typedef struct { uintptr_t self;const uint8_t *actor,*target;unsigned selected; } MysticDamageScope;
_Static_assert(sizeof(MysticDamageScope)==16,"Mystic formula scope ABI");
#define MYK_DAMAGE_SCOPE ((MysticDamageScope *volatile *)0x0203f72cu)
unsigned ffta_myk_incoming_flags(const uint8_t *a,const uint8_t *t,unsigned id,unsigned flags){
 if(id!=FFTA_MYK_A12)return flags;
 const MysticDamageScope *s=*MYK_DAMAGE_SCOPE;uintptr_t p=(uintptr_t)s,sp;
 __asm__ volatile("mov %0, sp":"=r"(sp));
 if((p&3u)||p<sp||p<0x03000000u||p>0x03008000u-sizeof(*s))return flags;
 if(s->self!=p || s->actor!=a || s->target!=t)return flags;
 if(s->selected==10)flags&=~FFTA_DRK_LAST_RESORT;
 if(s->selected==11)flags&=~FFTA_DRK_TBN;
 return flags;
}
extern unsigned ffta_primary_weapon(const uint8_t *);
extern unsigned ffta_snapshotted_evaluated_init(void *,const uint8_t *);
extern void ffta_snapshotted_evaluated_close(void *);
extern unsigned ffta_drk_usable(uint8_t *,unsigned,unsigned);
extern int ffta_samurai_magnitude(const uint8_t *,uint8_t *,uint8_t *);
extern unsigned ffta_samurai_law_hit(const uint8_t *,unsigned,const uint8_t *,unsigned);
extern int ffta_physical_effective_defense(int,unsigned);
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
/* Admission constructs a query with the weapon as its extra argument. An
 * authenticated AI scope owns the actual selected buff; actual execution
 * always retains its explicit choice, even if interception removed it. */
static unsigned selected_choice(const uint8_t *c){
 if((c[0x26]&16u) && half(c+12)==FFTA_MYK_A12){
  unsigned choice=ffta_ai_preview_choice(*(const uint8_t *const *)c,FFTA_MYK_A12);
  if(choice)return choice;
 }
 return half(c+14);
}
static unsigned alive(const uint8_t *u){return u && half(u+0x18) && !(u[0xe8]&64u);}
static unsigned hostile(const uint8_t *a,const uint8_t *t){return a!=t && (((a[0x29]>>7)^((a[0xeb]>>5)&1u))!=(t[0x29]>>7));}
static unsigned kind(const uint8_t *a){return ffta_action_unit_extension_flags(a)&FFTA_MYK_ENCHANT_MASK;}
extern unsigned ffta_chemist_payment_gate(uint8_t *,unsigned,unsigned,const unsigned *);
unsigned ffta_myk_payment_gate(uint8_t *a,unsigned id,unsigned selected,const unsigned *frame){
 if(ffta_myk_action(id)){
  if(!alive(a)||(a[0xeb]&24u)||!ffta_myk_weapon(ffta_primary_weapon(a)))return 0;
  if(id==FFTA_MYK_A13 && !ffta_myk_release_kind(kind(a)))return 0;
  if(id==FFTA_MYK_A12){
   if(!frame || !selected || selected>FFTA_MYK_DISPEL_CHOICES)return 0;
   uint8_t *peers[FFTA_JOB_UNIT_COUNT],*target=0;
   unsigned count=ffta_job_peers(a,peers,FFTA_JOB_UNIT_COUNT);
   for(unsigned i=0;i<count;i++)if(peers[i][0xf6]==frame[0x44/4] && peers[i][0xf7]==frame[0x48/4]){
    if(target)return 0;
    target=peers[i];
   }
   if(!target || !hostile(a,target) || !ffta_myk_dispellable(target,selected))return 0;
  }
 }
 return ffta_chemist_payment_gate(a,id,selected,frame);
}
extern unsigned ffta_chemist_geometry(const uint8_t *,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned);
extern unsigned ffta_projectile_los(unsigned,unsigned,unsigned,unsigned);
unsigned ffta_myk_geometry(const uint8_t *u,unsigned ax,unsigned ay,unsigned tx,unsigned ty,unsigned id,unsigned item,unsigned mode){
 unsigned result=ffta_chemist_geometry(u,ax,ay,tx,ty,id,item,mode);
 return result && id==FFTA_MYK_A13?ffta_projectile_los((uint8_t)ax,(uint8_t)ay,(uint8_t)tx,(uint8_t)ty):result;
}
unsigned ffta_myk_usable(uint8_t *a,unsigned id,unsigned item){
 if(ffta_chemist_action((uint16_t)id) && !ffta_medicine_available(a,(uint16_t)id))return 0;
 if(ffta_myk_action((uint16_t)id)){
  if(!alive(a)||(a[0xeb]&24u)||!ffta_myk_weapon(ffta_primary_weapon(a)))return 0;
  if(id==FFTA_MYK_A12 && !ffta_myk_dispel_available(a,0))return 0;
  if(id==FFTA_MYK_A13 && !ffta_myk_release_kind(kind(a)))return 0;
 }
 return ffta_drk_usable(a,id,item);
}
unsigned ffta_myk_eligibility(const uint8_t *c){
 if(!c)return 0;
 const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+4);
 unsigned id=half(c+12);
 if(!ffta_myk_action(id)||!alive(a)||!alive(t)||(a[0xeb]&24u)||!ffta_myk_weapon(ffta_primary_weapon(a)))return 0;
 if(id==FFTA_MYK_A13)return a!=t && ffta_myk_release_kind(kind(a));
 if(a==t)return id<=FFTA_MYK_A11 && !c[0x28];
 if(!hostile(a,t))return 0;
 if(id==FFTA_MYK_A12){
  /* Only admission chooses a status. Once the native result has passed the
   * hit/interception boundary, losing that exact status cannot cancel HP. */
  if(!(c[0x26]&16u) && ffta_action_phase()==FFTA_ACTION_RESULT && ffta_action_id()==id)return 1;
  return ffta_myk_dispellable(t,selected_choice(c));
 }
 if(!c[0x28])return 1;
 if(id!=FFTA_MYK_A4 && id!=FFTA_MYK_A5 && id!=FFTA_MYK_A6 && id!=FFTA_MYK_A9)return 0;
 if(!(c[0x26]&16u) && ffta_action_phase()==FFTA_ACTION_RESULT && ffta_action_id()==id)
  return ffta_action_hp_lost(t)>0;
 uint8_t copy[0x34],saved[0x34];volatile uint8_t *scratch=(volatile uint8_t *)0x0200f3f0u;
 for(unsigned i=0;i<sizeof(copy);i++){copy[i]=c[i];saved[i]=scratch[i];}
 const uint8_t *d=*(const uint8_t *const *)0x0812f2a0u;
 *(const uint8_t **)(copy+0x30)=d+63u*4u;copy[0x28]=0;copy[0x26]|=16u;
 volatile uint32_t *rng=(volatile uint32_t *)0x030034b0u;unsigned old=*rng;
 int n=ffta_myk_magnitude(copy);
 if(n>0 && ((unsigned (*)(const uint8_t *))0x0812e6a5u)(t)==13 &&
    ((unsigned (*)(const uint8_t *,const uint8_t *,unsigned,unsigned))0x0812e6e1u)(a,t,id,13))n=0;
 *rng=old;for(unsigned i=0;i<sizeof(copy);i++)scratch[i]=saved[i];
 return n>0;
}
unsigned ffta_myk_accuracy(const uint8_t *c){
 const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+4);
 unsigned id=half(c+12);
 if(id>=FFTA_MYK_A1 && id<=FFTA_MYK_A11 && a==t)return 100;
 return ((unsigned (*)(const uint8_t *))0x0813112du)(c);
}
unsigned ffta_myk_element(const uint8_t *a,unsigned id,unsigned item){
 (void)item;
 if(id>=FFTA_MYK_A1 && id<=FFTA_MYK_A11)return ffta_myk_element_kind(id-FFTA_MYK_A1+1);
 return id==FFTA_MYK_A13?ffta_myk_element_kind(kind(a)):0;
}
int ffta_myk_defense(int defense,unsigned id,const uint8_t *actor,unsigned item){
 return id==FFTA_MYK_A8 || (!id && ffta_myk_fight_kind(actor,item)==8)?
  ((int)(int16_t)defense*3)/4:ffta_physical_effective_defense(defense,id);
}
int ffta_myk_magnitude(const uint8_t *c){
 const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+4);unsigned id=half(c+12);
 if(!a||!t||a==t)return 0;
 if(id==FFTA_MYK_A13){
  if(!ffta_myk_release_kind(kind(a)))return 0;
  if(kind(a)!=8)return ((int (*)(const uint8_t *))0x0813189du)(c);
  /* The internal M44 row supplies the native formula's power BEFORE its
   * rounding. Its result returns through the original Release context and
   * therefore keeps Release's frozen flags, category and final modifiers. */
  uint8_t copy[0x34];for(unsigned i=0;i<sizeof(copy);i++)copy[i]=c[i];
  copy[12]=(uint8_t)FFTA_MYK_FLARE_RELEASE;copy[13]=(uint8_t)(FFTA_MYK_FLARE_RELEASE>>8);
  return ((int (*)(const uint8_t *))0x0813189du)(copy);
 }
 if(!ffta_myk_strike(id)||!ffta_myk_weapon(ffta_primary_weapon(a)))return 0;
 FFTA_EvaluatedUnit predicted;unsigned opened=0;
 if(id==FFTA_MYK_A12){
  opened=ffta_snapshotted_evaluated_init(&predicted,t);
  if(!opened)return 0;
  ffta_myk_dispel(predicted.unit,selected_choice(c));t=predicted.unit;
 }
 MysticDamageScope scope,*previous=*MYK_DAMAGE_SCOPE;
 if(id==FFTA_MYK_A12){
  scope.self=(uintptr_t)&scope;scope.actor=a;scope.target=t;scope.selected=selected_choice(c);
  *MYK_DAMAGE_SCOPE=&scope;
 }
 int result=((int (*)(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned,unsigned,unsigned))0x0812fe39u)
  (a,t,id,ffta_primary_weapon(a),0,(c[0x26]&16u)?2:0,0);
 if(id==FFTA_MYK_A12)*MYK_DAMAGE_SCOPE=previous;
 if(opened)ffta_snapshotted_evaluated_close(&predicted);
 return result;
}
int ffta_myk_success(const uint8_t *c,uint8_t *object,uint8_t *row){
 extern unsigned ffta_integrated_direct_kind(const uint8_t *);
 if(c && ffta_integrated_direct_kind(c)==1)
  ffta_myk_parry_hit(*(const uint8_t *const *)c,*(uint8_t *const *)(c+8),half(c+12));
 if(c && ffta_integrated_direct_kind(c)==2)ffta_myk_shell_hit(c);
 if(c && half(c+12)==FFTA_MYK_A12 && !c[0x28])ffta_myk_dispel(*(uint8_t *const *)(c+8),half(c+14));
 return ffta_samurai_magnitude(c,object,row);
}
unsigned ffta_myk_law_hit(const uint8_t *c,unsigned removal,const uint8_t *byte,unsigned bit){
 if(half(c+12)!=FFTA_MYK_A12 || c[0x28])return ffta_samurai_law_hit(c,removal,byte,bit);
 unsigned choice=half(c+14),status=ffta_myk_dispel_native(choice);
 unsigned removed=ffta_myk_dispel(*(uint8_t *const *)(c+8),choice);
 return removed && removal && status<44 && byte==c+0x10+status/8 && bit==status%8;
}
static void put(uint8_t *p,unsigned n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
/* Pure plan shared by committed execution and forecasts. Low16 is target MP
 * debit; high16 is signed actor resource loss (negative means recovery). */
uint32_t ffta_myk_resource_plan_after_cost(const uint8_t *a,const uint8_t *t,unsigned kind,unsigned removed,unsigned cost){
 if(!a || !t || !removed || !hostile(a,t) || (kind!=7 && kind!=10))return 0;
 unsigned undead=!!ffta_native_undead(t),n;
 if(kind==7){
  n=removed*35u/100u;unsigned cap=half(a+0x1a)*15u/100u;if(n>cap)n=cap;
  unsigned missing=half(a+0x1a)>half(a+0x18)?half(a+0x1a)-half(a+0x18):0;
  if(!undead && n>missing)n=missing;
  return (uint32_t)(uint16_t)(undead?(int)n:-(int)n)<<16;
 }
 n=removed/4u;if(n>10)n=10;if(n>half(t+0x1c))n=half(t+0x1c);
 unsigned mp=half(a+0x1c)>cost?half(a+0x1c)-cost:0;
 unsigned cap=undead?mp:half(a+0x1e)>mp?half(a+0x1e)-mp:0;
 unsigned amount=n<cap?n:cap;
 return n|((uint32_t)(uint16_t)(undead?(int)amount:-(int)amount)<<16);
}
uint32_t ffta_myk_resource_plan(const uint8_t *a,const uint8_t *t,unsigned kind,unsigned removed){
 return ffta_myk_resource_plan_after_cost(a,t,kind,removed,0);
}
void ffta_myk_resource_for_action(uint8_t *t,unsigned before,uint8_t *object,uint8_t *row,unsigned id){
 unsigned after=half(t+0x18);
 if((id!=FFTA_MYK_A7 && id!=FFTA_MYK_A10)||before<=after||ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY)return;
 uint8_t *a=**(uint8_t ***)object;
 if(!a||!hostile(a,t)||!ffta_action_claim_extension(a,FFTA_MYK_RESOURCE_USED))return;
 uint32_t plan=ffta_myk_resource_plan(a,t,id==FFTA_MYK_A7?7:10,before-after);
 int delta=(int16_t)(plan>>16);
 if(id==FFTA_MYK_A7){
  put(object+6,(unsigned)((int16_t)half(object+6)+delta));
 }else{
  unsigned n=plan&65535u;
  put(t+0x1c,half(t+0x1c)-n);put(a+0x1c,(unsigned)((int)half(a+0x1c)-delta));
  if(n){put(row+0xc,half(row+0xc)|2u);put(row+0x20,n);}
 }
}
void ffta_myk_resource(uint8_t *t,unsigned before,uint8_t *object,uint8_t *row){
 ffta_myk_resource_for_action(t,before,object,row,half(object+16));
}
