#include "geomancer-animation.h"
#define MAGIC 0x31414746u
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static unsigned word(const uint8_t *p){return *(const unsigned *)p;}
static unsigned valid(const void *p,unsigned bytes){
 uintptr_t n=(uintptr_t)p;return !(n&3u) && n>=0x02000000u && n<=0x0203f000u-bytes;
}
unsigned ffta_geo_animation_begin(FFTA_GeoAnimationSource *s,uint8_t *pool,unsigned tiles){
 if(!valid(s,sizeof(*s)) || !valid(pool,4+4*44) || !tiles || tiles>128)return 0;
 if(s->magic==MAGIC && s->self==(unsigned)s)return 0;
 if(half(pool)!=1024)return 0;
 volatile uint8_t *lock=(volatile uint8_t *)0x02009198u;
 unsigned prior_lock=*lock;*lock=1;
 /* Validate the complete set before redirecting any native destination. */
 unsigned count=0;
 for(unsigned i=0;i<4;i++){
  uint8_t *c=pool+4+44*i;if(!c[0] || c[1])continue;
  unsigned dest=word(c+20),current=word(c+28),length=half(c+8),progress=half(c+12);
  if(dest<0x06000000u || dest>=0x06005000u)continue;
  if(!length || c[4]==255 || !progress || (dest|length|half(c+10)|progress)&31u ||
     dest+length>0x06000000u+tiles*32u || progress>length ||
     current<dest || current>=dest+length ||
     word(c+16)<0x08000000u || word(c+16)>=0x0a000000u ||
     word(c+24)<0x08000000u || word(c+24)>=0x0a000000u){*lock=(uint8_t)prior_lock;return 0;}
  count++;
 }
 s->count=0;s->tiles=tiles;s->self=(unsigned)s;
 const volatile uint32_t *original=(const volatile uint32_t *)0x06000000u;
 for(unsigned i=0;i<tiles*8u;i++)((uint32_t *)s->graphics)[i]=original[i];
 for(unsigned i=0;i<4;i++){
  uint8_t *c=pool+4+44*i;unsigned dest=word(c+20);
  if(!c[0] || c[1] || dest<0x06000000u || dest>=0x06005000u)continue;
  FFTA_GeoAnimationBinding *b=&s->bindings[s->count++];
  b->controller=c;b->control=(const uint8_t *)word(c+16);b->source=(const uint8_t *)word(c+24);
  b->destination=dest;
  unsigned delta=(unsigned)s->graphics-0x06000000u;
  *(unsigned *)(c+20)=dest+delta;*(unsigned *)(c+28)=word(c+28)+delta;
 }
 s->magic=MAGIC;*lock=(uint8_t)prior_lock;return s->count==count;
}
void ffta_geo_animation_end(FFTA_GeoAnimationSource *s){
 if(!valid(s,sizeof(*s)) || s->magic!=MAGIC || s->self!=(unsigned)s || s->count>4 || s->tiles>128)return;
 volatile uint8_t *lock=(volatile uint8_t *)0x02009198u;
 unsigned prior_lock=*lock;*lock=1;
 for(unsigned i=0;i<s->count;i++){
  FFTA_GeoAnimationBinding *b=&s->bindings[i];uint8_t *c=b->controller;
  if(!valid(c,44) || word(c+16)!=(unsigned)b->control || word(c+24)!=(unsigned)b->source)continue;
  unsigned delta=(unsigned)s->graphics-0x06000000u,expected=b->destination+delta;
  unsigned current=word(c+28),length=half(c+8);
  if(word(c+20)!=expected || current<expected || current>=expected+length)continue;
  *(unsigned *)(c+20)=b->destination;*(unsigned *)(c+28)=current-delta;
 }
 s->magic=0;s->count=0;*lock=(uint8_t)prior_lock;
}
