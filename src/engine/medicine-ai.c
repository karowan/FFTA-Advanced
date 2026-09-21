#include "medicine-ai.h"
#include "chemist-items.h"
#include "chemist-state.h"
#include "registry.h"
#include "job-state.h"
#include "blade-wound.h"
#include "viking-state.h"
#include "geomancer.h"
#include "dancer.h"
#include "ai-choice.h"

static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static void sh(uint8_t *p,int n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static unsigned status(const uint8_t *u,unsigned n){return (u[0xe8+n/8]>>(n%8))&1u;}
static unsigned options(unsigned action,uint16_t *out){
 if(action==FFTA_CHM_A2){out[0]=367;out[1]=368;out[2]=369;out[3]=371;return 4;}
 if(action==FFTA_CHM_A4){out[0]=363;out[1]=364;return 2;}
 out[0]=0;return 1;
}
unsigned ffta_medicine_choice_valid(unsigned action,unsigned selected){
 uint16_t choices[4];unsigned count=options(action,choices);
 for(unsigned i=0;i<count;i++)if(choices[i]==selected)return 1;
 return 0;
}
unsigned ffta_medicine_available(const uint8_t *a,unsigned action){
 if(!a || !half(a+0x18) || (a[0xe8]&64u) || (a[0xeb]&16u))return 0;
 unsigned origin=ffta_job_origin(a);
 if(!origin || origin>24)return 0;
 uint16_t choices[4];unsigned count=options(action,choices);
 for(unsigned i=0;i<count;i++)if(ffta_chemist_stocked(action,choices[i]))return 1;
 return 0;
}
extern int ffta_integrated_item_healing(const uint8_t *);
extern void ffta_ai_original_row(uint8_t *,const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned);
extern unsigned ffta_medicine_original_recipient(const uint8_t *,const uint8_t *,unsigned);

/* C48A4 has no item argument: it normally substitutes the primary weapon.
 * For Field Remedy, test the exact stock-backed cure donor and our ownership/
 * faction policy. Without a forecast choice, admission asks whether ANY cure
 * can work; the later row selects one. All other actions use native admission.
 * This does not lend one target's chosen cure to another target. */
unsigned ffta_medicine_ai_recipient(const uint8_t *a,const uint8_t *t,unsigned action){
 if(action!=FFTA_CHM_A2)return ffta_medicine_original_recipient(a,t,action);
 if(!ffta_medicine_available(a,action) || !t)return 0;
 unsigned selected=ffta_ai_preview_choice(a,action);
 uint16_t choices[4];unsigned count=options(action,choices);
 for(unsigned i=0;i<count;i++){
  if(selected && choices[i]!=selected)continue;
  FFTA_ChemistRecipe recipe;
  if(!ffta_chemist_recipe(action,choices[i],&recipe) || !ffta_chemist_stocked(action,choices[i]))continue;
  /* Field Remedy eligibility reads only actor, target and the recipe pair;
   * unlike resurrection, it never reads the later native context flags. */
  uint32_t c[4]={(uintptr_t)a,(uintptr_t)t,(uintptr_t)t,action|((unsigned)choices[i]<<16)};
  if(ffta_chemist_eligibility((const uint8_t *)c) && ffta_medicine_original_recipient(a,t,recipe.donor))return 1;
 }
 return 0;
}

/* Small pure benefit calculation: never nest a second evaluated-unit battle
 * forecast inside native placement. Keep complete context flags for revival
 * admission; use the execution formulas for HP/MP and the same cure domain.
 * Negative values follow native recipient scoring. */
static __attribute__((noinline)) unsigned native_admission(const uint8_t *a,const uint8_t *t,unsigned action,unsigned selected){
 /* Native recipient admission reconstructs a context using the weapon.
  * Give that query this exact recipe, then retire the synchronous scope. */
 FFTA_AIChoiceScope scope;ffta_ai_choice_begin(&scope,a,action,selected,0);
 unsigned admitted=((unsigned (*)(const uint8_t *,const uint8_t *,unsigned))0x080c48a5u)(a,t,action);
 ffta_ai_choice_end(&scope);return admitted;
}
static __attribute__((noinline)) int benefit(const uint8_t *a,const uint8_t *t,unsigned action,unsigned selected){
 uint32_t words[13]={0};uint8_t *c=(uint8_t *)words;
 words[0]=(uintptr_t)a;words[1]=words[2]=(uintptr_t)t;words[3]=action|(selected<<16);c[0x26]=16u;
 if(!ffta_chemist_eligibility(c))return 0;
 unsigned benefit=0;
 if(action==FFTA_CHM_A1 || action==FFTA_CHM_A4 || action==FFTA_CHM_A5)
  benefit=2u*(unsigned)ffta_integrated_item_healing(c);
 else if(action==FFTA_CHM_A6)benefit=2u*(unsigned)ffta_chemist_mp(c);
 else if(action==FFTA_CHM_A3 || action==FFTA_CHM_A8)benefit=2u*(unsigned)ffta_chemist_revive(c);
 else if(action==FFTA_CHM_A2)benefit=40;
 else if(action==FFTA_CHM_A7){
  for(unsigned n=0;n<44;n++)if(status(t,n) && ffta_chemist_native_curable(n))benefit+=40;
  benefit+=40u*!!ffta_wound_record_remaining(ffta_owned_wound((uint8_t *)t));
  benefit+=40u*!!ffta_viking_challenger(t);
  benefit+=40u*!!ffta_geo_wisp(t);
  benefit+=40u*!!ffta_dancer_debuff(t,0);
  benefit+=40u*!!ffta_dancer_debuff(t,1);
 }else if(action==FFTA_CHM_A9)benefit=ffta_inoculated_active(t)?0:20;
 else if(action==FFTA_CHM_A10)benefit=20u*(!status(t,24)+!status(t,25));
 return -(int)(benefit>32767?32767:benefit);
}
int ffta_medicine_ai_value(const uint8_t *a,const uint8_t *t,unsigned action,unsigned selected){
 if(!ffta_medicine_available(a,action) || !t || !ffta_chemist_stocked(action,selected))return 0;
 /* These frames must not overlap: native admission has its own deep callers,
  * while the small benefit calculation needs a complete revival context. */
 return native_admission(a,t,action,selected)?benefit(a,t,action,selected):0;
}

void ffta_medicine_ai_row(uint8_t *row,const uint8_t *actor,const uint8_t *target,unsigned action,unsigned flags){
 const uint8_t *a=*(const uint8_t *const *)actor,*t=*(const uint8_t *const *)target;
 for(unsigned i=0;i<20;i++)row[i]=0;
 sh(row,action);
 if(!ffta_medicine_available(a,action))return;
 uint16_t choices[4];unsigned count=options(action,choices);int best=0;
 FFTA_AIChoiceScope scope;ffta_ai_choice_begin(&scope,a,action,0,0);
 for(unsigned i=0;i<count;i++){
  unsigned choice=choices[i];int value=ffta_medicine_ai_value(a,t,action,choice);
  if(value>=best)continue;
  uint8_t candidate[20]={0};scope.choice=choice;
  ffta_ai_original_row(candidate,actor,target,action,choice,flags);
  if(!half(candidate+10))continue;
  if(action==FFTA_CHM_A9){sh(candidate+4,82);sh(candidate+6,0);sh(candidate+10,1);}
  sh(candidate+12,value);sh(candidate+14,value);
  for(unsigned j=0;j<20;j++)row[j]=candidate[j];
  best=value;
 }
 ffta_ai_choice_end(&scope);
}

extern unsigned ffta_geo_original_search(uint8_t *,unsigned);
unsigned ffta_medicine_ai_search(uint8_t *node,unsigned flags){
 unsigned result=ffta_geo_original_search(node,flags),action=half(node+8);
 if(result || !node[0x1b1] || action==FFTA_CHM_A5)return result;
 const uint8_t *aw=*(const uint8_t *const *)node,*tw=*(const uint8_t *const *)(node+4);
 const uint8_t *a=aw?*(const uint8_t *const *)aw:0,*t=tw?*(const uint8_t *const *)tw:0;
 if(!a || !t || a==t)return result;
 /* Each native single-target node owns this particular beneficiary. With
  * Long Throw, its old base-range center list can publish the adjacent empty
  * tile even though native geometry admits the beneficiary itself. Commit
  * the actual target, only after the public range/height/LOS gate accepts it.
  * Mist keeps its genuine area center and all native placement scoring. */
 unsigned legal=((unsigned (*)(const uint8_t *,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned))0x080a0015u)
  (a,node[0x1ac],node[0x1ad],t[0xf6],t[0xf7],action,half(node+10),0);
 if(legal){node[0x1ae]=t[0xf6];node[0x1af]=t[0xf7];}
 else node[0x1b1]=0;
 return result;
}
