#include "custom-laws.h"
#include "battle-workspace.h"
#include "action-snapshot.h"
#include "curable-status.h"
#include "geomancer.h"
#include "job-state.h"
#include "blade-wound.h"
#include "mystic-knight.h"
#include "evaluated-units.h"

/* The existing receipt's last word is transient query ownership, not another
 * saved status. A live stack token authenticates each synchronous bound. */
typedef struct {uintptr_t self;const uint8_t *actor,*target;unsigned action,upper;} Bound;
typedef struct {uintptr_t *token;FFTA_ActionSnapshot frame;} Storage;
_Static_assert(sizeof(Storage)==824,"law query snapshot stride");
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static unsigned tag(unsigned action){return action==355?1:action==373?2:action==379?3:action==404?4:action==405?5:0;}
static Bound **owner(void){uint8_t *p=ffta_battle_workspace(FFTA_WORKSPACE_FIGHT_LAWS);return p?(Bound **)(p+60):0;}
int ffta_custom_law_reference(int n,unsigned action,const uint8_t *a,const uint8_t *t){
 if(n<=0 || !tag(action))return n;
 Bound **cell=owner();if(!cell)return n;
 const Bound *b=*cell;uintptr_t p=(uintptr_t)b,sp;
 __asm__ volatile("mov %0, sp":"=r"(sp));
 if((p&3u)||p<sp||p<0x03000000u||p>0x03008000u-sizeof(*b))return n;
 if(b->self!=p || b->actor!=a || b->action!=action ||
    ffta_action_phase()!=FFTA_ACTION_QUERY)return n;
 /* Reactive Shell creates an explicitly registered evaluated defender. Its
  * scalar forecast belongs to this same target; never substitute live data. */
 if(b->target!=t && (!ffta_evaluated_job((uint8_t *)t) || !ffta_job_origin(t) ||
    ffta_job_origin(t)!=ffta_job_origin(b->target)))return n;
 /* Native130072..13009A: +/-floor(reference/10). This runs before custom
  * coefficients and the native cap, so small/stacked results round correctly. */
 return b->upper?n+n/10:n-n/10;
}
extern unsigned ffta_primary_weapon(const uint8_t *);
extern int ffta_integrated_original_exposed_preview(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned,unsigned);

static unsigned predict(const uint8_t *a,const uint8_t *t,unsigned action,Bound *bound){
 uint8_t *c=(uint8_t *)0x0200f3f0u;
 unsigned item=ffta_primary_weapon(a);
 ((void (*)(unsigned,unsigned,unsigned))0x0812f2a5u)(action,item,0);
 *(const uint8_t **)c=a;*(const uint8_t **)(c+4)=t;*(const uint8_t **)(c+8)=t;c[0x26]|=16u;
 if(!((unsigned (*)(void))0x08130fbdu)() || !((unsigned (*)(void))0x08131379u)())return 0;
 if(ffta_chemist_prevent_custom(c,tag(action)))return 0;
 if(action==373){
  const uint8_t *d=*(const uint8_t *const *)(c+0x30);
  return ffta_job_origin(a) && ffta_job_state((uint8_t *)t) &&
   ((unsigned (*)(const uint8_t *,unsigned))0x08133a59u)(t,d[1]);
 }
 if(half(t+0x18)<=1 || (action==355 && !ffta_owned_wound((uint8_t *)t)))return 0;
 if(action==379 && ffta_geo_wisp(t)==2 && !(ffta_geo_affinity(a)&FFTA_GEO_HEAT))return 0;
 if(((unsigned (*)(const uint8_t *))0x0812e6a5u)(t)==13 &&
    ((unsigned (*)(const uint8_t *,const uint8_t *,unsigned,unsigned))0x0812e6e1u)(a,t,action,13))return 0;
 int n=ffta_integrated_original_exposed_preview(a,t,action,item,0,2);
 n=ffta_myk_shell_preview(n,a,t,action,item,0,2,0);
 if(n>0)return (unsigned)n<half(t+0x18);
 if(n<0)return 0;
 bound->upper=1;
 n=ffta_integrated_original_exposed_preview(a,t,action,item,0,2);
 n=ffta_myk_shell_preview(n,a,t,action,item,0,2,0);
 return n>0;
}
unsigned ffta_custom_law_forecast(const uint8_t *a,const uint8_t *t,unsigned action){
 if(!tag(action) || !a || !t || a==t || !half(a+0x18) || !half(t+0x18) ||
    (t[0xe8]&64u) || (((a[0x29]>>7)^((a[0xeb]>>5)&1u))==(t[0x29]>>7)) ||
    ((unsigned (*)(const uint8_t *))0x080cd50du)(t)==11 || !ffta_job_state((uint8_t *)t))return 0;
 if(!ffta_additional_workspace_prepare())return 0;
 Storage *bank=ffta_battle_workspace(FFTA_WORKSPACE_RESULTS);Bound **cell=owner();
 if(!bank || !cell)return 0;
 for(unsigned i=0;i<8;i++)if(!bank[i].token && !bank[i].frame.magic){
  FFTA_ActionSnapshot *snapshot=&bank[i].frame;uintptr_t token=(uintptr_t)snapshot;
  bank[i].token=&token;unsigned opened=ffta_snapshot_begin(snapshot,a,t,0);
  uint8_t saved[0x34],*c=(uint8_t *)0x0200f3f0u;
  for(unsigned k=0;k<sizeof(saved);k++)saved[k]=c[k];
  volatile unsigned *rng=(volatile unsigned *)0x030034b0u;unsigned old=*rng;
  Bound bound={(uintptr_t)&bound,a,t,action,0},*previous=*cell;*cell=&bound;
  unsigned result=predict(a,t,action,&bound);
  *cell=previous;*rng=old;for(unsigned k=0;k<sizeof(saved);k++)c[k]=saved[k];
  if(opened)ffta_snapshot_end(snapshot);
  else for(unsigned k=0;k<sizeof(*snapshot);k++)((uint8_t *)snapshot)[k]=0;
  bank[i].token=0;return result;
 }
 return 0;
}
