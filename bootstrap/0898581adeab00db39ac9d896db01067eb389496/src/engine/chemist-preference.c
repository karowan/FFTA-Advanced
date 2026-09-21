#include <stdint.h>
#include "chemist-preference-labels.h"
extern uint8_t *ffta_job_potion(uint8_t *);
extern unsigned ffta_original_potion_roster(unsigned,unsigned,uint8_t *);
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static unsigned lesson(const uint8_t *u){return u[6]==3?121:u[6]==5?100:0;}
static unsigned canonical(const uint8_t *u){
 uintptr_t d=(uintptr_t)u-0x02000080u;return d<24u*264u && d%264u==0;
}
/* This is the native Pick Abilities list, not the read-only AP browser.
 * Both entries retain the actual reaction lesson and its native help ID. */
unsigned ffta_potion_roster(unsigned type,unsigned race,uint8_t *menu){
 unsigned n=ffta_original_potion_roster(type,race,menu);
 uint8_t *ctx=*(uint8_t **)0x03002818u;
 if(type!=2 || !ctx || menu!=(uint8_t *)0x0203c000u || n>=24)return n;
 uint8_t *u=*(uint8_t **)(ctx+0x1d0c);
 if(!canonical(u) || !lesson(u))return n;
 uint8_t *rows=*(uint8_t **)(menu+0x18),*preference=ffta_job_potion(u);
 if(rows!=menu+0x230 || !preference)return n;
 for(unsigned i=0;i<n;i++)if(rows[20*i+14]==lesson(u)){
  for(unsigned j=n;j>i;j--)for(unsigned k=0;k<20;k++)rows[20*j+k]=rows[20*(j-1)+k];
  n++;
  for(unsigned j=0;j<n;j++){
   rows[20*j]=(uint8_t)j;rows[20*j+1]=0;
   ctx[0x1134+j]=rows[20*j+14];
  }
  unsigned selected=*preference==1;
  for(unsigned j=0;j<2;j++)
   *(const uint8_t **)(rows+20*(i+j)+8)=ffta_potion_preference_labels[j+(selected==j?2:0)];
  *(unsigned *)menu=n;ctx[0x1132]=(uint8_t)n;
  return n;
 }
 return n;
}
/* Called only from the native confirmed reaction-assignment branch. Native
 * cancellation never enters this function. Inspect the still-owned list's
 * selected row instead of inventing additional saved reaction IDs. */
void ffta_potion_confirm(uint8_t *ctx){
 uint8_t *u=*(uint8_t **)(ctx+0x1d0c);
 unsigned chosen=half(ctx+0x2cc8);
 u[0x3a]=(uint8_t)chosen;
 if(!canonical(u) || !lesson(u) || chosen!=lesson(u))return;
 uint8_t *menu=*(uint8_t **)(ctx+0x2d50);
 if(menu!=(uint8_t *)0x0203c000u)return;
 unsigned n=*(unsigned *)menu;
 uint8_t *rows=*(uint8_t **)(menu+0x18);
 if(n>24 || rows!=menu+0x230)return;
 int row=((int (*)(uint8_t *,int))0x08017b69u)(ctx+0x2d00,(int8_t)ctx[0x2d31]);
 if(row<0 || (unsigned)row>=n || rows[20*row+14]!=chosen)return;
 unsigned ordinal=0,total=0;
 for(unsigned j=0;j<n;j++)if(rows[20*j+14]==chosen){total++;if(j<(unsigned)row)ordinal++;}
 if(total!=2 || ordinal>1)return;
 uint8_t *p=ffta_job_potion(u);if(p)*p=(uint8_t)ordinal;
}
