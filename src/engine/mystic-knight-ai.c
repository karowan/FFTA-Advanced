#include "mystic-knight.h"
#include "ai-choice.h"
#include "registry.h"
#include "evaluated-units.h"
#include "native-unit.h"

extern int ffta_ai_original_score(const uint8_t *,const uint8_t *,unsigned,unsigned);
extern unsigned ffta_primary_weapon(const uint8_t *);
extern void ffta_ai_original_row(uint8_t *,const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned);
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}

/* Spellbreak keeps one action record. Evaluate the explicitly selected buff
 * on this target, preserving native damage, hit, law and movement consumers.
 * A modest removal value allows a useful dispel even with zero HP damage;
 * otherwise damage after the chosen removal determines the best option. */
static unsigned spellbreak_target(const uint8_t *a,const uint8_t *t,unsigned choice){
 return a && t && a!=t && (((a[0x29]>>7)^((a[0xeb]>>5)&1u))!=(t[0x29]>>7)) &&
  ffta_myk_dispellable(t,choice) && !(a[0xeb]&24u) &&
  ffta_myk_weapon(ffta_primary_weapon(a));
}
int ffta_myk_ai_spellbreak_value(int native,const uint8_t *a,const uint8_t *t,unsigned choice){
 if(!spellbreak_target(a,t,choice))return 0;
 unsigned chance=((unsigned (*)(const uint8_t *,const uint8_t *,unsigned,unsigned))0x0812dba9u)(a,t,FFTA_MYK_A12,0);
 if(!chance)return 0;
 if(chance>100)chance=100;
 int value=native+(int)(20u*chance/100u);
 return value>32767?32767:value;
}
__attribute__((noinline)) void ffta_myk_ai_spellbreak_row(uint8_t *row,const uint8_t *actor,const uint8_t *target,unsigned flags){
 const uint8_t *a=*(const uint8_t *const *)actor,*t=*(const uint8_t *const *)target;
 FFTA_AIChoiceScope scope;ffta_ai_choice_begin(&scope,a,FFTA_MYK_A12,0,0);
 uint8_t candidate[20];int best=0;
 for(unsigned i=0;i<20;i++)row[i]=0;
 row[0]=(uint8_t)FFTA_MYK_A12;row[1]=(uint8_t)(FFTA_MYK_A12>>8);
 for(unsigned choice=1;choice<=FFTA_MYK_DISPEL_CHOICES;choice++){
  if(!spellbreak_target(a,t,choice))continue;
  scope.choice=choice;
  for(unsigned i=0;i<20;i++)candidate[i]=0;
  ffta_ai_original_row(candidate,actor,target,FFTA_MYK_A12,choice,flags);
  if(!half(candidate+10))continue;
  int value=ffta_myk_ai_spellbreak_value((int16_t)half(candidate+12),a,t,choice);
  if(value>best){
   best=value;candidate[12]=(uint8_t)value;candidate[13]=(uint8_t)(value>>8);
   for(unsigned i=0;i<20;i++)row[i]=candidate[i];
  }
 }
 ffta_ai_choice_end(&scope);
}

/* AI values are signed from the recipient's perspective. A self preparation
 * is a small benefit, not the native H-stage's zero damage plus 100 hit value.
 * Prepare only a bare blade: otherwise successive turns can cycle enchants.
 * This is planning policy only; player refreshes and attack-and-enchant keep
 * their normal eligibility. Native AI also classifies the application kind:
 * use its non-HP beneficial-status category (Protect82) in this forecast row
 * only. Execution still dispatches the original Mystic action/descriptors;
 * no Protect is granted and native hit/law flags remain untouched. */
int ffta_myk_ai_self_value(int native,const uint8_t *a){
 return native>0 && !ffta_myk_enchantment(a)?-20:0;
}
void ffta_myk_ai_self_row(uint8_t *row,const uint8_t *a){
 int value=half(row+10)?ffta_myk_ai_self_value((int16_t)half(row+12),a):0;
 if(!value){for(unsigned i=4;i<20;i++)row[i]=0;return;}
 row[4]=82;row[5]=0;
 row[12]=(uint8_t)value;row[13]=(uint8_t)(value>>8);
 row[14]=row[12];row[15]=row[13];
}

extern unsigned ffta_myk_ai_original_self_search(uint8_t *,unsigned);
unsigned ffta_myk_ai_self_search(uint8_t *node,unsigned flags){
 unsigned action=half(node+8);
 if(ffta_geo_ai_utility(action))return ffta_geo_ai_utility_search(node,flags);
 const uint8_t *w=*(const uint8_t *const *)node;
 if(action<FFTA_MYK_A1 || action>FFTA_MYK_A11 ||
    w!=*(const uint8_t *const *)(node+4))return ffta_myk_ai_original_self_search(node,flags);
 const uint8_t *a=w?*(const uint8_t *const *)w:0;
 node[0x1b1]=0;
 /* Native self-centered area search excludes its caster at BE6C2, so a
  * self-only preparation has zero recipients. Admit the real candidate and
  * current movement-map tile, then publish precisely that one self target.
  * No movement is needed; other self/area actions retain the native search. */
 if(!a || ffta_myk_enchantment(a) ||
    !((unsigned (*)(uint8_t *))0x080bdf9du)(node) ||
    !ffta_myk_usable((uint8_t *)a,action,128u))return 0;
 unsigned x=a[0xf6],y=a[0xf7];
 if(!((unsigned (*)(uint8_t *,unsigned,unsigned,unsigned,unsigned))0x080be075u)(node,x,y,x,y))return 0;
 int value=ffta_myk_ai_self_value(ffta_ai_original_score(w,w,action,flags),a);
 if(value>=0)return 0;
 *(int *)(node+0x1c)=-value;*(int *)(node+0x20)=1;
 node[0x1ac]=node[0x1ae]=(uint8_t)x;node[0x1ad]=node[0x1af]=(uint8_t)y;
 node[0x1b0]=0;node[0x1b1]=1;
 return 0;
}

extern int ffta_integrated_mystic_effect_preview(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned);
extern unsigned ffta_snapshotted_evaluated_init(void *,const uint8_t *);
extern void ffta_snapshotted_evaluated_close(void *);
static unsigned enemy(const uint8_t *a,const uint8_t *t){
 return a && t && a!=t && (((a[0x29]>>7)^((a[0xeb]>>5)&1u))!=(t[0x29]>>7));
}
/* Native status value alone undervalues Petrify against an armored, healthy
 * enemy. Add expected remaining HP neutralized, only if native application on
 * an owned target actually admits Petrify. Boss prevention, Astra, Immunity
 * and custom protection keep their native semantics. No random roll or write
 * is lent to the live actor/target. */
int ffta_myk_ai_break_value(const uint8_t *a,const uint8_t *t){
 if(!enemy(a,t) || !half(t+0x18))return 0;
 FFTA_EvaluatedUnit copy;if(!ffta_snapshotted_evaluated_init(&copy,t))return 0;
 uint8_t *c=(uint8_t *)0x0200f3f0u,saved[0x34];
 for(unsigned i=0;i<sizeof(saved);i++)saved[i]=c[i];
 volatile uint32_t *rng=(volatile uint32_t *)0x030034b0u;uint32_t old=*rng;
 ((void (*)(unsigned,unsigned,unsigned))0x0812f2a5u)(FFTA_MYK_A14,ffta_primary_weapon(a),0);
 *(const uint8_t **)c=a;*(uint8_t **)(c+4)=copy.unit;*(uint8_t **)(c+8)=copy.unit;c[0x26]|=16u;
 unsigned chance=0;
 if(((unsigned (*)(void))0x08130fbdu)() && (chance=((unsigned (*)(void))0x08131379u)())){
  ((void (*)(void))0x0813388du)();
  if(!(c[0x10]&64u))chance=0;
 }
 *rng=old;for(unsigned i=0;i<sizeof(saved);i++)c[i]=saved[i];
 ffta_snapshotted_evaluated_close(&copy);
 if(chance>100)chance=100;
 unsigned hp=half(t+0x18);if(hp>999)hp=999;
 return (int)(chance+hp*chance/100u);
}
static __attribute__((noinline)) unsigned mp_shield(const uint8_t *a,const uint8_t *t,unsigned action){
 if(((unsigned (*)(const uint8_t *))0x0812e6a5u)(t)!=13)return 0;
 uint8_t *c=(uint8_t *)0x0200f3f0u,saved[0x34];
 for(unsigned i=0;i<sizeof(saved);i++)saved[i]=c[i];
 volatile uint32_t *rng=(volatile uint32_t *)0x030034b0u;uint32_t old=*rng;
 unsigned result=((unsigned (*)(const uint8_t *,const uint8_t *,unsigned,unsigned))0x0812e6e1u)(a,t,action,13);
 *rng=old;for(unsigned i=0;i<sizeof(saved);i++)c[i]=saved[i];return result;
}
int ffta_myk_ai_strike_value(int native,const uint8_t *a,const uint8_t *t,unsigned action){
 if(action<FFTA_MYK_A1 || action>FFTA_MYK_A11 || !native || !enemy(a,t))return native;
 unsigned bare=!ffta_myk_enchantment(a);
 if(!bare && action!=FFTA_MYK_A7 && action!=FFTA_MYK_A10)return native;
 int damage=ffta_integrated_mystic_effect_preview(a,t,action,ffta_primary_weapon(a),0);
 if(damage<=0)return native;
 if(mp_shield(a,t,action))return native;
 unsigned removed=(unsigned)damage;if(removed>half(t+0x18))removed=half(t+0x18);
 int value=native+(bare && removed &&
  !((action==FFTA_MYK_A7 || action==FFTA_MYK_A10) && ffta_native_undead(t))?20:0);
 if(action==FFTA_MYK_A7 || action==FFTA_MYK_A10){
  unsigned cost=((unsigned (*)(const uint8_t *,unsigned))0x0812ed99u)(a,action);
  uint32_t plan=ffta_myk_resource_plan_after_cost(a,t,action==FFTA_MYK_A7?7:10,removed,cost);
  value+=(int)(plan&65535u)-(int16_t)(plan>>16);
 }
 return value>32767?32767:value< -32768?-32768:value;
}

/* Row16 also gates native random willingness at C359C/12F1DC. Never change
 * it to rank a custom effect. After native sorting, move a better Mystic
 * candidate immediately ahead of Fight within that target's existing rows.
 * Preserve native target order, admission probability, law flags and all
 * complete records. Keep the free native knockout preference. */
void ffta_myk_ai_order(uint8_t *group){
 unsigned count=half(group+0x2908);if(count>13)return;
 for(unsigned u=0;u<count;u++){
  uint8_t *unit=group+u*808u;unsigned n=half(unit+804);if(n>40)continue;
  const uint8_t *w=*(const uint8_t *const *)unit,*t=w?*(const uint8_t *const *)w:0;
  if(!t)continue;
  unsigned fight=n,best=n;int value=0;
  for(unsigned i=0;i<n;i++)if(!half(unit+4+i*20u)){fight=i;break;}
  if(fight==n)continue;
  uint8_t *f=unit+4+fight*20u;
  if((int16_t)half(f+14)>0 && (unsigned)(int16_t)half(f+14)>=half(t+0x18))continue;
  value=(int16_t)half(f+12);
  for(unsigned i=fight+1;i<n;i++){
   uint8_t *r=unit+4+i*20u;unsigned action=half(r);int v=(int16_t)half(r+12);
   if(((action>=FFTA_MYK_A1 && action<=FFTA_MYK_A11) || action==FFTA_MYK_A14) &&
      half(r+10) && v>0 && v>value){best=i;value=v;}
  }
  if(best==n)continue;
  uint8_t row[20];for(unsigned i=0;i<20;i++)row[i]=unit[4+best*20u+i];
  for(unsigned i=best;i>fight;i--)for(unsigned j=0;j<20;j++)unit[4+i*20u+j]=unit[4+(i-1)*20u+j];
  for(unsigned i=0;i<20;i++)f[i]=row[i];
 }
}
extern unsigned ffta_myk_ai_original_rank(uint8_t *,unsigned,unsigned,uint8_t *);
unsigned ffta_myk_ai_rank(uint8_t *ai,unsigned strategy,unsigned side,uint8_t *group){
 unsigned result=ffta_myk_ai_original_rank(ai,strategy,side,group);
 if(side && group)ffta_myk_ai_order(group);
 return result;
}
