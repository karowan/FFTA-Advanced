#include "mystic-knight.h"
#include "battle-workspace.h"
#include "action-snapshot.h"
#include "job-state.h"
#include "registry.h"
#include "bard.h"
#include "geomancer.h"

/* Native controller92784 drives two separate A8194 constructors. Its +AF
 * index advances only at95D04, and all completion/cancellation paths join
 * 95D66. This owner survives between ticks but never becomes an active
 * snapshot. No saved state, borrowed native context bytes or stack pointers. */
typedef struct { const uint8_t *unit,*wrapper; } Reference;
typedef struct {
 unsigned magic,self;const uint8_t *controller,*wrapper,*actor;
 unsigned index,active,seen,count,resolved,references;
 FFTA_ActionCarry units[64];Reference refs[64];
} Continuation;
typedef struct { unsigned magic;Continuation *record;uint8_t *heap;unsigned reserved; } Slot;
_Static_assert(sizeof(Slot)==16,"Doublecast pool reservation");
_Static_assert(sizeof(Continuation)==1836,"Doublecast native allocation");
#define MAGIC 0x3243444du
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static unsigned valid(const void *p,unsigned bytes){
 uintptr_t n=(uintptr_t)p;return !(n&3u) && n>=0x0200000cu && n<=0x0203f000u-bytes;
}
static Slot *slot(void){return ffta_battle_workspace(FFTA_WORKSPACE_DOUBLECAST);}
static Continuation *current(void){
 Slot *s=slot();
 if(!s || s->magic!=MAGIC || s->heap!=*(uint8_t **)0x0200f434u || !valid(s->record,sizeof(Continuation)))return 0;
 const uint16_t *h=(const uint16_t *)((uint8_t *)s->record-12);
 unsigned size=4u*h[3];
 if(h[2]!=0x616c || size<sizeof(Continuation)+12 || size>sizeof(Continuation)+24)return 0;
 Continuation *c=s->record;
 return c->magic==MAGIC && c->self==(unsigned)c && c->count<=64 && c->references<=64?c:0;
}
void ffta_myk_doublecast_retire(void){
 Slot *s=slot();Continuation *c=current();if(!s)return;
 uint8_t *heap=s->heap;
 s->magic=0;s->record=0;s->heap=0;s->reserved=0;
 if(c)((void (*)(void *,void *))0x08007171u)(heap,c);
}
static Continuation *create(const uint8_t *controller,const uint8_t *wrapper){
 ffta_myk_doublecast_retire();
 if(!ffta_additional_workspace_prepare())return 0;
 Slot *s=slot();if(!s)return 0;
 Continuation *c=((Continuation *(*)(unsigned))0x08022841u)(sizeof(*c));
 if(!c)return 0;
 for(unsigned i=0;i<sizeof(*c);i++)((uint8_t *)c)[i]=0;
 c->self=(unsigned)c;c->controller=controller;c->wrapper=wrapper;c->actor=*(const uint8_t *const *)wrapper;c->magic=MAGIC;
 s->heap=*(uint8_t **)0x0200f434u;s->record=c;s->magic=MAGIC;return c;
}
extern unsigned ffta_original_doublecast_construct(uint8_t *,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned);
unsigned ffta_myk_doublecast_construct(uint8_t *wrapper,unsigned action,unsigned item,unsigned x,unsigned y,unsigned mode,unsigned last,const uint8_t *controller,unsigned caller){
 Continuation *c=0;
 if(caller==0x08095b65u && controller==(const uint8_t *)0x0200f4e8u &&
    valid(wrapper,4) && *(const uint8_t *const *)(controller+4)==wrapper &&
    half(controller+0xa6)==33 && controller[0xaf]<2 &&
    half(controller+0xaa+2u*controller[0xaf])==action){
  if(!controller[0xaf])c=create(controller,wrapper);
  else {
   c=current();
   if(c && (c->controller!=controller || c->wrapper!=wrapper ||
      c->actor!=*(const uint8_t *const *)wrapper || c->index!=0 || c->active))c=0;
  }
  if(c){c->index=controller[0xaf];c->active=1;}
 }else ffta_myk_doublecast_retire();
 unsigned result=ffta_original_doublecast_construct(wrapper,action,item,x,y,mode,last);
 if(c)c->active=0;
 return result;
}
static const uint8_t *retained_wrapper(const Continuation *c,const uint8_t *unit){
 for(unsigned i=0;i<c->references;i++)if(c->refs[i].unit==unit &&
    valid(c->refs[i].wrapper,4) && *(const uint8_t *const *)c->refs[i].wrapper==unit)return c->refs[i].wrapper;
 return 0;
}
static void retain(Continuation *c,const uint8_t *wrapper){
 if(!valid(wrapper,4))return;
 const uint8_t *unit=*(const uint8_t *const *)wrapper;
 if(!unit || retained_wrapper(c,unit) || c->references==64)return;
 unsigned known=0;
 for(unsigned i=0;i<64;i++){const uint8_t *u=ffta_action_unit_at(i);if(!u)break;if(u==unit){known=1;break;}}
 if(known){c->refs[c->references].unit=unit;c->refs[c->references++].wrapper=wrapper;}
}
static unsigned can_continue(const Continuation *c){
 const uint8_t *a=c->actor;
 if(!((unsigned (*)(const uint8_t *))0x0812e4a9u)(a) ||
    ((unsigned (*)(const uint8_t *))0x080cd95du)(a) ||
    ((unsigned (*)(const uint8_t *))0x080cdb9du)(a) ||
    ((unsigned (*)(const uint8_t *))0x080cdbb5u)(a))return 0;
 int cost=((int (*)(const uint8_t *,unsigned))0x0812ed99u)(a,half(c->controller+0xac));
 return cost>=0 && (unsigned)cost<=half(a+0x1c);
}
void ffta_myk_doublecast_restore(const uint8_t *u){
 Continuation *c=current();
 if(!c || !c->active || c->index!=1 || c->actor!=u)return;
 for(unsigned i=0;i<c->count;i++){
  FFTA_ActionCarry state=c->units[i];
  /* Native interception/redirect markers describe this subcast's result,
   * not a frozen job benefit. Attunement explicitly prices each subcast. */
  state.unit.flags&=~(24u|(1u<<24));
  if(state.unit.unit==u)state.extra&=~(FFTA_GEO_REFUND|FFTA_GEO_REFUNDED);
  ffta_action_restore_unit(&state);
 }
}
unsigned ffta_myk_doublecast_defer(unsigned *frame){
 Continuation *c=current();
 if(!c || !c->active || c->actor!=ffta_action_actor() ||
    ffta_action_phase()!=FFTA_ACTION_COMPLETING || ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY)return 0;
 if(c->index || c->resolved)return 0;
 /* Only completed native result rows can lend a wrapper to a later queue.
  * Never recover a first-only target by scanning the live roster. */
 retain(c,(const uint8_t *)frame[0x24/4]);
 const uint8_t *output=(const uint8_t *)frame[0x20/4];unsigned count=output[0x26bd];
 if(count<=13)for(unsigned i=0;i<count;i++){
  const uint8_t *object=output+i*0x2c4;unsigned n=object[0x2c0];
  if(n<=15)for(unsigned j=0;j<n;j++)retain(c,*(const uint8_t *const *)(object+0x20+44*j));
 }
 if(can_continue(c))return 1;
 c->resolved=1;return 0;
}
const uint8_t *ffta_myk_doublecast_wrapper(const unsigned *frame,const uint8_t *unit){
 extern unsigned ffta_action_owns_native_frame(const unsigned *);
 Continuation *c=current();
 if(!c || !c->active || c->index!=1 || c->actor!=ffta_action_actor() ||
    !ffta_action_owns_native_frame(frame) || frame[0x24/4]!=(unsigned)c->wrapper)return 0;
 return retained_wrapper(c,unit);
}
unsigned ffta_myk_doublecast_event(const uint8_t *u,unsigned id,unsigned event){
 Continuation *c=current();
 if(!c || !c->active || c->actor!=u || ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY)return 0;
 if(event!=3)return 0;
 if((ffta_action_paid_count() || !id) && (ffta_action_unit_extension_flags(u)&FFTA_MYK_WEAVE) &&
    !(ffta_action_unit_extra_flags(u)&FFTA_BARD_FORCED)){
  unsigned category=ffta_myk_sequence_category(u,id);
  c->seen|=category?category:4u;
 }
 c->count=0;
 for(unsigned i=0;i<64;i++){
  const uint8_t *unit=ffta_action_unit_at(i);if(!unit)break;
  if(ffta_action_export_unit(unit,&c->units[c->count]))c->count++;
 }
 /* Sequence commits once at native completion; the carried snapshot now
  * also owns other jobs' frozen benefits, claims and cumulative HP loss. */
 return 1;
}
void ffta_myk_doublecast_finish(const uint8_t *controller){
 Continuation *c=current();
 if(!c || c->active || c->controller!=controller)return;
 uint8_t *u=(uint8_t *)c->actor;
 if(controller==(const uint8_t *)0x0200f4e8u && half(controller+0xa6)==33 &&
    *(const uint8_t *const *)(controller+4)==c->wrapper && *(const uint8_t *const *)c->wrapper==u &&
    half(u+0x18) && !(u[0xe8]&64u) &&
    ((unsigned (*)(const uint8_t *))0x080cd50du)(u)==FFTA_MYK_S1 && c->seen){
  unsigned flags=0;
  for(unsigned i=0;i<c->count;i++)if(c->units[i].unit.unit==u)flags=c->units[i].extension;
  if(flags&FFTA_MYK_WEAVE){
   uint8_t *s=ffta_job_state(u);
   unsigned value=c->seen==1 || c->seen==2?c->seen:0;
   if(s){unsigned n=(half(s+FFTA_JOB_MYK_BLADE)&0x1fffu)|(value<<13);s[FFTA_JOB_MYK_BLADE]=(uint8_t)n;s[FFTA_JOB_MYK_BLADE+1]=(uint8_t)(n>>8);}
  }
 }
 ffta_myk_doublecast_retire();
}

extern int ffta_integrated_original_exposed_preview(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned,unsigned);
extern unsigned ffta_integrated_direct_kind(const uint8_t *);
/* Read-only contribution of the selected second spell. The caller owns a
 * QUERY snapshot and restores the current native descriptor/RNG. Use the
 * native recipient constructor, including its eligibility filtering, rather
 * than treating a selected area center as the only recipient. Its scratch
 * result/area are heap-owned: never put 5KB on the nested battle stack. */
static int selected_forecast(const uint8_t *wrapper,const uint8_t *t,unsigned action,unsigned item,unsigned x,unsigned y,unsigned prior){
 uint8_t *scratch=((uint8_t *(*)(unsigned))0x08022841u)(0x2c4+0x1000+0x94);
 if(!scratch)return 0;
 for(unsigned i=0;i<0x2c4;i++)scratch[i]=0;
 /* A3778/A3848 also use the native action-query bank before F3F0. */
 uint8_t *saved=scratch+0x2c4+0x1000;volatile uint8_t *bank=(volatile uint8_t *)0x0200f390u;
 for(unsigned i=0;i<0x94;i++)saved[i]=bank[i];
 volatile uint32_t *rng=(volatile uint32_t *)0x030034b0u;uint32_t old=*rng;
 ((unsigned (*)(void *,const void *,const void *,const void *,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned,void *,unsigned))0x080a39f9u)
  (scratch,wrapper,*(const void *const *)(wrapper+0x80),wrapper,x,y,action,item,0,0,scratch+0x2c4,0);
 unsigned found=0,count=scratch[0x2c0];
 if(count<=15)for(unsigned i=0;i<count;i++){
  const uint8_t *w=*(const uint8_t *const *)(scratch+0x20+0x2c*i);
  if(w && *(const uint8_t *const *)w==t){found=1;break;}
 }
 int damage=found?ffta_integrated_original_exposed_preview(*(const uint8_t *const *)wrapper,t,action,item,0,2):0;
 const uint8_t *context=(const uint8_t *)0x0200f3f0u,*descriptor=*(const uint8_t *const *)(context+0x30);
 /* A preceding admitted HP heal changes the later reaction's decision HP.
  * Element absorption is different: its magical hit already claims the one
  * opportunity and forecasts positive pair damage before its own effect. */
 unsigned healing=prior && damage<0 && descriptor && descriptor[1]==38 && descriptor[3]==35;
 if(!healing && (damage<0 || ffta_integrated_direct_kind(context)!=2))damage=0;
 *rng=old;for(unsigned i=0;i<0x94;i++)bank[i]=saved[i];
 ((void (*)(void *))0x08022855u)(scratch);
 return damage;
}

int ffta_myk_doublecast_forecast(const uint8_t *a,const uint8_t *t,unsigned id,unsigned item){
 Continuation *c=current();
 if(!c || !c->active || c->index || c->actor!=a || ffta_action_phase()!=FFTA_ACTION_QUERY)return 0;
 const uint8_t *b=c->controller;
 if(b!=(const uint8_t *)0x0200f4e8u || half(b+0xa6)!=33 || b[0xaf] ||
    *(const uint8_t *const *)(b+4)!=c->wrapper || *(const uint8_t *const *)c->wrapper!=a || half(b+0xaa)!=id)return 0;
 unsigned next=half(b+0xac);
 if(!((unsigned (*)(unsigned,unsigned))0x080ccd51u)(next,19) || !can_continue(c))return 0;
 return selected_forecast(c->wrapper,t,next,item,b[0xcc],b[0xce],0);
}

/* Called only by the native B55CC player forecast, never generic formulas or
 * AI. AE is the selection index (AF is the later execution index). At phase
 * 31h / AE=1 the first area is committed, while CC/CE are still stale. The
 * live targeter's second spell supplies this preview's actual recipient.
 * Backtracking resets AE; exiting retires B+60. No persistent query scope. */
int ffta_myk_doublecast_menu_forecast(int damage,const uint8_t *a,const uint8_t *t,unsigned id,unsigned item){
 const uint8_t *b=(const uint8_t *)0x0200f4e8u;
 if(ffta_action_phase()!=FFTA_ACTION_QUERY || half(b+0xa6)!=33 || b[0xae]!=1 || half(b+0xdc)!=0x31 || half(b+0xac)!=id)return damage;
 const uint8_t *menu=*(const uint8_t *const *)(b+0x60),*wrapper=*(const uint8_t *const *)(b+4);
 if(!valid(menu,0x11c) || !valid(wrapper,0x84) || *(const uint8_t *const *)wrapper!=a ||
    *(const uint8_t *const *)(menu+4)!=wrapper || half(menu+0xec)!=id || half(menu+0xee)!=item)return damage;
 const uint8_t *recipient=*(const uint8_t *const *)(menu+8);
 if(!valid(recipient,4) || *(const uint8_t *const *)recipient!=t)return damage;
 unsigned first=half(b+0xaa);
 if(!((unsigned (*)(unsigned,unsigned))0x080ccd51u)(first,19) ||
    !((unsigned (*)(unsigned,unsigned))0x080ccd51u)(id,19))return damage;
 int first_cost=((int (*)(const uint8_t *,unsigned))0x0812ed99u)(a,first);
 int second_cost=((int (*)(const uint8_t *,unsigned))0x0812ed99u)(a,id);
 if(first_cost<0 || second_cost<0 || (unsigned)(first_cost+second_cost)>half(a+0x1c))return damage;
 int earlier=selected_forecast(wrapper,t,first,half(b+0xa8),b[0xcb],b[0xcd],1);
 if(earlier<0){
  unsigned hp=half(t+0x18),maximum=half(t+0x1a),healed=hp+(unsigned)(-earlier);
  if(healed>maximum)healed=maximum;
  /* Return the current positive damage only when it still triggers at the
   * projected healed HP. This also handles a heal that leaves HP below half. */
  return damage>0 && 2*((int)healed-damage)<=(int)maximum?damage:0;
 }
 return (damage>0?damage:0)+earlier;
}
