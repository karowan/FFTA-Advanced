#include "registry.h"
#include "geomancer.h"
#include "ai-choice.h"
#include "chemist-items.h"
#include "medicine-ai.h"

/* Native C01D0 owns this node and its buffers. One proposed origin is examined
 * per callback, then C0B46 publishes the winning native action/extra/coordinates.
 * No live unit is moved, and no candidate position survives in saved state. */
static unsigned h(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static void sh(uint8_t *p,unsigned n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static unsigned distance(unsigned x,unsigned y,unsigned a,unsigned b){
 return (x>a?x-a:a-x)+(y>b?y-b:b-y);
}
static unsigned hostile(const uint8_t *a,const uint8_t *t){
 return (((a[0x29]>>7)^((a[0xeb]>>5)&1u))!=(t[0x29]>>7));
}
unsigned ffta_geo_ai_row_options(FFTA_AIChoiceScope *scope,uint8_t *options,unsigned *positions){
 const uint8_t *a=scope->actor;
 unsigned count=1,seen=1u<<2;options[0]=2;positions[0]=0;
 unsigned move=((unsigned (*)(const uint8_t *))0x080ca395u)(a);
 if(move>30)move=30;
 /* Native action ranking precedes the detailed path search. Discover each
  * potential element within the movement radius once, without pretending that
  * straight-line reach proves a legal path. The search later verifies every
  * origin with the actual native movement map before publishing a choice. */
 for(unsigned y=0;y<16 && count<5;y++)for(unsigned x=0;x<16 && count<5;x++){
  if(distance(x,y,a[0xf6],a[0xf7])>move)continue;
  scope->position=0x10000u|x|(y<<8);
  uint8_t available[5];unsigned n=ffta_geo_choices(a,FFTA_GEO_A8,available);
  for(unsigned i=0;i<n;i++)if(!(seen&(1u<<available[i]))){
   seen|=1u<<available[i];options[count]=available[i];positions[count++]=scope->position;
  }
 }
 scope->position=0;return count;
}
unsigned ffta_geo_ai_recipients(const uint8_t *node,const uint8_t **units){
 unsigned count=0;
 for(unsigned group=0;group<2;group++){
  const uint8_t *g=*(const uint8_t *const *)(node+12+4*group);
  if(!g)continue;
  unsigned n=h(g+0x2908);if(n>13)n=13;
  for(unsigned i=0;i<n;i++){
   const uint8_t *w=*(const uint8_t *const *)(g+i*808u);
   const uint8_t *u=w?*(const uint8_t *const *)w:0;
   if(!u || !h(u+0x18) || (u[0xe8]&64u))continue;
   unsigned j=0;while(j<count && units[j]!=u)j++;
   if(j==count)units[count++]=u;
  }
 }
 return count;
}
static int expected(const uint8_t *a,const uint8_t *t,unsigned action,unsigned choice,unsigned x,unsigned y){
 if(a==t || !((unsigned (*)(const uint8_t *,const uint8_t *,unsigned))0x080c48a5u)(a,t,action))return 0;
 unsigned chance=((unsigned (*)(const uint8_t *,const uint8_t *,unsigned,unsigned))0x0812dba9u)(a,t,action,0);
 if(chance>100)chance=100;
 int amount=((int (*)(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned,unsigned))0x08130201u)(a,t,action,choice,0,2);
 if(amount>(int)h(t+0x18))amount=(int)h(t+0x18);
 if(amount<0 && -amount>(int)(h(t+0x1a)-h(t+0x18)))amount=-(int)(h(t+0x1a)-h(t+0x18));
 int value=amount*(int)chance;
 if(action==FFTA_GEO_A3 && amount>0 && (ffta_geo_affinity(a)&FFTA_GEO_WATER)){
  uint8_t px,py;
  if(ffta_geo_push_destination(t,choice,&px,&py) && !(px==x && py==y)){
   /* A modest spacing bonus, never a substitute for positive HP damage.
    * Simultaneous pushes use the current occupancy, like native previews. */
   int delta=(int)distance(px,py,x,y)-(int)distance(t[0xf6],t[0xf7],x,y);
   value+=delta*4*(int)chance;
  }
 }
 return hostile(a,t)?value:-2*value;
}
extern unsigned ffta_geo_original_search(uint8_t *,unsigned);
__attribute__((noinline)) static unsigned choice_search(uint8_t *node,unsigned flags){
 unsigned action=h(node+8);
 if(action!=FFTA_GEO_A3 && action!=FFTA_GEO_A8)return ffta_geo_original_search(node,flags);
 const uint8_t *w=*(const uint8_t *const *)node,*a=w?*(const uint8_t *const *)w:0;
 uint8_t *buffer=*(uint8_t **)(node+0x204);
 unsigned cursor=h(node+0x1b8);
 if(!a || !buffer || cursor>=256)return 0;
 if(!cursor){*(int *)(node+0x1c)=0;node[0x1b1]=0;}
 const uint8_t *anchor=*(const uint8_t *const *)(node+4);
 anchor=anchor?*(const uint8_t *const *)anchor:a;
 unsigned x=0,y=0;
 /* Skip unusable grid cells synchronously; yield only after useful work.
  * Otherwise every rejected cell costs a native AI scheduler interval. */
 for(;cursor<256;cursor++){
  x=cursor&15u;y=cursor>>4;
  if(((unsigned (*)(uint8_t *,unsigned,unsigned,unsigned,unsigned))0x080be075u)(node,x,y,anchor[0xf6],anchor[0xf7]))break;
 }
 sh(node+0x1b8,cursor+1);
 if(cursor==256)return 0;
 FFTA_AIChoiceScope scope;ffta_ai_choice_begin(&scope,a,action,0,0x10000u|x|(y<<8));
 uint8_t options[5];unsigned options_count=ffta_geo_choices(a,action,options);
 const uint8_t *units[26];unsigned count=ffta_geo_ai_recipients(node,units);
 int values[5][26];
 for(unsigned k=0;k<options_count;k++){
  scope.choice=options[k];
  for(unsigned j=0;j<count;j++)values[k][j]=expected(a,units[j],action,options[k],x,y);
 }
 struct {const uint8_t *actor;uint8_t x,y,cx,cy;uint16_t action,extra;} descriptor={a,x,y,x,y,action,0};
 unsigned centers=((unsigned (*)(const void *,unsigned,unsigned,void *))0x080b4a1du)(&descriptor,0,0,buffer);
 /* Range4 has at most41 cells. The separate512-byte slices exceed the native
  * maximum for these two fixed actions and fit the native1024-byte node
  * allocation. Native list records contain x,y and two flags. */
 if(centers>128)centers=0;
 for(unsigned i=0;i<centers;i++){
  unsigned cx=buffer[4*i],cy=buffer[4*i+1];
  descriptor.x=descriptor.cx=(uint8_t)cx;descriptor.y=descriptor.cy=(uint8_t)cy;
  unsigned tiles=((unsigned (*)(const void *,unsigned,unsigned,void *))0x080b4a1du)(&descriptor,0,1,buffer+512);
  if(tiles>128)continue;
  for(unsigned k=0;k<options_count;k++){
   int score=0;
   for(unsigned j=0;j<count;j++){
    for(unsigned tile=0;tile<tiles;tile++)if(buffer[512+4*tile]==units[j][0xf6] && buffer[513+4*tile]==units[j][0xf7]){
     score+=values[k][j];break;
    }
   }
   int best=*(int *)(node+0x1c);
   unsigned movement=distance(x,y,a[0xf6],a[0xf7]);
   unsigned previous=distance(node[0x1ac],node[0x1ad],a[0xf6],a[0xf7]);
   if(score>0 && (score>best || (score==best && movement<previous))){
    *(int *)(node+0x1c)=score;sh(node+10,options[k]);
    node[0x1ac]=(uint8_t)x;node[0x1ad]=(uint8_t)y;
    node[0x1ae]=(uint8_t)cx;node[0x1af]=(uint8_t)cy;node[0x1b0]=0;node[0x1b1]=1;
   }
  }
 }
 ffta_ai_choice_end(&scope);return cursor<255;
}

/* Dispatch before allocating the multi-choice search's large local matrix.
 * Utility forecasts must not inherit that unrelated IWRAM stack frame. */
unsigned ffta_geo_ai_search(uint8_t *node,unsigned flags){
 unsigned action=h(node+8);
 if(ffta_geo_ai_utility(action))return ffta_geo_ai_utility_search(node,flags);
 if(ffta_chemist_action(action))return ffta_medicine_ai_search(node,flags);
 /* The compiled multi-choice frame is764 bytes, even on its early fallback.
  * Ordinary commands must never inherit that matrix on the native AI stack. */
 if(action!=FFTA_GEO_A3 && action!=FFTA_GEO_A8)return ffta_geo_original_search(node,flags);
 return choice_search(node,flags);
}
