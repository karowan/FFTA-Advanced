#include "mystic-knight.h"
#include "action-snapshot.h"

/* An actual A433C weapon component, never an item-ID guess. The pointer is
 * transient and outside the saved bank; nested calls restore its prior value.
 * Spellbreak owns a different cell, so either scope can nest the other. */
typedef struct { uintptr_t self;const uint8_t *actor,*object;unsigned item,kind;uint8_t *damaged; } FightScope;
#define FIGHT_SCOPE ((FightScope *volatile *)0x0203f730u)
_Static_assert(sizeof(FightScope)==24,"Fight component scope ABI");
extern unsigned ffta_primary_weapon(const uint8_t *);
extern unsigned ffta_original_snapshot_result(uint8_t *,uint8_t *,uint8_t *,unsigned,unsigned,void *,unsigned,unsigned);
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}

unsigned ffta_myk_fight_kind(const uint8_t *actor,unsigned item){
 const FightScope *s=*FIGHT_SCOPE;uintptr_t p=(uintptr_t)s,sp;
 __asm__ volatile("mov %0, sp":"=r"(sp));
 if((p&3u)||p<sp||p<0x03000000u||p>0x03008000u-sizeof(*s))return 0;
 if(s->self!=p || s->actor!=actor || s->item!=item || !s->kind || s->kind>11)return 0;
 if(ffta_action_id()!=0)return 0;
 if(s->object){if(!ffta_action_in_result(s->object,actor))return 0;}
 else if(ffta_action_phase()!=FFTA_ACTION_QUERY || ffta_action_actor()!=actor)return 0;
 return s->kind;
}

/* Native12F0D8/12E55C stably sort the equipment pair. Every recognized
 * forecast below carries the first sorted weapon; BDF54 also exposes its
 * actual loop index. Item equality alone cannot distinguish duplicate blades. */
static unsigned primary_component(const uint8_t *a,unsigned item,unsigned index){
 uint16_t ordered[2]={0,0};
 unsigned count=((unsigned (*)(const uint8_t *,uint16_t *))0x0812e4f5u)(a,ordered);
 if(!count || count>2 || ordered[0]!=item || item!=ffta_primary_weapon(a))return 0;
 unsigned primary=0;
 if(count==2){
  unsigned first=((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(ordered[0],10)&255u;
  unsigned second=((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(ordered[1],10)&255u;
  primary=second>first;
 }
 return index==primary;
}

extern int ffta_integrated_exposed_preview(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned,unsigned);
extern int ffta_integrated_fight_effect_preview(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned);
extern int ffta_integrated_magic_menu_preview(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned);
extern int ffta_integrated_mystic_effect_preview(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned);
/* Effect simulation supplies the actual sorted iteration itself. Unlike the
 * old first-weapon consumers, this can reach equipment-primary second. */
int ffta_myk_fight_component_preview(const uint8_t *a,const uint8_t *t,unsigned item,unsigned iteration,unsigned minimum){
 FightScope scope={0},*previous=*FIGHT_SCOPE;
 if(primary_component(a,item,iteration)){
  scope.self=(uintptr_t)&scope;scope.actor=a;scope.item=item;scope.kind=ffta_myk_enchantment(a);
 }
 *FIGHT_SCOPE=&scope;
 int damage=ffta_integrated_fight_effect_preview(a,t,item,0,minimum);
 *FIGHT_SCOPE=previous;
 return damage;
}
int ffta_myk_fight_preview(const uint8_t *a,const uint8_t *t,unsigned action,unsigned item,const unsigned *frame){
 /* frame: original r4-r7, LR, reaction discriminator, calculation mode.
  * The discriminator is NOT a weapon index. Result-owned formulas retain
  * their already authenticated exact component, including primary-second. */
 unsigned caller=frame[4],reaction=frame[5],mode=frame[6];
 if(caller==0x080a2919u || caller==0x080a2979u)
  return ffta_integrated_exposed_preview(a,t,action,item,reaction,mode);
 FightScope scope={0},*previous=*FIGHT_SCOPE;
 unsigned known=caller==0x080b5731u || caller==0x080bdf59u || caller==0x080c2369u ||
  caller==0x0812e7ddu || caller==0x0812e979u || caller==0x0812e9a9u ||
  caller==0x0812ea03u || caller==0x081356edu;
 unsigned origin=ffta_action_origin();
 unsigned own_result=!ffta_action_result_object() || ffta_action_actor()==a;
 if(a && !action && mode==2 && known && own_result && origin!=FFTA_ACTION_NATIVE_REACTION &&
    primary_component(a,item,caller==0x080bdf59u?frame[0]:0)){
  scope.self=(uintptr_t)&scope;scope.actor=a;scope.item=item;scope.kind=ffta_myk_enchantment(a);
 }
 /* Unknown/nested forecasts shadow the previous query. A forged item-equal
  * call cannot inherit fuel from another forecast or a queued reaction. */
 *FIGHT_SCOPE=&scope;
 /* These native QUERY callers can nest below two evaluated copies (notably
  * Damage-to-MP admission). Use bank storage for their snapshot; real result
  * callers above retain the existing deferred-barrier publication path. */
 int damage=action && mode==2 && caller==0x080b5731u?
  ffta_integrated_magic_menu_preview(a,t,action,item,reaction):
  !action && mode==2 && known?
  ffta_integrated_fight_effect_preview(a,t,item,reaction,0):
  mode==2 && (known || ffta_myk_action((uint16_t)action))?
  ffta_integrated_mystic_effect_preview(a,t,action,item,reaction):
  ffta_integrated_exposed_preview(a,t,action,item,reaction,mode);
 *FIGHT_SCOPE=previous;
 return damage;
}

int ffta_myk_fight_element(const uint8_t *actor,unsigned action,unsigned item){
 /* Weapon-free self Last Resort never invokes a damage formula. The enemy
  * mode passes its actual primary item while retaining action360 throughout. */
 if(action==360)return item?((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(item,4):0;
 unsigned kind=action?0:ffta_myk_fight_kind(actor,item);
 return kind?(int)ffta_myk_element_kind(kind):-1;
}

/* Both native drain callers must be suppressed: formula sign and subsequent
 * actor recovery. The effect3E cleanup is separate; effect3F and equipment
 * properties are deliberately untouched. No item-equal query can bind this. */
unsigned ffta_myk_fight_replace_weapon(unsigned item,unsigned caller){
 if(caller!=0x081300c1u && caller!=0x080a2b11u && caller!=0x080a270bu &&
    caller!=0x080a2dcdu && caller!=0x08133959u)return 0;
 const uint8_t *a=ffta_action_actor();
 return a && ffta_myk_fight_kind(a,item);
}

unsigned ffta_myk_fight_sleep(const uint8_t *c){
 return c && !half(c+12) && c[0x28]==1 &&
  ffta_myk_fight_kind(*(const uint8_t *const *)c,half(c+14))==5;
}

int ffta_myk_fight_restorative(int reference,const uint8_t *a){
 if(reference>0 && a){
  unsigned item=ffta_primary_weapon(a);
  if(ffta_myk_fight_kind(a,item) && ((unsigned (*)(unsigned))0x08130621u)(item))return -reference;
 }
 return reference;
}

/* Only the authenticated native Fight HP writer calls this, before the
 * executor applies the object's accumulated actor HP delta. Per-component
 * actual loss excludes overkill, absorption, misses and MP redirection. */
void ffta_myk_fight_after_hp(uint8_t *target,unsigned before){
 uint8_t *object=(uint8_t *)ffta_action_result_object();
 if(!object || !*(uint8_t **)object || object[0x2c0]>15)return;
 uint8_t *a=**(uint8_t ***)object;
 unsigned kind=ffta_myk_fight_kind(a,half(object+18));
 if(kind && before>half(target+0x18))(*FIGHT_SCOPE)->damaged=target;
 if(kind!=7 && kind!=10)return;
 for(unsigned i=0;i<object[0x2c0];i++){
  uint8_t *row=object+0x20+i*0x2c;
  if(*(uint8_t **)row && **(uint8_t ***)row==target){
   ffta_myk_resource_for_action(target,before,object,row,kind==7?416:419);return;
  }
 }
}

/* Native Fight skips the descriptor loop. Enter one native S stage only
 * AFTER its damage-sensitive-status cleanup, so newly inflicted Sleep stays
 * asleep. Preserve the shared context around the synchronous attempt. */
void ffta_myk_fight_status(uint8_t *object,uint8_t *target){
 if(!object || !target || !*(uint8_t **)object || ffta_action_phase()!=FFTA_ACTION_RESULT)return;
 const uint8_t *a=**(uint8_t ***)object;
 unsigned kind=ffta_myk_fight_kind(a,half(object+18));
 if(!kind || (*FIGHT_SCOPE)->object!=object || (*FIGHT_SCOPE)->damaged!=target)return;
 (*FIGHT_SCOPE)->damaged=0; /* exactly one attempt for this successful component */
 unsigned descriptor=kind==4?125:kind==5?97:kind==6?111:kind==9?104:0;
 /* Fight retains native friendly fire. Unlike Drain/Osmose, the approved
  * status riders have no enemy-only exception after positive HP damage. */
 if(!descriptor || !half(target+0x18))return;
 uint8_t *row=0;
 if(object[0x2c0]>15)return;
 for(unsigned i=0;i<object[0x2c0];i++){
  uint8_t *p=object+0x20+i*0x2c;
  if(*(uint8_t **)p && **(uint8_t ***)p==target){row=p;break;}
 }
 if(!row)return;
 uint8_t *c=(uint8_t *)0x0200f3f0u,saved[0x34];
 for(unsigned i=0;i<sizeof(saved);i++)saved[i]=c[i];
 ((void (*)(unsigned,unsigned,unsigned))0x0812f2a5u)(0,half(object+18),1);
 *(const uint8_t **)c=a;*(uint8_t **)(c+4)=target;*(uint8_t **)(c+8)=target;
 *(const uint8_t **)(c+0x30)=*(const uint8_t *const *)0x0812f2a0u+descriptor*4u;
 c[0x28]=1;
 if(((unsigned (*)(void))0x08130fbdu)()){
  unsigned chance=((unsigned (*)(void))0x08131379u)();
  /* Preserve the executor's ordinary player-side S adjustment. */
  if(chance && !((unsigned (*)(const uint8_t *))0x080c8241u)(a)){
   chance+=10;if(chance>100)chance=100;
  }
  if(((unsigned (*)(unsigned))0x0812f1ddu)(chance)){
   for(unsigned i=0;i<8;i++)c[0x10+i]=row[0x14+i];
   ((void (*)(void))0x0813388du)();
   for(unsigned i=0;i<8;i++)row[0x14+i]=c[0x10+i];
   if(!(half(c+0x26)&0x100u))row[0xc]|=0x80u;
  }
 }
 for(unsigned i=0;i<sizeof(saved);i++)c[i]=saved[i];
}

unsigned ffta_additional_native_result(uint8_t *object,uint8_t *wrapper,uint8_t *manager,unsigned flags,
 unsigned mode,void *scratch,unsigned secondary,unsigned last,const unsigned *frame){
 FightScope scope={0},*previous=*FIGHT_SCOPE;
 /* The frame's original action and current result must both be Fight. Native
  * A4852 carries the actual iteration at+34, unlike the reaction discriminator
  * passed to12FE38.12F0D8 stably sorts the two equipment weapons by power. */
 if(frame && object && !half(object+16) && !frame[0x28/4] && frame[0x38/4]>=1 &&
    frame[0x38/4]<=2 && frame[0x34/4]<frame[0x38/4] && wrapper && *(uint8_t **)wrapper){
  const uint8_t *a=*(uint8_t **)wrapper;
  unsigned kind=ffta_myk_enchantment(a);
  if(kind){
   unsigned item=half(object+18);
   if(primary_component(a,item,frame[0x34/4])){
    scope.self=(uintptr_t)&scope;scope.actor=a;scope.object=object;scope.item=item;scope.kind=kind;
   }
  }
 }
 /* An ineligible nested native result shadows, rather than inherits, fuel. */
 *FIGHT_SCOPE=&scope;
 ffta_myk_law_record(object,frame,scope.kind);
 unsigned result=ffta_original_snapshot_result(object,wrapper,manager,flags,mode,scratch,secondary,last);
 ffta_myk_law_record(object,frame,scope.kind);
 *FIGHT_SCOPE=previous;
 return result;
}
