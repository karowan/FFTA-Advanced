#include "registry.h"
#include "geomancer.h"
#include "ai-choice.h"

static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static void sh(uint8_t *p,int n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static unsigned hostile(const uint8_t *a,const uint8_t *t){
 return ((a[0x29]>>7)^((a[0xeb]>>5)&1u))!=(t[0x29]>>7);
}
unsigned ffta_geo_ai_utility(unsigned action){
 return action==FFTA_GEO_A4 || action==FFTA_GEO_A7 || action==FFTA_GEO_A9;
}

/* Signed recipient value, like native damage/status rows: benefits are
 * negative. These are planning weights, not changes to ability strength.
 * Native admission, probability, law flags and execution remain separate.
 * Coordinates may belong to an authenticated proposed movement endpoint. */
int ffta_geo_ai_utility_value(int native,const uint8_t *a,const uint8_t *t,unsigned action){
 if(!ffta_geo_ai_utility(action))return native;
 if(!a || !t || !half(a+0x18) || !half(t+0x18) ||
    (a[0xe8]&64u) || (t[0xe8]&64u) ||
    !((unsigned (*)(const uint8_t *,const uint8_t *,unsigned))0x080c48a5u)(a,t,action))return 0;
 int x=a[0xf6],y=a[0xf7];ffta_ai_position(a,&x,&y);
 int tx=t==a?x:t[0xf6],ty=t==a?y:t[0xf7];
 if(action==FFTA_GEO_A7){
  /* Rime harms allies too. Float/flight and Surefoot remove only the
   * terrain penalty, never its original elemental HP forecast. */
  if(ffta_geo_grounded(t) &&
     ((unsigned (*)(const uint8_t *))0x080cd50du)(t)!=FFTA_GEO_S2 &&
     !ffta_geo_field_at(t,tx,ty,1))native+=6;
  return native>32767?32767:native;
 }
 if(hostile(a,t))return 0;
 if(action==FFTA_GEO_A9){
  if(!ffta_geo_grounded(t) || ffta_geo_field_at(t,tx,ty,2))return 0;
  return -20;
 }
 /* Move+1 still helps an innate flyer and stacks with Light Foot/Surefoot.
  * Do not refresh a live Updraft or remove an ally's current Refuge benefit
  * just to add Float. The player remains free to make either tradeoff. */
 if(ffta_geo_updraft(t,0) ||
    (ffta_geo_grounded(t) && ffta_geo_field_at(t,tx,ty,2)))return 0;
 int value=-16;
 if(((unsigned (*)(unsigned,unsigned))0x0801cc7du)(x,y) &&
    ((unsigned (*)(unsigned,unsigned))0x0801cc7du)(tx,ty)){
  int height=((int (*)(unsigned,unsigned))0x0801cc19u)(x,y);
  int target_height=((int (*)(unsigned,unsigned))0x0801cc19u)(tx,ty);
  if(height-target_height>=2 && !ffta_geo_updraft(t,1))value-=4;
 }
 return value;
}

void ffta_geo_ai_utility_row(uint8_t *row,const uint8_t *a,const uint8_t *t,unsigned action){
 if(!ffta_geo_ai_utility(action) || !half(row+10))return;
 int value=ffta_geo_ai_utility_value((int16_t)half(row+12),a,t,action);
 if(!value){for(unsigned i=4;i<20;i++)row[i]=0;return;}
 if(action!=FFTA_GEO_A7){
  /* Forecast category only: native beneficial non-HP status, as for Mystic
   * preparations. Do not grant Protect or change the action descriptor. */
  sh(row+4,82);
 }
 sh(row+12,value);sh(row+14,value);
}
