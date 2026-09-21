#include "passing-step.h"
#include "registry.h"
#include "action-snapshot.h"
#include "turn-supports.h"

enum { SELECT_MAP=1,SELECT_ROUTE,CONFIRM,ARMED,REVALIDATE,MOVING,RETIRED,AI_MAP };
typedef struct {
 uint32_t magic,phase;
 uint8_t *owner,*wrapper,*actor;
 unsigned budget,cost,count,old38,originX,originY,completed,started;
 uint8_t cursor[36],route[128],fresh[128];
} Passing;
/* Explicit transient reservation inside the permanent4KiB reserved region.
 * No pointers or route data enter persistent/copy-owned unit records. */
static Passing *const s=(Passing *)0x0203f000u;
_Static_assert(sizeof(Passing)<=512,"Passing Step transient reservation");
#define MAGIC 0x50535450u
static uint8_t *const battle=(uint8_t *)0x0200f4e8u;
static uint8_t *const cursor=(uint8_t *)0x0200f3acu;
static unsigned h(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static void sh(uint8_t *p,unsigned v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
static void copy(uint8_t *d,const uint8_t *a,unsigned n){while(n--)*d++=*a++;}
static void clear(void){for(unsigned i=0;i<sizeof(*s)/4;i++)((unsigned *)s)[i]=0;}
static void retire(void){s->count=0;s->completed=s->started=0;s->phase=RETIRED;}
static unsigned movable(const uint8_t *u){
 /* Native status bits: Petrify6, Sleep0, Stop32, Immobilize30. Disable31
  * does not prevent ordinary movement. Silence27 does not prevent dancing. */
 return u && h(u+0x18) && !(u[0xe8]&0x41u) && !(u[0xeb]&0x40u) && !(u[0xec]&1u);
}
static unsigned owned(void){
 return s->magic==MAGIC && s->wrapper && s->actor &&
  *(uint8_t **)(battle+4)==s->wrapper && *(uint8_t **)s->wrapper==s->actor;
}
static uint8_t *grid(void){return *(uint8_t **)(s->wrapper+0x3c);}
static unsigned at_origin(void){return (h(s->wrapper+8)>>5)==s->originX && (h(s->wrapper+12)>>5)==s->originY;}
static void grid_visibility(unsigned yes){
 ((void (*)(void *,unsigned,void *))0x0809a5e1u)(*(void **)battle,yes,s->wrapper);
 ((void (*)(void *,unsigned))0x0809a5c1u)(*(void **)battle,yes);
}
static void prepare_grid(void){
 s->old38=h(s->wrapper+0x38);sh(s->wrapper+0x38,0x30);
 ((void (*)(void *))0x08099ea1u)(s->wrapper);
 uint8_t *g=grid();
 ((void (*)(void *,int,int,unsigned,unsigned,unsigned))0x08149231u)
  (g,(int8_t)g[0x981],(int8_t)g[0x982],s->budget,s->originX,s->originY);
 ((void (*)(void *))0x08099f01u)(s->wrapper);
}
static unsigned ready(void){return ((unsigned (*)(void *))0x08149369u)(grid());}
static unsigned route(unsigned x,unsigned y,uint8_t *out){
 if(x>15 || y>15 || !s->budget || !ready() ||
    !((unsigned (*)(const void *,unsigned,unsigned))0x08149385u)(grid(),x,y))return 0;
 unsigned cost=((unsigned (*)(const void *,unsigned,unsigned))0x081493adu)(grid(),x,y);
 if(!cost || cost>s->budget)return 0;
 int n=((int (*)(void *,unsigned,unsigned,unsigned,void *))0x0809a605u)(s->wrapper,x,y,s->budget,out);
 if(n<2 || n>32 || out[0]!=s->originX || out[1]!=s->originY ||
    out[4*(n-1)]!=x || out[4*(n-1)+1]!=y)return 0;
 s->cost=cost;return (unsigned)n;
}
static unsigned distance(unsigned x,unsigned y,unsigned tx,unsigned ty){
 return (x>tx?x-tx:tx-x)+(y>ty?y-ty:ty-y);
}
unsigned ffta_passing_ai_prepare(void){
 /* The native AI has already chosen its action and approach. Preselect the
  * optional retreat here, before the Act flag/payment, without changing its
  * target, score, RNG or command order. The selected path uses native terrain
  * costs and occupancy, just as the player's path does. */
 const uint8_t *ai=(const uint8_t *)0x020101f8u,*node=ai+0x5290;
 uint8_t *w=*(uint8_t **)(battle+4);
 if(h(ai+0x54be)!=FFTA_DNC_A9 || !w || !movable(*(uint8_t **)w) ||
    *(uint8_t *const *)node!=w || h(node+8)!=FFTA_DNC_A9 || node[0x1b1]!=1){
  if(owned() && !s->owner && s->phase==AI_MAP){sh(w+0x38,s->old38);grid_visibility(0);retire();}
  return 0;
 }
 if(!owned() || s->owner || s->phase!=AI_MAP){
  unsigned budget=ffta_turn_step_remaining(*(uint8_t **)w);
  if(!budget)return 0;
  clear();s->magic=MAGIC;s->phase=AI_MAP;s->wrapper=w;s->actor=*(uint8_t **)w;
  s->budget=budget;s->originX=h(w+8)>>5;s->originY=h(w+12)>>5;
  prepare_grid();return 1;
 }
 grid_visibility(1);
 if(!ready())return 1;
 sh(w+0x38,s->old38);
 unsigned tx=ai[0x54b2],ty=ai[0x54b3];
 unsigned best=distance(s->originX,s->originY,tx,ty),best_cost=0;
 if(tx<=15 && ty<=15 && at_origin())for(unsigned y=0;y<16;y++)for(unsigned x=0;x<16;x++){
  unsigned d=distance(x,y,tx,ty);
  if(d<best)continue;
  unsigned n=route(x,y,s->fresh);
  if(n && (d>best || (s->count && s->cost<best_cost))){
   best=d;best_cost=s->cost;s->count=n;copy(s->route,s->fresh,4*n);
  }
 }
 s->cost=best_cost;grid_visibility(0);s->phase=ARMED;return 0;
}
extern void ffta_passing_original_confirm(void);
void ffta_passing_begin(uint8_t *owner){
 const uint8_t *m=*(const uint8_t *const *)0x0200f438u;
 uint8_t *w=*(uint8_t **)(battle+4);
 if(s->magic==MAGIC && s->phase!=MOVING)clear();
 if(!m || *(unsigned *)(m+20)!=FFTA_DNC_A9 || *(void **)(battle+0x60)!=owner ||
    !w || *(void **)w!=*(void **)(m+24) || !movable(*(uint8_t **)w)){
  ffta_passing_original_confirm();return;
 }
 unsigned budget=ffta_turn_step_remaining(*(uint8_t **)w);
 if(!budget){ffta_passing_original_confirm();return;}
 clear();s->magic=MAGIC;s->phase=SELECT_MAP;s->owner=owner;s->wrapper=w;s->actor=*(uint8_t **)w;
 s->budget=budget;s->originX=h(w+8)>>5;s->originY=h(w+12)>>5;
 copy(s->cursor,cursor,sizeof(s->cursor));prepare_grid();
}
static void finish_selection(void){
 grid_visibility(0);((void (*)(void))0x080231adu)();sh(s->wrapper+0x38,s->old38);
 copy(cursor,s->cursor,sizeof(s->cursor));
 ((void (*)(void *,unsigned))0x08024abdu)(cursor,s->cursor[4]);
 ffta_passing_original_confirm();s->phase=CONFIRM;
}
int ffta_passing_poll(uint8_t *owner,unsigned pressed,unsigned repeat){
 (void)repeat;
 if(s->magic!=MAGIC || s->owner!=owner || s->phase>=CONFIRM){
  int r=((int (*)(void))0x08025465u)();
  if(owned() && s->owner==owner && s->phase==CONFIRM && r){
   if(r>0 && ((unsigned (*)(void))0x080254a1u)()==0x12)s->phase=ARMED;
   else retire();
  }
  return r;
 }
 if(!owned()){retire();return -1;}
 grid_visibility(1);
 if(s->phase==SELECT_MAP){
  if(!ready())return 0;
  sh(s->wrapper+0x38,s->old38);
  ((void (*)(void *))0x0809a625u)(s->wrapper);
  sh(cursor+12,s->originX);sh(cursor+14,h(s->wrapper+10)>>4);sh(cursor+16,s->originY);
  copy(cursor+20,cursor+12,8);((void (*)(void *,unsigned))0x08024abdu)(cursor,1);
  s->phase=SELECT_ROUTE;return 0;
 }
 ((unsigned (*)(void *))0x08098a89u)(s->wrapper);
 if((pressed&2u) || !movable(s->actor)){s->count=0;finish_selection();return 0;}
 if(!(pressed&1u))return 0;
 unsigned x=h(cursor+12),y=h(cursor+16);
 if(x==s->originX && y==s->originY){s->count=0;finish_selection();return 0;}
 unsigned n=route(x,y,s->route);
 if(n){s->count=n;finish_selection();}
 return 0;
}
void ffta_passing_action_event(const uint8_t *u,unsigned action,unsigned event){
 /* A copied prediction, another actor or a nested reaction cannot arm the
  * player route. A confirmation alone does not prove payment/execution. */
 if(!owned() || s->phase!=ARMED || u!=s->actor || action!=FFTA_DNC_A9 ||
    ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY)return;
 if(event==0)s->started=1;
 if(event==3 && s->started && ffta_action_paid_count())s->completed=1;
}
unsigned ffta_passing_after_action(void){
 if(s->magic!=MAGIC || s->phase<ARMED || s->phase==RETIRED || s->phase==AI_MAP)return 0;
 if(!owned()){retire();return 0;}
 if(s->phase==MOVING){
  /* Match the native action's coordinate commit, now after actual movement.
   * Traps may interrupt the animation; retain the tile actually reached. */
  s->actor[0xf6]=(uint8_t)(h(s->wrapper+8)>>5);
  s->actor[0xf7]=(uint8_t)(h(s->wrapper+12)>>5);
  if(!s->owner){
   /* Native AI may have planned Act -> Move -> Wait. A completed finishing
    * step spends Move, so skip only subsequent Move commands (2). Native
    * command1 advances the list without executing a command. */
   uint8_t *ai=(uint8_t *)0x020101f8u;
   unsigned count=ai[0x54e8],current=battle[0x1ac];
   if(count<=4 && current<count)for(unsigned i=current+1;i<count;i++)
    if(ai[0x54e4+i]==2)ai[0x54e4+i]=1;
  }
  ffta_turn_close_movement(s->actor);retire();return 0;
 }
 if(!s->completed || s->count<2 || !movable(s->actor) || !at_origin()){
  if(s->phase==REVALIDATE){sh(s->wrapper+0x38,s->old38);grid_visibility(0);}
  retire();return 0;
 }
 if(s->phase==ARMED){
  unsigned remaining=ffta_turn_step_remaining(s->actor);
  if(remaining<s->budget)s->budget=remaining;
  if(!s->budget){retire();return 0;}
  prepare_grid();s->phase=REVALIDATE;return 1;
 }
 grid_visibility(1);
 if(!ready())return 1;
 sh(s->wrapper+0x38,s->old38);
 unsigned last=4*(s->count-1),n=route(s->route[last],s->route[last+1],s->fresh);
 grid_visibility(0);
 /* Never substitute a newly reconstructed path: every native node, including
  * its height and jump marker, must match the preselected route exactly. */
 if(n!=s->count){retire();return 0;}
 for(unsigned i=0;i<4*n;i++)if(s->fresh[i]!=s->route[i]){retire();return 0;}
 unsigned depth=h(battle+0xde);
 if(depth>=32){retire();return 0;}
 copy(battle+0x124,s->route,4*n);*(unsigned *)(battle+0x1a4)=n;*(void **)(battle+8)=s->wrapper;
 sh(battle+0xe0+2*depth,19);sh(battle+0xde,depth+1);sh(battle+0xdc,40);
 s->phase=MOVING;return 1;
}
void ffta_passing_lifecycle(uint8_t *u,unsigned event){
 if(s->magic!=MAGIC)return;
 /* Simulated lifecycle events on owned AI copies cannot retire a live
  * player's pending route. Only the fixed native roster owns this UI. */
 uintptr_t p=(uintptr_t)u;
 unsigned live=(p>=0x02000080u && p<0x02000080u+24u*264u && (p-0x02000080u)%264u==0) ||
               (p>=0x02002fc4u && p<0x02002fc4u+12u*264u && (p-0x02002fc4u)%264u==0);
 if(!live)return;
 if(event==1 || event==4 || (u==s->actor && event>=2 && event<=5 && s->phase!=MOVING))clear();
}
void ffta_passing_turn_end(uint8_t *u){if(s->magic==MAGIC && u==s->actor)clear();}
