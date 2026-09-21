#include "mystic-knight.h"
#include "battle-workspace.h"
#include "action-snapshot.h"
#include "custom-laws.h"
#include "geomancer.h"

extern unsigned ffta_dancer_preview_choice(const uint8_t *,unsigned,unsigned);
extern unsigned ffta_primary_weapon(const uint8_t *);

/* Native A433C owns fourteen 0x2c4-byte result objects. Preserve enchanted
 * component identity plus successful custom applications per recipient row.
 * This receipt survives reaction cleanup, but is never a saved unit status. */
typedef struct {
 unsigned magic;const uint8_t *container,*actor,*wrapper;
 uint8_t kind[14],reserved[2];
 uint16_t harmful[14];uintptr_t query_owner;
} FightReceipt;
_Static_assert(sizeof(FightReceipt)==64,"Committed law receipt");
#define MAGIC 0x314c464du
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static unsigned weapon_elemental(unsigned action){
 return (action>=360 && action<=362) || action==367 || action==370 || action==408 || action==421 ||
  (action>=424 && action<=431);
}
static unsigned primary_element(const uint8_t *a){
 unsigned item=ffta_primary_weapon(a);
 return item?((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(item,4):0;
}
static FightReceipt *receipt(void){return ffta_battle_workspace(FFTA_WORKSPACE_FIGHT_LAWS);}
static unsigned valid(const void *p,unsigned bytes){
 uintptr_t n=(uintptr_t)p;
 return !(n&3u) && n>=0x02000000u && n<=0x0203f000u-bytes;
}
void ffta_myk_law_begin(void){
 if(ffta_action_phase()!=FFTA_ACTION_EXECUTING || ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY)return;
 FightReceipt *r=receipt();
 if(r)for(unsigned i=0;i<sizeof(*r);i++)((uint8_t *)r)[i]=0;
}
void ffta_myk_law_record(const uint8_t *object,const unsigned *frame,unsigned kind){
 if(!object || kind>11 || !frame || ffta_action_phase()!=FFTA_ACTION_RESULT ||
    ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY || ffta_action_result_object()!=object)return;
 unsigned action=half(object+16);
 if(!kind && action!=355 && action!=373 && action!=379 && action!=404 && action!=405 && action!=381 && action!=422 && !weapon_elemental(action))return;
 const uint8_t *container=(const uint8_t *)frame[8];
 if(!valid(container,0x26d0) || object<container || object>=container+14u*0x2c4u ||
    (unsigned)(object-container)%0x2c4u || (kind && half(object+16)))return;
 const uint8_t *wrapper=*(const uint8_t *const *)object;
 if(!valid(wrapper,4) || *(const uint8_t *const *)wrapper!=ffta_action_actor())return;
 FightReceipt *r=receipt();if(!r)return;
 if(r->magic && (r->container!=container || r->actor!=ffta_action_actor() || r->wrapper!=wrapper))return;
 unsigned index=(unsigned)(object-container)/0x2c4u;
 /* Bind the executed primary before native effects/reactions. The second
  * observation must not replace it after an equipment change. */
 if(weapon_elemental(action) && (r->kind[index]&0x80u))return;
 r->container=container;r->actor=ffta_action_actor();r->wrapper=wrapper;
 /* Command elements share the existing per-object byte with Fight kinds.
  * The high bit distinguishes a recorded non-elemental command from an
  * unbound object. Release reads the frozen snapshot, not consumed fuel. */
 if(action==381)kind=0x80u|ffta_geo_element(r->actor,action,half(object+18));
 if(action==422)kind=0x80u|ffta_myk_element(r->actor,action,0);
 if(weapon_elemental(action))kind=0x80u|primary_element(r->actor);
 r->kind[index]=(uint8_t)kind;r->magic=MAGIC;
}
static int dynamic_element(const unsigned *frame,unsigned movement){
 unsigned action=frame[7];const uint8_t *law=(const uint8_t *)frame[22];
 if(movement || law[4]!=2 || (action!=381 && action!=422 && !weapon_elemental(action)))return -1;
 const uint8_t *a=(const uint8_t *)frame[5],*t=(const uint8_t *)frame[6];
 if(action==360 && a==t)return 0;
 const uint8_t *mask=(const uint8_t *)frame[21];unsigned value=0;
 if(!mask){
  value=weapon_elemental(action)?primary_element(a):action==381?ffta_geo_element(a,action,ffta_dancer_preview_choice(a,action,0)):
   ffta_myk_element(a,action,0);
 }else{
  FightReceipt *r=receipt();
  if(!r || r->magic!=MAGIC || r->actor!=a || !valid(r->container,0x26d0) ||
     !valid(r->wrapper,4) || *(const uint8_t *const *)r->wrapper!=a)return 0;
  unsigned admitted=0;
  for(unsigned i=0;i<14;i++){
   const uint8_t *o=r->container+i*0x2c4u;
   if(!(r->kind[i]&0x80u) || *(const uint8_t *const *)o!=r->wrapper ||
      half(o+16)!=action || o[0x2c0]>15)continue;
   for(unsigned j=0;j<o[0x2c0];j++){
    const uint8_t *row=o+0x20+j*0x2cu,*w=*(const uint8_t *const *)row;
    if(mask==row+0x14 && valid(w,4) && *(const uint8_t *const *)w==t){
     value=r->kind[i]&0x7fu;admitted=1;
    }
   }
  }
  if(!admitted)return 0;
 }
 for(unsigned i=0;i<7;i++)if(value && law[5+i]==value)return 1;
 return 0;
}
/* Called by an actual successful custom setter, including a refresh. Never
 * infer application from a surviving timer: a later reaction may cure it.
 * Native target rows already exist before their effects are resolved. */
void ffta_custom_law_applied(const uint8_t *unit){
 const uint8_t *o=ffta_action_result_object();FightReceipt *r=receipt();
 if(!o || !unit || ffta_action_phase()!=FFTA_ACTION_RESULT ||
    ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY || !r || r->magic!=MAGIC ||
    r->actor!=ffta_action_actor() || !valid(r->container,0x26d0) ||
    o<r->container || o>=r->container+14u*0x2c4u ||
    (unsigned)(o-r->container)%0x2c4u || *(const uint8_t *const *)o!=r->wrapper ||
    half(o+16)!=ffta_action_id() || o[0x2c0]>15)return;
 unsigned index=(unsigned)(o-r->container)/0x2c4u;
 for(unsigned j=0;j<o[0x2c0];j++){
  const uint8_t *w=*(const uint8_t *const *)(o+0x20+j*0x2cu);
  if(valid(w,4) && *(const uint8_t *const *)w==unit)r->harmful[index]|=(uint16_t)(1u<<j);
 }
}
/* The native harmful group has no generic beneficial-status counterpart.
 * Custom effects never acquire a fabricated Poison/Sleep/etc. identity. */
static int custom_committed(const unsigned *frame,unsigned movement){
 unsigned action=frame[7];
 if(movement || (action!=355 && action!=373 && action!=379 && action!=404 && action!=405) ||
    ((const uint8_t *)frame[22])[4]!=16)return -1;
 if(!frame[21])return ffta_custom_law_forecast((const uint8_t *)frame[5],(const uint8_t *)frame[6],action);
 FightReceipt *r=receipt();const uint8_t *mask=(const uint8_t *)frame[21];
 if(!r || r->magic!=MAGIC || r->actor!=(const uint8_t *)frame[5] ||
    !valid(r->container,0x26d0) || !valid(r->wrapper,4) ||
    *(const uint8_t *const *)r->wrapper!=r->actor)return 0;
 for(unsigned i=0;i<14;i++){
  const uint8_t *o=r->container+i*0x2c4u;
  if(*(const uint8_t *const *)o!=r->wrapper || half(o+16)!=action || o[0x2c0]>15)continue;
  for(unsigned j=0;j<o[0x2c0];j++){
   const uint8_t *row=o+0x20+j*0x2cu,*w=*(const uint8_t *const *)row;
   if(mask==row+0x14 && valid(w,4) && *(const uint8_t *const *)w==(const uint8_t *)frame[6])
    return !!(r->harmful[i]&(1u<<j));
  }
 }
 return 0;
}
static unsigned status(unsigned kind){return kind==4?9:kind==5?26:kind==6?27:kind==9?22:255;}
/* New commands retain their own command IDs, while recipes still use items
 * and primary-only techniques must not inherit an unused offhand weapon.
 * Native actor/movement and late hit gates remain outside classification. */
static int carrier_category(const unsigned *frame,unsigned movement){
 unsigned id=frame[7];if(id<347 || id>431 || movement)return -1;
 const uint8_t *law=(const uint8_t *)frame[22];
 /* Theft remains theft inside Reaving. Preserve its real command identity
  * and the native selector for every other mapped command family. */
 if(law[4]==1 && (id==366 || id==367 || id==370))
  for(unsigned i=0;i<7;i++)if(law[5+i]==23)return 1;
 if(law[4]==4)return id>=383 && id<=392;
 if(law[4]!=10)return -1;
 const uint8_t *a=(const uint8_t *)frame[5];
 unsigned uses=(id>=347 && id<=358) || (id>=360 && id<=363) || id==367 || id==370 ||
  id==408 || (id>=410 && id<=421) || id==423 || (id>=424 && id<=431);
 if(id==360 && a==(const uint8_t *)frame[6])uses=0; /* self Last Resort */
 if(!uses)return 0;
 unsigned item=ffta_primary_weapon(a);if(!item)return 0;
 unsigned type=((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(item,3);
 for(unsigned i=0;i<7;i++)if(type && law[5+i]==type)return 1;
 return 0;
}
/* Return -1 to retain the original law selector. Its actor and KO gates have
 * already executed. Seven law values are ORed by the native record format. */
int ffta_myk_fight_law(const unsigned *frame,unsigned movement){
 int category=carrier_category(frame,movement);if(category>=0)return category;
 int element=dynamic_element(frame,movement);if(element>=0)return element;
 int custom=custom_committed(frame,movement);if(custom>=0)return custom;
 if(frame[7] || movement)return -1;
 const uint8_t *law=(const uint8_t *)frame[22];unsigned type=law[4];
 if(type!=2 && type!=15 && type!=16)return -1;
 const uint8_t *a=(const uint8_t *)frame[5],*t=(const uint8_t *)frame[6];
 const uint8_t *mask=(const uint8_t *)frame[21];
 if(!mask){
  unsigned kind=ffta_myk_enchantment(a);if(!kind)return -1;
  unsigned value=type==2?ffta_myk_element_kind(kind):ffta_myk_fight_status_forecast(a,t);
  if(type!=2){if(!value)return 0;--value;if(type==16)return 1;}
  for(unsigned i=0;i<7;i++)if(value && law[5+i]==value)return 1;
  return 0;
 }
 FightReceipt *r=receipt();
 if(!r || r->magic!=MAGIC || r->actor!=a || !valid(r->container,0x26d0) ||
    !valid(r->wrapper,4) || *(const uint8_t *const *)r->wrapper!=a)return -1;
 /* Authenticate the actual committed recipient mask, rather than trusting
  * an arbitrary pointer or rediscovering the actor's current enchantment. */
 unsigned admitted=0;
 for(unsigned i=0;i<14;i++){
  const uint8_t *o=r->container+i*0x2c4u;
  if(*(const uint8_t *const *)o!=r->wrapper || half(o+16) || o[0x2c0]>15)continue;
  for(unsigned j=0;j<o[0x2c0];j++){
   const uint8_t *row=o+0x20+j*0x2c,*w=*(const uint8_t *const *)row;
   if(mask==row+0x14 && valid(w,4) && *(const uint8_t *const *)w==t)admitted=1;
  }
 }
 if(!admitted)return -1;
 for(unsigned i=0;i<14;i++){
  unsigned kind=r->kind[i];if(!kind)continue;
  const uint8_t *o=r->container+i*0x2c4u;
  if(*(const uint8_t *const *)o!=r->wrapper || half(o+16) || o[0x2c0]>15)continue;
  for(unsigned j=0;j<o[0x2c0];j++){
   const uint8_t *row=o+0x20+j*0x2c,*w=*(const uint8_t *const *)row;
   if(!valid(w,4) || *(const uint8_t *const *)w!=t || !(row[0xc]&0x80u) || (row[0xc]&0x40u))continue;
   unsigned value=type==2?ffta_myk_element_kind(kind):status(kind);
   if(type!=2 && (value>=44 || !(row[0x14+value/8]&(1u<<(value%8)))))continue;
   if(type==16)return 1;
   for(unsigned k=0;k<7;k++)if(value && law[5+k]==value)return 1;
  }
 }
 return 0;
}
