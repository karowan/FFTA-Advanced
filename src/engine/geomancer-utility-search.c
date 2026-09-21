#include "registry.h"
#include "geomancer.h"
#include "ai-choice.h"
#include "job-state.h"
#include "mystic-knight.h"

static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static void sh(uint8_t *p,unsigned n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static unsigned distance(int x,int y,int a,int b){
 int dx=x-a,dy=y-b;return (unsigned)(dx<0?-dx:dx)+(unsigned)(dy<0?-dy:dy);
}
static unsigned hostile(const uint8_t *a,const uint8_t *t){
 return ((a[0x29]>>7)^((a[0xeb]>>5)&1u))!=(t[0x29]>>7);
}
static int height(unsigned x,unsigned y){return ((int (*)(unsigned,unsigned))0x0801cc19u)(x,y);}
static unsigned covers(const uint8_t *s,unsigned x,unsigned y){
 if(distance(s[15],s[16],x,y)>1)return 0;
 int delta=height(s[15],s[16])-height(x,y);return delta>=-2 && delta<=2;
}

/* Node+204 is the native1024-byte heap allocation, not an IWRAM stack array.
 * Its lifetime already spans this coroutine. First512 bytes are scratch;
 * center/area records occupy512..767; peer scratch occupies768..911. */
typedef struct {
 const uint8_t *units[26];
 int damage[26];
 int16_t benefit[26];
 uint8_t before[26],other[26],ground[26];
} UtilityScratch;
_Static_assert(sizeof(UtilityScratch)<=512,"utility scratch overlaps geometry");
/* Shared heap-backed effect forecast. Its historical Mystic name does not
 * restrict action IDs; this is the same native mode2 formula and Shell policy
 * with an authenticated result-bank snapshot instead of an824-byte stack copy. */
extern int ffta_integrated_mystic_effect_preview(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned);

/* Actual learned/equipped command discovery, MP/status admission and positive
 * native magic forecast. Manhattan move+range is only a potential threat
 * bound, not a claim that an enemy has a legal path or will choose this cast.
 * Stop at the first real offensive spell; shelter's weight remains modest. */
static unsigned magical_threat(const uint8_t *e,const uint8_t *t,unsigned tx,unsigned ty,uint16_t *actions){
 if(!hostile(e,t))return 0;
 unsigned n=((unsigned (*)(uint16_t *,const uint8_t *))0x08134095u)(actions,e);
 if(n>40)n=40;
 unsigned move=((unsigned (*)(const uint8_t *))0x080ca395u)(e);
 for(unsigned i=0;i<n;i++){
  unsigned id=actions[i];
  if(!((unsigned (*)(unsigned,unsigned))0x080ccd51u)(id,28) ||
     !ffta_myk_usable((uint8_t *)e,id,128u))continue;
  unsigned range=((unsigned (*)(unsigned,unsigned))0x080ccd51u)(id,4);
  if(range>16)range=16;
  if(distance(e[0xf6],e[0xf7],tx,ty)>move+range+2)continue;
  if(!((unsigned (*)(const uint8_t *,const uint8_t *,unsigned))0x080c48a5u)(e,t,id))continue;
  unsigned chance=((unsigned (*)(const uint8_t *,const uint8_t *,unsigned,unsigned))0x0812dba9u)(e,t,id,0);
  if(chance && ffta_integrated_mystic_effect_preview(e,t,id,0,0)>0)return 1;
 }
 return 0;
}

unsigned ffta_geo_ai_utility_search(uint8_t *node,unsigned flags){
 (void)flags;
 unsigned action=half(node+8),cursor=half(node+0x1b8);
 const uint8_t *wrapper=*(const uint8_t *const *)node;
 const uint8_t *a=wrapper?*(const uint8_t *const *)wrapper:0;
 uint8_t *buffer=*(uint8_t **)(node+0x204);
 if(!a || !buffer || cursor>=256)return 0;
 if(!cursor){
  node[0x1b1]=0;*(int *)(node+0x1c)=0;
  if(!((unsigned (*)(uint8_t *))0x080bdf9du)(node) ||
     !ffta_myk_usable((uint8_t *)a,action,128u))return 0;
 }
 const uint8_t *anchor=*(const uint8_t *const *)(node+4);
 anchor=anchor?*(const uint8_t *const *)anchor:a;
 unsigned x=0,y=0;
 for(;cursor<256;cursor++){
  x=cursor&15u;y=cursor>>4;
  if(((unsigned (*)(uint8_t *,unsigned,unsigned,unsigned,unsigned))0x080be075u)
      (node,x,y,anchor[0xf6],anchor[0xf7]))break;
 }
 sh(node+0x1b8,cursor+1);if(cursor==256)return 0;
 FFTA_AIChoiceScope scope;ffta_ai_choice_begin(&scope,a,action,0,0x10000u|x|(y<<8));
 UtilityScratch *scratch=(UtilityScratch *)buffer;
 unsigned count=ffta_geo_ai_recipients(node,scratch->units);
 unsigned found=0;for(unsigned i=0;i<count;i++)if(scratch->units[i]==a)found=1;
 if(!found && count<26)scratch->units[count++]=a;
 for(unsigned i=0;i<count;i++){
  const uint8_t *t=scratch->units[i];unsigned tx=t==a?x:t[0xf6],ty=t==a?y:t[0xf7];
  scratch->before[i]=scratch->other[i]=0;scratch->damage[i]=0;scratch->benefit[i]=0;
  scratch->ground[i]=(uint8_t)(ffta_geo_grounded(t)?
   (((unsigned (*)(const uint8_t *))0x080cd50du)(t)==FFTA_GEO_S2?2:3):0);
  if(action==FFTA_GEO_A4){
   int value=ffta_geo_ai_utility_value(0,a,t,action);
   if(value<0)for(unsigned j=0;j<count;j++)if(hostile(t,scratch->units[j])){
    scratch->benefit[i]=(int16_t)-value;break;
   }
  }else{
   if(scratch->ground[i]&2u)for(unsigned j=0;j<count;j++)
    if(magical_threat(scratch->units[j],t,tx,ty,(uint16_t *)(buffer+912))){scratch->benefit[i]=20;break;}
   if(action==FFTA_GEO_A7 && a!=t &&
      ((unsigned (*)(const uint8_t *,const uint8_t *,unsigned))0x080c48a5u)(a,t,action)){
    unsigned chance=((unsigned (*)(const uint8_t *,const uint8_t *,unsigned,unsigned))0x0812dba9u)(a,t,action,0);
    if(chance>100)chance=100;
    int amount=ffta_integrated_mystic_effect_preview(a,t,action,0,0);
    if(amount>(int)half(t+0x18))amount=(int)half(t+0x18);
    if(amount<0 && -amount>(int)(half(t+0x1a)-half(t+0x18)))amount=-(int)(half(t+0x1a)-half(t+0x18));
    scratch->damage[i]=amount*(int)chance*(hostile(a,t)?1:-2);
   }
  }
 }
 if(action!=FFTA_GEO_A4){
  uint8_t **peers=(uint8_t **)(buffer+768);
  unsigned n=ffta_job_peers((uint8_t *)a,peers,36);
  for(unsigned p=0;p<n;p++){
   unsigned kind=ffta_geo_field_kind(peers[p]);if(!kind)continue;
   const uint8_t *s=ffta_job_state(peers[p]);
   for(unsigned i=0;i<count;i++){
    const uint8_t *t=scratch->units[i];unsigned tx=t==a?x:t[0xf6],ty=t==a?y:t[0xf7];
    if((kind==2 && hostile(peers[p],t)) || !covers(s,tx,ty))continue;
    unsigned bit=kind==1?1:2;scratch->before[i]|=bit;
    if(peers[p]!=a)scratch->other[i]|=bit;
   }
  }
 }
 struct {const uint8_t *actor;uint8_t x,y,cx,cy;uint16_t action,extra;} descriptor={a,x,y,x,y,action,0};
 uint8_t *centers=buffer+512,*area=buffer+640;
 unsigned nc=((unsigned (*)(const void *,unsigned,unsigned,void *))0x080b4a1du)(&descriptor,0,0,centers);
 /* These three fixed range3/cross actions have at most25 centers and5 area
  * records. Retain native range, height, obstruction and map restrictions. */
 if(nc>32)nc=0;
 for(unsigned c=0;c<nc;c++){
  unsigned cx=centers[4*c],cy=centers[4*c+1];
  descriptor.x=descriptor.cx=(uint8_t)cx;descriptor.y=descriptor.cy=(uint8_t)cy;
  unsigned nt=((unsigned (*)(const void *,unsigned,unsigned,void *))0x080b4a1du)(&descriptor,0,1,area);
  if(nt>32)continue;
  int score=0;
  for(unsigned i=0;i<count;i++){
   const uint8_t *t=scratch->units[i];unsigned tx=t==a?x:t[0xf6],ty=t==a?y:t[0xf7],inside=0;
   for(unsigned k=0;k<nt;k++)if(area[4*k]==tx && area[4*k+1]==ty){inside=1;break;}
   if(action==FFTA_GEO_A4){if(inside)score+=scratch->benefit[i]*100;continue;}
   unsigned after=scratch->other[i],before=scratch->before[i];
   if(inside){
    score+=scratch->damage[i];
    if(action==FFTA_GEO_A7)after|=1;
    else if(!hostile(a,t))after|=2;
   }
   int benefit=0;
   if(scratch->ground[i]&1u)benefit-=6*((int)(after&1u)-(int)(before&1u));
   if(scratch->ground[i]&2u)benefit+=scratch->benefit[i]*((int)((after>>1)&1u)-(int)((before>>1)&1u));
   score+=benefit*100*(hostile(a,t)?(benefit>0?-2:-1):(benefit<0?2:1));
  }
  int best=*(int *)(node+0x1c);
  if(score>0 && (score>best || (score==best && distance(x,y,a[0xf6],a[0xf7])<
      distance(node[0x1ac],node[0x1ad],a[0xf6],a[0xf7])))){
   *(int *)(node+0x1c)=score;*(int *)(node+0x20)=1;sh(node+10,0);
   node[0x1ac]=(uint8_t)x;node[0x1ad]=(uint8_t)y;
   node[0x1ae]=(uint8_t)cx;node[0x1af]=(uint8_t)cy;node[0x1b0]=0;node[0x1b1]=1;
  }
 }
 ffta_ai_choice_end(&scope);return cursor<255;
}
