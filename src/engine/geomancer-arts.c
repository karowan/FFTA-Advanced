#include "geomancer.h"
#include "registry.h"
#include "job-state.h"
#include "action-snapshot.h"
#include "curable-status.h"
#include "ai-choice.h"
#include "custom-laws.h"
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static unsigned alive(const uint8_t *u){return u && half(u+0x18) && !(u[0xe8]&64u);}
static unsigned timer(unsigned t){return (t&3u) && (t&3u)<=2;}
static unsigned own_turn(const uint8_t *u){const uint8_t *m=*(const uint8_t *const *)0x0200f438u;return m && *(const uint8_t *const *)(m+24)==u;}
static unsigned hostile(const uint8_t *a,const uint8_t *t){return a && t && a!=t && (((a[0x29]>>7)^((a[0xeb]>>5)&1u))!=(t[0x29]>>7));}
/* Material annotations are immutable ROM content, indexed by the native map
 * identity and coordinates. Unannotated cells remain neutral. Native water is
 * independently recognized, including inaccessible neighboring water. */
unsigned ffta_geo_affinity(const uint8_t *u){
 if(!u)return 0;
 int x=u[0xf6],y=u[0xf7];
 /* Move updates the active wrapper before A433C synchronizes the unit.
  * Menu/forecast queries must see that displayed position without writing
  * unit or AP state. Exact pointer ownership excludes copied AI candidates;
  * they retain the coordinates supplied by their native simulation. */
 const uint8_t *m=*(const uint8_t *const *)0x0200f438u;
 const uint8_t *w=*(const uint8_t *const *)0x0200f4ecu;
 if(!ffta_ai_position(u,&x,&y) && m && m[4]>=6 && m[4]<=11 && *(const uint8_t *const *)(m+24)==u &&
    w && *(const uint8_t *const *)w==u){x=(int)(half(w+8)>>5);y=(int)(half(w+12)>>5);}
 if(x>=16 || y>=16)return 0;
 if(!((unsigned (*)(unsigned,unsigned))0x0801cc7du)(x,y))return 0;
 unsigned map=*(const uint16_t *)0x02007f10u,mask=0;
 int h=((int (*)(unsigned,unsigned))0x0801cc19u)(x,y);
 static const int8_t delta[5][2]={{0,0},{1,0},{-1,0},{0,1},{0,-1}};
 for(unsigned i=0;i<5;i++){
  int nx=x+delta[i][0],ny=y+delta[i][1];
  if(nx<0||nx>=16||ny<0||ny>=16||!((unsigned (*)(unsigned,unsigned))0x0801cc7du)(nx,ny))continue;
  int difference=((int (*)(unsigned,unsigned))0x0801cc19u)(nx,ny)-h;
  if(difference < -2 || difference > 2)continue;
  if(((unsigned (*)(unsigned,unsigned))0x0801cd09u)(nx,ny)&2u)mask|=FFTA_GEO_WATER;
  if(map<163)mask|=((const uint8_t *)0x091f0000u)[map*256u+16u*(unsigned)ny+(unsigned)nx]&31u;
 }
 return mask;
}
unsigned ffta_geo_wisp(const uint8_t *u){
 const uint8_t *s=ffta_job_state((uint8_t *)u);
 return alive(u) && s && timer(s[FFTA_JOB_GEO_FIELD_FLAGS]>>5)?1u+(s[FFTA_JOB_GEO_TRAVERSAL]&1u):0;
}
unsigned ffta_geo_steady(const uint8_t *u){
 const uint8_t *s=ffta_job_state((uint8_t *)u);
 return alive(u) && s && timer(s[FFTA_JOB_GEO_STEADY]&7u);
}
void ffta_geo_wisp_hp_loss(uint8_t *u,unsigned before,unsigned after){
 if(before<=after || !alive(u) || ffta_action_id()!=FFTA_GEO_A6 ||
    ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY || !hostile(ffta_action_actor(),u))return;
 const uint8_t *c=(const uint8_t *)0x0200f3f0u;
 uint8_t *s=ffta_job_state(u);if(!s)return;
 unsigned strong=!!(ffta_geo_affinity(ffta_action_actor())&FFTA_GEO_HEAT);
 if(ffta_geo_wisp(u)==2 && !strong)return;
 if(((unsigned (*)(const uint8_t *))0x080cd50du)(u)==11 ||
    ffta_chemist_prevent_custom(c,FFTA_CURABLE_WISP_EXPOSURE))return;
 s[FFTA_JOB_GEO_FIELD_FLAGS]=(uint8_t)((s[FFTA_JOB_GEO_FIELD_FLAGS]&31u)|((2u|(own_turn(u)?4u:0u))<<5));
 s[FFTA_JOB_GEO_TRAVERSAL]=(uint8_t)((s[FFTA_JOB_GEO_TRAVERSAL]&254u)|strong);
 ffta_custom_law_applied(u);
}
extern uint8_t *ffta_bard_original_application(uint8_t *,unsigned);
uint8_t *ffta_geo_ward_apply(uint8_t *c){
 /* Ordinary Protect keeps its native status/immunity/timer consumer. */
 const uint8_t *a=*(const uint8_t *const *)c;uint8_t *u=*(uint8_t **)(c+8);
 if(!alive(a)||!alive(u)||hostile(a,u))return c;
 /* The relocated table contains the change observer, which dispatches by
  * this context's descriptor110. Re-entering it would recurse into Ward.
  * Use the preserved original native callback behind the observer. */
 ffta_bard_original_application(c,82);
 uint8_t *s=ffta_job_state(u);unsigned origin=ffta_job_origin(u);
 if(!s || !(ffta_geo_affinity(a)&FFTA_GEO_ROCK) || !origin)return c;
 uintptr_t live=origin<=24?0x02000080u+(origin-1)*264u:0x02002fc4u+(origin-25)*264u;
 if((c[0x26]&16u) && (uintptr_t)u==live)return c;
 unsigned own=origin==ffta_job_origin(a);
 s[FFTA_JOB_GEO_STEADY]=(uint8_t)((s[FFTA_JOB_GEO_STEADY]&248u)|2u|(own?4u:0u));
 return c;
}
unsigned ffta_geo_rider(const uint8_t *c){
 if(!c)return 0;
 unsigned id=half(c+12);const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+8);
 if(!a||!t)return 0;
 if(id==FFTA_GEO_A7 && !(ffta_geo_affinity(a)&FFTA_GEO_ICE))return 0;
 if(id==FFTA_GEO_A3 && !(ffta_geo_affinity(a)&FFTA_GEO_WATER))return 0;
 if(!(c[0x26]&16u) && ffta_action_phase()==FFTA_ACTION_RESULT && ffta_action_id()==id)
  return ffta_action_hp_lost(t)>0;
 /* Prediction uses the original damage descriptor and restores native scratch
  * and RNG. It cannot grant a rider from a status-only or absorbed result. */
 uint8_t copy[0x34],saved[0x34];volatile uint8_t *scratch=(volatile uint8_t *)0x0200f3f0u;
 for(unsigned i=0;i<sizeof(copy);i++){copy[i]=c[i];saved[i]=scratch[i];}
 const uint8_t *d=*(const uint8_t *const *)0x0812f2a0u;
 *(const uint8_t **)(copy+0x30)=d+63u*4u;copy[0x28]=0;copy[0x26]|=16u;
 volatile uint32_t *rng=(volatile uint32_t *)0x030034b0u;unsigned old=*rng;
 int n=((int (*)(const uint8_t *))0x0813189du)(copy);
 const uint8_t *original=*(const uint8_t *const *)(c+4);
 if(n>0 && original && ((unsigned (*)(const uint8_t *))0x0812e6a5u)(original)==13 &&
    ((unsigned (*)(const uint8_t *,const uint8_t *,unsigned,unsigned))0x0812e6e1u)(a,original,id,13))n=0;
 *rng=old;for(unsigned i=0;i<sizeof(copy);i++)scratch[i]=saved[i];
 return n>0;
}
unsigned ffta_geo_choices(const uint8_t *u,unsigned action,uint8_t *out){
 if(action==FFTA_GEO_A3){for(unsigned i=0;i<4;i++)out[i]=(uint8_t)(i+1);return 4;}
 if(action!=FFTA_GEO_A8)return 0;
 unsigned a=ffta_geo_affinity(u),n=0;out[n++]=2; /* Wind is always available. */
 if(a&FFTA_GEO_ROCK)out[n++]=3;
 if(a&FFTA_GEO_WATER)out[n++]=4;
 if(a&FFTA_GEO_HEAT)out[n++]=1;
 if(a&FFTA_GEO_ICE)out[n++]=5;
 return n;
}
unsigned ffta_geo_element(const uint8_t *u,unsigned action,unsigned choice){
 (void)action;if(!choice || choice==2)return 2;
 uint8_t elements[5];unsigned n=ffta_geo_choices(u,FFTA_GEO_A8,elements);
 for(unsigned i=0;i<n;i++)if(elements[i]==choice)return choice;
 return 0;
}
extern unsigned ffta_sea_legs(const uint8_t *);
unsigned ffta_geo_push_destination(const uint8_t *original,unsigned choice,uint8_t *x,uint8_t *y){
 if(!alive(original)||choice<1||choice>4||ffta_sea_legs(original)||ffta_geo_steady(original))return 0;
 static const int8_t direction[4][2]={{0,-1},{1,0},{0,1},{-1,0}};
 uint8_t origin[248]={0};
 /* The native displacement routine wraps its coordinate delta to signed8. */
 origin[0xf6]=(uint8_t)(original[0xf6]-direction[choice-1][0]);
 origin[0xf7]=(uint8_t)(original[0xf7]-direction[choice-1][1]);
 uint8_t *manager=((uint8_t *(*)(void))0x08096d7du)();
 uint8_t *wrapper=((uint8_t *(*)(uint8_t *,const uint8_t *))0x08099561u)(manager,original);
 uint8_t *companion=wrapper?*(uint8_t **)(wrapper+4):0;
 return ((unsigned (*)(uint8_t *,const uint8_t *,const uint8_t *,uint8_t *,uint8_t *,uint8_t *))0x08098e7du)
     (manager,origin,original,companion,x,y);
}
uint8_t *ffta_geo_torrent_apply(uint8_t *c){
 const uint8_t *a=*(const uint8_t *const *)c,*original=*(const uint8_t *const *)(c+4);
 uint8_t *target=*(uint8_t **)(c+8);unsigned choice=half(c+14);
 if(!alive(target)||!original||!a||choice<1||choice>4||!ffta_geo_rider(c)||
    ffta_sea_legs(original)||ffta_geo_steady(original))return c;
 unsigned token=ffta_job_origin(target);
 uintptr_t live=token<=24?0x02000080u+(token-1)*264u:0x02002fc4u+(token-25)*264u;
 if(!token || ((c[0x26]&16u) && (uintptr_t)target==live))return c;
 uint8_t x=0,y=0;
 if(ffta_geo_push_destination(original,choice,&x,&y)){
  c[0x26]|=8u;target[0xf6]=x;target[0xf7]=y;
 }
 return c;
}
