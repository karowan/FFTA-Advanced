#include "geomancer.h"
#include "registry.h"
#include "job-state.h"
#include "action-snapshot.h"
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static unsigned alive(const uint8_t *u){return u && half(u+0x18) && !(u[0xe8]&64u);}
static unsigned valid_timer(unsigned t){return (t&3u) && (t&3u)<=2;}
static unsigned tick(unsigned t){return (t&3u)>2?0:(t&4u)?t&3u:t?t-1:0;}
static unsigned absolute(int v){return (unsigned)(v<0?-v:v);}
static unsigned hostile(const uint8_t *a,const uint8_t *t){return ((a[0x29]>>7)^((a[0xeb]>>5)&1u))!=(t[0x29]>>7);}
static unsigned tile(int x,int y){return x>=0 && x<16 && y>=0 && y<16 && ((unsigned (*)(unsigned,unsigned))0x0801cc7du)(x,y);}
unsigned ffta_geo_updraft(const uint8_t *u,unsigned jump){
 const uint8_t *s=ffta_job_state((uint8_t *)u);
 return alive(u) && s && valid_timer((s[FFTA_JOB_GEO_TRAVERSAL]>>(jump?4:1))&7u);
}
unsigned ffta_geo_field_kind(const uint8_t *u){
 const uint8_t *s=ffta_job_state((uint8_t *)u);
 if(!alive(u)||!s||!valid_timer((s[FFTA_JOB_GEO_FIELD_FLAGS]>>2)&7u))return 0;
 unsigned kind=s[FFTA_JOB_GEO_FIELD_FLAGS]&3u;
 return kind<=2 && tile(s[FFTA_JOB_GEO_FIELD_X],s[FFTA_JOB_GEO_FIELD_Y])?kind:0;
}
unsigned ffta_geo_grounded(const uint8_t *u){
 /* Updraft's tagged Float is independent of innate/equipped flight. It
  * does not grant flight's unrestricted height or occupied-tile traversal. */
 return u && !ffta_geo_updraft(u,0) && u[0xfc]!=2 && u[0xfc]!=3 && u[0xfd]!=5;
}
unsigned ffta_geo_field_at(const uint8_t *u,int x,int y,unsigned kind){
 if(!u || !tile(x,y) || (kind!=1 && kind!=2))return 0;
 uint8_t *peers[FFTA_JOB_UNIT_COUNT];
 unsigned count=ffta_job_peers((uint8_t *)u,peers,FFTA_JOB_UNIT_COUNT);
 /* The peer API returns the complete canonical cohort in slot order.
  * Its live records are contiguous. Resolve that bank once; simulated
  * cohorts keep their own per-peer lookup and never fall back to it. */
 const uint8_t *live=count==FFTA_JOB_UNIT_COUNT && peers[0]==(uint8_t *)0x02000080u &&
  peers[24]==(uint8_t *)0x02002fc4u?ffta_job_state(peers[0]):0;
 for(unsigned i=0;i<count;i++){
  const uint8_t *caster=peers[i],*s=live?live+i*FFTA_JOB_RECORD_BYTES:ffta_job_state(peers[i]);
  if(!s || (s[FFTA_JOB_GEO_FIELD_FLAGS]&3u)!=kind || !valid_timer((s[FFTA_JOB_GEO_FIELD_FLAGS]>>2)&7u) ||
     !alive(caster) || (kind==2 && hostile(caster,u)))continue;
  int cx=s[FFTA_JOB_GEO_FIELD_X],cy=s[FFTA_JOB_GEO_FIELD_Y];
  if(absolute(x-cx)+absolute(y-cy)>1 || !tile(cx,cy))continue;
  int h=((int (*)(unsigned,unsigned))0x0801cc19u)(x,y);
  int ch=((int (*)(unsigned,unsigned))0x0801cc19u)(cx,cy);
  if(absolute(h-ch)<=2)return 1;
 }
 return 0;
}
unsigned ffta_geo_refuge(const uint8_t *u){return alive(u) && ffta_geo_grounded(u) && ffta_geo_field_at(u,u[0xf6],u[0xf7],2);}
unsigned ffta_geo_field_eligibility(const uint8_t *c){
 if(!c)return 0;
 const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+4);
 unsigned id=half(c+12);
 if(!alive(a)||!alive(t)||(a[0xeb]&16u))return 0;
 if(id==FFTA_GEO_A8 && !ffta_geo_element(a,id,half(c+14)))return 0;
 if(id==FFTA_GEO_A4 || id==FFTA_GEO_A5)return !hostile(a,t);
 if(id==FFTA_GEO_A2 || id==FFTA_GEO_A6)return hostile(a,t) && (!c[0x28] || ffta_geo_rider(c));
 if(id==FFTA_GEO_A1 || id==FFTA_GEO_A3 || id==FFTA_GEO_A7 || id==FFTA_GEO_A8)return a!=t && (!c[0x28] || ffta_geo_rider(c));
 return id==FFTA_GEO_A9;
}
uint8_t *ffta_geo_updraft_apply(uint8_t *c){
 if(!ffta_geo_field_eligibility(c)||half(c+12)!=FFTA_GEO_A4)return c;
 const uint8_t *a=*(const uint8_t *const *)c;uint8_t *u=*(uint8_t **)(c+8),*s=ffta_job_state(u);
 unsigned origin=ffta_job_origin(u);if(!alive(u)||!s||!origin)return c;
 uintptr_t live=origin<=24?0x02000080u+(origin-1)*264u:0x02002fc4u+(origin-25)*264u;
 if((c[0x26]&16u) && (uintptr_t)u==live)return c;
 unsigned timer=2u|(origin==ffta_job_origin(a)?4u:0u),v=s[FFTA_JOB_GEO_TRAVERSAL];
 v=(v&~14u)|(timer<<1);
 if(tile(a[0xf6],a[0xf7]) && tile(u[0xf6],u[0xf7])){
  int ah=((int (*)(unsigned,unsigned))0x0801cc19u)(a[0xf6],a[0xf7]);
  int uh=((int (*)(unsigned,unsigned))0x0801cc19u)(u[0xf6],u[0xf7]);
  if(ah-uh>=2)v=(v&~112u)|(timer<<4);
 }
 s[FFTA_JOB_GEO_TRAVERSAL]=(uint8_t)v;
 /* Update the native cached traversal fields without changing position. */
 ffta_geo_mobility(u);return c;
}
void ffta_geo_field_action(const uint8_t *u,unsigned action,unsigned event){
 if(event!=2 || (action!=FFTA_GEO_A7 && action!=FFTA_GEO_A9) ||
    ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY || !ffta_action_paid_count() || !alive(u))return;
 const uint8_t *object=ffta_action_result_object();uint8_t *s=ffta_job_state((uint8_t *)u);
 if(!object || !s || half(object+16)!=action || !tile(object[10],object[11]))return;
 /* Native result completion occurs even when its cross has no recipients
  * or every accuracy roll misses. The chosen center belongs to this object. */
 s[FFTA_JOB_GEO_FIELD_X]=object[10];s[FFTA_JOB_GEO_FIELD_Y]=object[11];
 s[FFTA_JOB_GEO_FIELD_FLAGS]=(uint8_t)((s[FFTA_JOB_GEO_FIELD_FLAGS]&224u)|24u|(action==FFTA_GEO_A7?1u:2u));
}
void ffta_geo_event(uint8_t *u,unsigned event){
 uint8_t *s=ffta_job_state(u);if(!s)return;
 unsigned jump=valid_timer((s[FFTA_JOB_GEO_TRAVERSAL]>>4)&7u);
 if(event>=2 && event<=5){
  s[FFTA_JOB_GEO_FIELD_X]=s[FFTA_JOB_GEO_FIELD_Y]=s[FFTA_JOB_GEO_FIELD_FLAGS]=s[FFTA_JOB_GEO_TRAVERSAL]=0;
  s[FFTA_JOB_GEO_STEADY]&=248u;
 }else if(event==6){
  s[FFTA_JOB_GEO_FIELD_FLAGS]&=31u;s[FFTA_JOB_GEO_TRAVERSAL]&=254u;
 }else if(event==7){
  /* Dispel removes recipient buffs; the caster's placed field is not one. */
  s[FFTA_JOB_GEO_TRAVERSAL]&=129u;s[FFTA_JOB_GEO_STEADY]&=248u;
 }
 if(jump && !valid_timer((s[FFTA_JOB_GEO_TRAVERSAL]>>4)&7u))ffta_geo_mobility(u);
}
void ffta_geo_turn_end(uint8_t *u){
 uint8_t *s=ffta_job_state(u);if(!s)return;
 unsigned field=s[FFTA_JOB_GEO_FIELD_FLAGS],traversal=s[FFTA_JOB_GEO_TRAVERSAL];
 unsigned duration=tick((field>>2)&7u);
 s[FFTA_JOB_GEO_FIELD_FLAGS]=(uint8_t)((tick(field>>5)<<5)|(duration<<2)|(duration?(field&3u):0));
 if(!duration)s[FFTA_JOB_GEO_FIELD_X]=s[FFTA_JOB_GEO_FIELD_Y]=0;
 s[FFTA_JOB_GEO_TRAVERSAL]=(uint8_t)((traversal&129u)|(tick((traversal>>1)&7u)<<1)|(tick((traversal>>4)&7u)<<4));
 s[FFTA_JOB_GEO_STEADY]=(uint8_t)((s[FFTA_JOB_GEO_STEADY]&248u)|tick(s[FFTA_JOB_GEO_STEADY]&7u));
 if(valid_timer((traversal>>4)&7u) && !valid_timer((s[FFTA_JOB_GEO_TRAVERSAL]>>4)&7u))ffta_geo_mobility(u);
}
extern int ffta_move_with_support(const uint8_t *);
int ffta_geo_move(const uint8_t *u){
 int n=ffta_move_with_support(u);return ffta_geo_updraft(u,0) && n<127?n+1:n;
}
