#include "mystic-knight.h"
#include "action-snapshot.h"
#include "evaluated-units.h"
#include "battle-workspace.h"

extern int ffta_integrated_original_exposed_preview(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned,unsigned);
extern unsigned ffta_integrated_direct_kind(const uint8_t *);
extern unsigned ffta_snapshotted_evaluated_init(void *,const uint8_t *);
extern void ffta_snapshotted_evaluated_close(void *);
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static unsigned ready(const uint8_t *a,const uint8_t *t){
 if(!a || !t || a==t || !half(t+0x18) || (t[0xeb]&1u))return 0;
 unsigned f=ffta_action_unit_extension_reaction_flags(t);
 if(!(f&FFTA_MYK_SHELL_READY) || (f&FFTA_MYK_SHELL_USED))return 0;
 unsigned af=ffta_action_unit_flags(a),tf=ffta_action_unit_flags(t),origin=ffta_action_origin();
 return !(tf&4u) && ((((af>>7)^(af>>8))&1u)!=((tf>>7)&1u)) &&
  origin!=FFTA_ACTION_NATIVE_REACTION && origin!=FFTA_ACTION_EXPLICIT_COMBO &&
  ffta_action_reaction_forecast_enabled();
}
static unsigned threshold(const uint8_t *t,int damage){
 return damage>0 && 2*((int)half(t+0x18)-damage)<=(int)half(t+0x1a);
}
static void grant(uint8_t *t){
 /* Native Shell application83 (1335EC) uses these exact setters: status24
  * and its ordinary three-turn timer. Do not attach the defensive reaction
  * to the enemy spell's status-result mask or refresh pre-existing Shell. */
 ((void (*)(uint8_t *,unsigned))0x080ce071u)(t,1);
 ((void (*)(uint8_t *,unsigned))0x080ce441u)(t,3);
}
/* Keep optional stack-heavy paths out of every native formula's frame.
 * Calling the displaced native preview bypasses this reaction entirely;
 * the child QUERY freezes other factors but cannot publish damage claims. */
__attribute__((noinline)) static int forecast(const uint8_t *a,const uint8_t *t,unsigned id,unsigned item){
 /* Borrow an unused existing result-bank slot with the exact live stack
  * token required by action-snapshot.c. Native recipient construction has a
  * large frame; another820-byte local would overwrite IWRAM clear code. */
 typedef struct { uintptr_t *token;FFTA_ActionSnapshot frame; } Storage;
 _Static_assert(sizeof(Storage)==824,"native snapshot bank stride");
 Storage *bank=ffta_battle_workspace(FFTA_WORKSPACE_RESULTS);
 if(bank)for(unsigned i=0;i<8;i++)if(!bank[i].token && !bank[i].frame.magic){
  FFTA_ActionSnapshot *snapshot=&bank[i].frame;
  uintptr_t token=(uintptr_t)snapshot;bank[i].token=&token;
  unsigned opened=ffta_snapshot_begin(snapshot,a,t,0);
  int damage=0;
  if(opened){
   damage=ffta_integrated_original_exposed_preview(a,t,id,item,0,2);
   /* Immunity/absorption of this element must not hide a damaging second
    * element. The threshold counts eligible HP damage, not healing. */
   damage=(damage>0?damage:0)+ffta_myk_doublecast_forecast(a,t,id,item);
   ffta_snapshot_end(snapshot);
  }
  bank[i].token=0;return damage;
 }
 return 0;
}
void ffta_myk_shell_hit(const uint8_t *c){
 if(!c || (c[0x26]&16u) || ffta_action_phase()!=FFTA_ACTION_RESULT ||
    ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY || !ffta_action_reactions_enabled())return;
 const uint8_t *a=*(const uint8_t *const *)c;
 uint8_t *t=*(uint8_t *const *)(c+8);
 if(!ready(a,t) || ffta_integrated_direct_kind(c)!=2 ||
    !ffta_action_claim_extension(t,FFTA_MYK_SHELL_USED))return;
 /* The success hook follows the native accuracy roll. Its one forecast must
  * not advance RNG, overwrite the active descriptor, or re-enter success. */
 uint8_t saved[0x34];volatile uint8_t *native=(volatile uint8_t *)0x0200f3f0u;
 for(unsigned i=0;i<sizeof(saved);i++)saved[i]=native[i];
 volatile uint32_t *rng=(volatile uint32_t *)0x030034b0u;uint32_t old=*rng;
 int damage=forecast(a,t,half(c+12),half(c+14));
 *rng=old;for(unsigned i=0;i<sizeof(saved);i++)native[i]=saved[i];
 if(threshold(t,damage))grant(t);
}
__attribute__((noinline)) static int protected_preview(const uint8_t *a,const uint8_t *t,unsigned id,unsigned item,unsigned index,unsigned mode,int damage){
 FFTA_EvaluatedUnit copy;
 if(!ffta_snapshotted_evaluated_init(&copy,t))return damage;
 uint8_t saved[0x34];volatile uint8_t *native=(volatile uint8_t *)0x0200f3f0u;
 for(unsigned i=0;i<sizeof(saved);i++)saved[i]=native[i];
 volatile uint32_t *rng=(volatile uint32_t *)0x030034b0u;uint32_t old=*rng;
 grant(copy.unit);
 damage=ffta_integrated_original_exposed_preview(a,copy.unit,id,item,index,mode);
 *rng=old;for(unsigned i=0;i<sizeof(saved);i++)native[i]=saved[i];
 ffta_snapshotted_evaluated_close(&copy);
 return damage;
}
int ffta_myk_shell_preview(int damage,const uint8_t *a,const uint8_t *t,unsigned id,unsigned item,unsigned index,unsigned mode,unsigned menu){
 if(!ready(a,t))return damage;
 const uint8_t *c=(const uint8_t *)0x0200f3f0u;
 if(half(c+12)!=id || ffta_integrated_direct_kind(c)!=2)return damage;
 int total=menu?ffta_myk_doublecast_menu_forecast(damage,a,t,id,item):damage;
 if(!threshold(t,total))return damage;
 return protected_preview(a,t,id,item,index,mode,damage);
}
