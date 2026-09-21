#include "mystic-knight.h"
#include "evaluated-units.h"
#include "action-snapshot.h"

extern unsigned ffta_snapshotted_evaluated_init(void *,const uint8_t *);
extern void ffta_snapshotted_evaluated_close(void *);
extern unsigned ffta_primary_weapon(const uint8_t *);
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static void put(uint8_t *p,unsigned n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}

/* Each branch simulates native weapon order on independent actor/target
 * copies. Status laws also consider a preceding miss when accuracy permits;
 * resource ranking uses the ordinary successful-component branch. */
__attribute__((noinline)) static uint32_t forecast(const uint8_t *a,const uint8_t *t,unsigned policy){
 unsigned kind=ffta_myk_enchantment(a);
 unsigned descriptor=kind==4?125:kind==5?97:kind==6?111:kind==9?104:0;
 unsigned status=kind==4?9:kind==5?26:kind==6?27:22;
 if((!descriptor && kind!=7 && kind!=10) || !t || a==t || !half(t+0x18) || (t[0xe8]&64u) ||
    ffta_action_origin()==FFTA_ACTION_NATIVE_REACTION ||
    ffta_action_origin()==FFTA_ACTION_EXPLICIT_COMBO)return 0;
 FFTA_EvaluatedUnit actor_copy,copy;
 if(!ffta_snapshotted_evaluated_init(&actor_copy,a))return 0;
 if(!ffta_snapshotted_evaluated_init(&copy,t)){
  ffta_snapshotted_evaluated_close(&actor_copy);return 0;
 }
 a=actor_copy.unit;
 uint8_t *target=copy.unit,*c=(uint8_t *)0x0200f3f0u,saved[0x34];
 for(unsigned i=0;i<sizeof(saved);i++)saved[i]=c[i];
 volatile uint32_t *rng=(volatile uint32_t *)0x030034b0u;uint32_t old=*rng;
 uint16_t sorted[2]={0,0},equipped[2]={0,0};unsigned result=0;
 unsigned count=((unsigned (*)(const uint8_t *,uint16_t *))0x0812f0d9u)(a,sorted);
 unsigned slots=((unsigned (*)(const uint8_t *,uint16_t *))0x0812e4f5u)(a,equipped);
 unsigned primary=0;
 if(slots==2){
  unsigned first=((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(equipped[0],10)&255u;
  unsigned second=((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(equipped[1],10)&255u;
  primary=second>first;
 }
 if(count>2 || primary>=count)count=0;
 for(unsigned i=0;i<count && i<=primary;i++){
  unsigned chance=((unsigned (*)(const uint8_t *,const uint8_t *,unsigned,unsigned))0x0812c8ddu)(a,target,1,0);
  if(i<primary && (policy&1u)){if(chance>=100)break;continue;}
  if(!chance)continue;
  int damage=ffta_myk_fight_component_preview(a,target,sorted[i],i,descriptor && !(policy&2u));
  if(i<primary && ((unsigned (*)(unsigned))0x08130655u)(sorted[i])){
   /* Original drain credits its actor before the following weapon. Its
    * negative (undead/absorbed) result can debit the actor instead. */
   int hp=(int)half(a+0x18)+damage;unsigned maximum=half(a+0x1a);
   put(actor_copy.unit+0x18,hp<0?0:(unsigned)hp>maximum?maximum:(unsigned)hp);
   if(!half(a+0x18))break;
  }
  if(damage<0){
   unsigned hp=half(target+0x18)+(unsigned)(-damage),maximum=half(target+0x1a);
   put(target+0x18,hp>maximum?maximum:hp);
   ((void (*)(uint8_t *,unsigned))0x08133bb5u)(target,21);
   if(i<primary)((void (*)(unsigned,unsigned,uint8_t *))0x08130689u)(sorted[i],0,target);
   continue;
  }
  if(!damage)continue;
  if(((unsigned (*)(const uint8_t *))0x0812e6a5u)(target)==13 &&
     ((unsigned (*)(const uint8_t *,const uint8_t *,unsigned,unsigned))0x0812e6e1u)(a,target,0,13)){
   unsigned mp=half(target+0x1c);put(target+0x1c,(unsigned)damage>=mp?0:mp-(unsigned)damage);
   continue;
  }
  unsigned hp=half(target+0x18);
  unsigned removed=(unsigned)damage>hp?hp:(unsigned)damage;
  if(i==primary && (kind==7 || kind==10)){
   result=ffta_myk_resource_plan(a,target,kind,removed);break;
  }
  if((unsigned)damage>=hp)break; /* no status stage on a defeated recipient */
  put(target+0x18,hp-(unsigned)damage);
  /* Same damage-sensitive cleanup as native A2DBA, on the owned copy. This
   * allows a successful Sleep Blade to reapply Sleep after the hit wakes it. */
  ((void (*)(uint8_t *,unsigned))0x08133bb5u)(target,21);
  if(i!=primary){
   ((void (*)(unsigned,unsigned,uint8_t *))0x08130689u)(sorted[i],0,target);
   continue;
  }
  /* Native generic status ranking rewards refreshes. A persistent Fight
   * rider has no new value when its ailment survives the damage cleanup.
   * Sleep is different: the hit wakes it, so applying it again is useful. */
  if((policy&2u) && (target[0xe8+status/8]&(1u<<(status%8))))break;
  ((void (*)(unsigned,unsigned,unsigned))0x0812f2a5u)(0,ffta_primary_weapon(a),1);
  *(const uint8_t **)c=a;*(uint8_t **)(c+4)=target;*(uint8_t **)(c+8)=target;
  *(const uint8_t **)(c+0x30)=*(const uint8_t *const *)0x0812f2a0u+descriptor*4u;
  c[0x26]|=16u;c[0x28]=1;
  unsigned accuracy=0;
  if(((unsigned (*)(void))0x08130fbdu)() && (accuracy=((unsigned (*)(void))0x08131379u)())){
   /* Native law prediction applies the admitted status without a random
    * roll. Native setters and prevention observers determine the output mask,
    * including Astra, Immunity, Inoculated and War Cry. */
   ((void (*)(void))0x0813388du)();
   if(c[0x10+status/8]&(1u<<(status%8)))result=(policy&2u)?accuracy:status+1;
  }
 }
 *rng=old;for(unsigned i=0;i<sizeof(saved);i++)c[i]=saved[i];
 ffta_snapshotted_evaluated_close(&copy);ffta_snapshotted_evaluated_close(&actor_copy);
 return result;
}
unsigned ffta_myk_fight_status_forecast(const uint8_t *a,const uint8_t *t){
 unsigned kind=ffta_myk_enchantment(a);
 if(kind!=4 && kind!=5 && kind!=6 && kind!=9)return 0;
 unsigned result=forecast(a,t,0);
 return result?result:forecast(a,t,1);
}
uint32_t ffta_myk_fight_resource_forecast(const uint8_t *a,const uint8_t *t){
 unsigned kind=ffta_myk_enchantment(a);
 return kind==7 || kind==10?forecast(a,t,0):0;
}
int ffta_myk_fight_ai_value(int native,const uint8_t *a,const uint8_t *t){
 if(!native || !a || !t)return native;
 unsigned kind=ffta_myk_enchantment(a);
 if((kind!=4 && kind!=5 && kind!=6 && kind!=7 && kind!=9 && kind!=10) ||
    !((unsigned (*)(const uint8_t *,const uint8_t *,unsigned))0x080c48a5u)(a,t,0))return native;
 uint32_t plan=(kind==7 || kind==10)?ffta_myk_fight_resource_forecast(a,t):0;
 /* Add the same resource units as actual execution: target MP loss and actor
  * recovery are benefits; undead actor loss is a cost. No HP damage is added
  * again. Native side/target legality and downstream ranking remain in place. */
 int value=native+(int)(plan&65535u)-(int16_t)(plan>>16);
 /* Native C257C adds status accuracy to its effect value. Reuse the native
  * S chance only after the owned simulation actually admits the rider. AI
  * ranking uses the ordinary successful/average branch, not a law warning's
  * optimistic missed-offhand or minimum-damage branch. */
 if(kind==4 || kind==5 || kind==6 || kind==9)value+=(int)forecast(a,t,2);
 return value>32767?32767:value< -32768?-32768:value;
}
