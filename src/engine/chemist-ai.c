#include "chemist-progression.h"
#include "job-state.h"
#include "mystic-knight.h"

static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static void sh(uint8_t *p,unsigned v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
static unsigned distance(unsigned x,unsigned y,unsigned a,unsigned b){
 return (x>a?x-a:a-x)+(y>b?y-b:b-y);
}
/* One candidate origin per native scheduler callback. The node's original
 * 1024-byte scratch allocation owns peer and center lists. This is a modest
 * visible-trap policy, not a simulation of future enemy decisions: prefer
 * an empty approach tile adjacent to an enemy, and do not refresh a live
 * trap. Native command, MP, law, movement and range admission remain in force. */
unsigned ffta_cp_ai_trap_search(uint8_t *node,unsigned flags){
 (void)flags;
 const uint8_t *w=*(const uint8_t *const *)node,*a=w?*(const uint8_t *const *)w:0;
 uint8_t *buffer=*(uint8_t **)(node+0x204);unsigned cursor=half(node+0x1b8);
 if(!a || !buffer || cursor>=256)return 0;
 if(!cursor){
  node[0x1b1]=0;*(int *)(node+0x1c)=0;
  if(!((unsigned (*)(uint8_t *))0x080bdf9du)(node) ||
     !ffta_myk_usable((uint8_t *)a,456,128u) || !ffta_cp_ai_value(0,a,a,456))return 0;
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
 uint8_t **peers=(uint8_t **)buffer,*centers=buffer+512;
 unsigned np=ffta_job_peers((uint8_t *)a,peers,36);
 struct {const uint8_t *actor;uint8_t x,y,cx,cy;uint16_t action,extra;} d={a,x,y,x,y,456,0};
 unsigned nc=((unsigned (*)(const void *,unsigned,unsigned,void *))0x080b4a1du)(&d,0,0,centers);
 if(nc>32)return cursor<255;
 for(unsigned c=0;c<nc;c++){
  unsigned cx=centers[c*4],cy=centers[c*4+1],score=0;
  if((cx==x && cy==y) || !ffta_cp_empty_tile(a,cx,cy))continue;
  for(unsigned i=0;i<np;i++){
   const uint8_t *t=peers[i];
   if(!half(t+0x18) || (t[0xe8]&64u) ||
      (((a[0x29]>>7)^((a[0xeb]>>5)&1u))==(t[0x29]>>7)))continue;
   if(distance(cx,cy,t[0xf6],t[0xf7])==1 &&
      distance(x,y,cx,cy)<distance(x,y,t[0xf6],t[0xf7]))score+=800;
  }
  unsigned best=*(unsigned *)(node+0x1c);
  if(score && (score>best || (score==best && distance(x,y,a[0xf6],a[0xf7])<
      distance(node[0x1ac],node[0x1ad],a[0xf6],a[0xf7])))){
   *(unsigned *)(node+0x1c)=score;*(unsigned *)(node+0x20)=1;sh(node+10,0);
   node[0x1ac]=(uint8_t)x;node[0x1ad]=(uint8_t)y;
   node[0x1ae]=(uint8_t)cx;node[0x1af]=(uint8_t)cy;node[0x1b0]=0;node[0x1b1]=1;
  }
 }
 return cursor<255;
}
