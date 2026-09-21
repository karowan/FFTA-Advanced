#include <stdint.h>
#include "registry.h"
#include "geomancer.h"
#include "ai-choice.h"
#include "mystic-knight.h"
#include "bard.h"
#include "dancer.h"
#include "dark-knight-state.h"
#include "viking-state.h"
#include "medicine-ai.h"
#include "chemist-items.h"

/* A synchronous forecast owns this stack token. It is never a saved option,
 * a unit identity guess, or a choice left over from a previous AI turn. */
typedef FFTA_AIChoiceScope ChoiceScope;
#define ROOT ((ChoiceScope *volatile *)0x0203f728u)
#define MAGIC 0x41494348u
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static unsigned supported(unsigned action){return action==FFTA_CHM_A2 || action==FFTA_CHM_A4 || action==FFTA_DNC_A6 || action==FFTA_GEO_A3 || action==FFTA_GEO_A8 || action==FFTA_MYK_A12;}
static unsigned valid(unsigned action,unsigned choice){return ffta_chemist_action(action)?ffta_medicine_choice_valid(action,choice):choice>=1 && choice<=(action==FFTA_MYK_A12?FFTA_MYK_DISPEL_CHOICES:action==FFTA_GEO_A8?5u:4u);}
void ffta_ai_choice_begin(ChoiceScope *s,const uint8_t *actor,unsigned action,unsigned choice,unsigned position){
 s->magic=MAGIC;s->self=s;s->actor=actor;s->action=action;s->choice=choice;s->position=position;s->previous=*ROOT;*ROOT=s;
}
void ffta_ai_choice_end(ChoiceScope *s){s->magic=0;*ROOT=s->previous;}
static const ChoiceScope *active(const uint8_t *actor){
 register uintptr_t stack __asm__("sp");const ChoiceScope *s=*ROOT;uintptr_t p=(uintptr_t)s;
 return !(p&3u) && p>=stack && p>=0x03000000u && p<=0x03008000u-sizeof(*s) &&
  s->magic==MAGIC && s->self==s && s->actor==actor?s:0;
}
static unsigned published(const uint8_t *actor,unsigned action){
    const uint8_t *ai=(const uint8_t *)0x020101f8u,*node=ai+0x5290;
    const uint8_t *wrapper=*(const uint8_t *const *)0x0200f4ecu;
    unsigned choice=half(node+10);
    /* Native mode8 is a completed decision. Actual AI selection and movement
     * outlive the synchronous score call; validate the published decision at
     * that boundary, without lending it to a player-controlled turn. */
    return actor && (actor[0x29]&128u) && wrapper &&
        *(const uint8_t *const *)wrapper==actor &&
        *(const uint8_t *const *)node==wrapper && half(ai+0x54f4)==8 &&
        node[0x1b1]==1 && half(node+8)==action && half(ai+0x54be)==action &&
        half(ai+0x54c0)==choice && valid(action,choice)?choice:0;
}
unsigned ffta_ai_preview_choice(const uint8_t *actor,unsigned action){
    if(!supported(action))return 0;
    const ChoiceScope *s=active(actor);
    if(s && s->action==action && valid(action,s->choice))return s->choice;
    return published(actor,action);
}
unsigned ffta_ai_position(const uint8_t *actor,int *x,int *y){
 const ChoiceScope *s=active(actor);
 if(s && (s->position&0x10000u)){*x=s->position&255u;*y=(s->position>>8)&255u;return 1;}
 const uint8_t *node=(const uint8_t *)0x02015488u;unsigned action=half(node+8);
 if((action==FFTA_GEO_A3 || action==FFTA_GEO_A8) && published(actor,action)){
  /* Planning publishes before movement. Forecasts for that committed cast
   * must already use its chosen endpoint, not the wrapper's departure tile. */
  *x=node[0x1ac];*y=node[0x1ad];return *x<16 && *y<16;
 }
 return 0;
}
extern void ffta_ai_original_row(uint8_t *,const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned);
extern int ffta_ai_original_score(const uint8_t *,const uint8_t *,unsigned,unsigned);

static unsigned martial_utility(unsigned action){
 return action==FFTA_SAM_A4 || action==FFTA_SAM_A5 || action==FFTA_DRK_A4 ||
  action==FFTA_DRK_A9 || action==FFTA_VIK_A4 || action==FFTA_DRK_A5;
}
extern int ffta_integrated_technique_healing(const uint8_t *);
extern unsigned ffta_primary_weapon(const uint8_t *);
extern unsigned ffta_integrated_weapon_valid(unsigned,unsigned);
static unsigned has_status(const uint8_t *u,unsigned bit){return (u[0xe8+bit/8]>>(bit%8))&1u;}
/* Marginal planning weights, after native admission. Reuse the small healing
 * formula rather than nesting another full evaluated-unit forecast on IWRAM.
 * Last Resort's hostile strike retains its native damage/hit contribution. */
static int martial_value(int native,const uint8_t *a,const uint8_t *t,unsigned action){
 if(!martial_utility(action))return native;
 if(!native || !a || !t || !half(a+0x18) || !half(t+0x18) ||
    (a[0xe8]&64u) || (t[0xe8]&64u))return 0;
 if(action==FFTA_DRK_A5 && a!=t){
  if(((a[0x29]>>7)^((a[0xeb]>>5)&1u))==(t[0x29]>>7))return 0;
  /* The native area scorer can retain the actor-buff stage after rejecting
   * the hostile strike. Keep its weapon gate equal to the recipient row;
   * an unarmed/Healer user can still choose the separate self mode. */
  if(!ffta_integrated_weapon_valid(action,ffta_primary_weapon(a)))return 0;
  return native+(ffta_drk_last_resort(a)?0:20);
 }
 int benefit=0;
 if(action==FFTA_SAM_A4 || action==FFTA_DRK_A4){
  uintptr_t c[4]={(uintptr_t)a,(uintptr_t)t,(uintptr_t)t,action};
  benefit=2*ffta_integrated_technique_healing((const uint8_t *)c);
 }
 if(action==FFTA_SAM_A5)benefit+=has_status(t,25)?0:20;
 if(action==FFTA_SAM_A5 || action==FFTA_DRK_A4)benefit+=has_status(t,24)?0:20;
 if(action==FFTA_DRK_A5)benefit+=ffta_drk_last_resort(a)?0:20;
 if(action==FFTA_DRK_A9)benefit+=ffta_drk_tbn(t)?0:20;
 if(action==FFTA_VIK_A4){
  benefit+=ffta_viking_war_cry(t)?0:20;
  static const uint8_t cures[3]={10,27,28};
  for(unsigned i=0;i<3;i++)if(has_status(t,cures[i]))benefit+=20;
 }
 return -benefit;
}
static void martial_row(uint8_t *row,const uint8_t *a,const uint8_t *t,unsigned action){
 if(!martial_utility(action))return;
 int native=(int16_t)half(row+12);
 /* Native C24C6 subtracts the Sure(100) status stage from its recipient's
  * row. Last Resort grants that stage to the ACTOR after its strike. Remove
  * the false enemy benefit; the ordinary area scorer never subtracts it.
  * Tests compare against the same native row with only this stage omitted. */
 if(action==FFTA_DRK_A5 && a!=t && half(row+10) &&
    (half(row+4)==97 || half(row+6)==97))native+=100;
 int value=half(row+10)?martial_value(native,a,t,action):0;
 if(!value){for(unsigned i=4;i<20;i++)row[i]=0;return;}
 /* Native's later candidate filter knows only its original application kinds.
  * Describe these pure custom buffs as one beneficial status in the AI row.
  * Self Last Resort has no strike; leaving its second custom97 kind/count
  * here causes the filter to reject it even after fixing the signed value.
  * Native execution still receives the original action/descriptors. */
 if(action==FFTA_DRK_A9 || action==FFTA_VIK_A4 || (action==FFTA_DRK_A5 && a==t)){
  row[4]=82;row[5]=row[6]=row[7]=0;row[10]=1;row[11]=0;
 }
 row[12]=(uint8_t)value;row[13]=(uint8_t)(value>>8);
 row[14]=row[12];row[15]=row[13];
}
static unsigned repeated_challenge(const uint8_t *a,const uint8_t *t,unsigned action){
 if(action!=FFTA_VIK_A9)return 0;
 unsigned source=ffta_job_origin(a);
 return source && ffta_viking_challenger(t)==source;
}
/* Called after native common restrictions and its ordinary row willingness.
 * A custom ward is useful according to its own state, not the recipient's
 * native Protect bit or Protect's extra10% self/50% ally random heuristic.
 * Preserve that native policy for original statuses and all other commands. */
unsigned ffta_martial_ai_custom_benefit(const uint8_t *row,const uint8_t *a,const uint8_t *t){
 unsigned action=half(row);
 if(action==FFTA_CHM_A9)return half(row+10) && ffta_medicine_ai_value(a,t,action,half(row+2))<0;
 if(action!=FFTA_DRK_A9 && action!=FFTA_VIK_A4 && !(action==FFTA_DRK_A5 && a==t))return 0;
 return half(row+10) && (int16_t)half(row+12)<0 && martial_value(-1,a,t,action)<0;
}

void ffta_ai_choice_row(uint8_t *row,const uint8_t *actor,const uint8_t *target,
                        unsigned action,unsigned extra,unsigned flags){
    if(ffta_chemist_action((uint16_t)action)){ffta_medicine_ai_row(row,actor,target,(uint16_t)action,flags);return;}
    if((uint16_t)action==FFTA_MYK_A12){ffta_myk_ai_spellbreak_row(row,actor,target,flags);return;}
    if(!supported((uint16_t)action)){
        ffta_ai_original_row(row,actor,target,action,extra,flags);
        ffta_geo_ai_utility_row(row,*(const uint8_t *const *)actor,
            *(const uint8_t *const *)target,(uint16_t)action);
        ffta_bard_ai_row(row,*(const uint8_t *const *)actor,
            *(const uint8_t *const *)target,(uint16_t)action);
        martial_row(row,*(const uint8_t *const *)actor,
            *(const uint8_t *const *)target,(uint16_t)action);
        if(ffta_dancer_ai_redundant(*(const uint8_t *const *)target,(uint16_t)action) ||
           repeated_challenge(*(const uint8_t *const *)actor,*(const uint8_t *const *)target,(uint16_t)action))
            for(unsigned i=4;i<20;i++)row[i]=0;
        if(action>=FFTA_MYK_A1 && action<=FFTA_MYK_A11 &&
           *(const uint8_t *const *)actor==*(const uint8_t *const *)target)
            ffta_myk_ai_self_row(row,*(const uint8_t *const *)actor);
        if(action>=FFTA_MYK_A1 && action<=FFTA_MYK_A14 && half(row+10)){
            int value=action==FFTA_MYK_A14?ffta_myk_ai_break_value(*(const uint8_t *const *)actor,*(const uint8_t *const *)target):
                ffta_myk_ai_strike_value((int16_t)half(row+12),*(const uint8_t *const *)actor,*(const uint8_t *const *)target,action);
            row[12]=(uint8_t)value;row[13]=(uint8_t)(value>>8);
            if(action==FFTA_MYK_A14 && !value)for(unsigned i=4;i<20;i++)row[i]=0;
        }
        if(!(uint16_t)action && half(row+10)){
            int value=ffta_myk_fight_ai_value((int16_t)half(row+12),
                *(const uint8_t *const *)actor,*(const uint8_t *const *)target);
            row[12]=(uint8_t)value;row[13]=(uint8_t)(value>>8);
        }
        return;
    }
    ChoiceScope scope;ffta_ai_choice_begin(&scope,*(const uint8_t *const *)actor,action,0,0);
    uint8_t candidate[20];int best=-1;
    const uint8_t *unit=*(const uint8_t *const *)target;
    static const uint8_t status[4]={10,27,9,28};
    /* Keep one record per actual action: the native40-row allocations and
     * deduplication remain intact. Compare the native signed effect value;
     * non-applicable statuses (including an existing ailment) score zero.
     * Ties are stable in menu order. Native action/target ranking follows. */
    uint8_t options[5]={1,2,3,4,0};unsigned positions[5]={0,0,0,0,0},count=4;
    if(action==FFTA_GEO_A8)count=ffta_geo_ai_row_options(&scope,options,positions);
    for(unsigned ordinal=0;ordinal<count;ordinal++){
        unsigned choice=options[ordinal];
        scope.choice=choice;
        scope.position=positions[ordinal];
        for(unsigned i=0;i<20;i++)candidate[i]=0;
        ffta_ai_original_row(candidate,actor,target,action,choice,flags);
        /* Native status forecasts assign the same weight even when an ailment
         * is already present. Do not spend a turn refreshing it, or cast an
         * enemy-only dance on an ally because its donor accepted that target. */
        if(action==FFTA_DNC_A6 && ((unit[0xe8+status[choice-1]/8]&(1u<<(status[choice-1]%8))) ||
           (((scope.actor[0x29]>>7)^((scope.actor[0xeb]>>5)&1u))==(unit[0x29]>>7)))){
            for(unsigned i=4;i<20;i++)candidate[i]=0;
        }
        int value=(int16_t)half(candidate+12);
        if(action==FFTA_DNC_A6){if(value<0)value=-value;}
        else{
            unsigned enemy=(((scope.actor[0x29]>>7)^((scope.actor[0xeb]>>5)&1u))!=(unit[0x29]>>7));
            if(!enemy)value=-value;
            if(value<=0){value=0;for(unsigned i=4;i<20;i++)candidate[i]=0;}
        }
        if(!half(candidate+10))value=0;
        if(value>best){best=value;for(unsigned i=0;i<20;i++)row[i]=candidate[i];}
    }
    ffta_ai_choice_end(&scope);
}

int ffta_ai_choice_score(const uint8_t *actor,const uint8_t *target,unsigned action,unsigned flags){
    const uint8_t *node=(const uint8_t *)0x02015488u;
    unsigned choice=half(node+10);
    if(ffta_chemist_action((uint16_t)action)){
        if(*(const uint8_t *const *)node!=actor || half(node+8)!=(uint16_t)action)return 0;
        return ffta_medicine_ai_value(*(const uint8_t *const *)actor,
            *(const uint8_t *const *)target,(uint16_t)action,choice);
    }
    if(!supported((uint16_t)action) || *(const uint8_t *const *)node!=actor ||
       half(node+8)!=(uint16_t)action || !valid(action,choice))
    {
        if((uint16_t)action==FFTA_MYK_A12)return 0;
        if(action==FFTA_MYK_A14)return ffta_myk_ai_break_value(*(const uint8_t *const *)actor,*(const uint8_t *const *)target);
        int score=ffta_ai_original_score(actor,target,action,flags);
        score=ffta_bard_ai_value(score,*(const uint8_t *const *)actor,
            *(const uint8_t *const *)target,(uint16_t)action);
        score=martial_value(score,*(const uint8_t *const *)actor,
            *(const uint8_t *const *)target,(uint16_t)action);
        if(ffta_dancer_ai_redundant(*(const uint8_t *const *)target,(uint16_t)action) ||
           repeated_challenge(*(const uint8_t *const *)actor,*(const uint8_t *const *)target,(uint16_t)action))return 0;
        if(ffta_geo_ai_utility((uint16_t)action))
            return ffta_geo_ai_utility_value(score,*(const uint8_t *const *)actor,
                *(const uint8_t *const *)target,(uint16_t)action);
        score=ffta_myk_ai_strike_value(score,*(const uint8_t *const *)actor,*(const uint8_t *const *)target,action);
        if(action>=FFTA_MYK_A1 && action<=FFTA_MYK_A11 &&
           *(const uint8_t *const *)actor==*(const uint8_t *const *)target)
            return ffta_myk_ai_self_value(score,*(const uint8_t *const *)actor);
        return (uint16_t)action?score:ffta_myk_fight_ai_value(score,
            *(const uint8_t *const *)actor,*(const uint8_t *const *)target);
    }
    ChoiceScope scope;ffta_ai_choice_begin(&scope,*(const uint8_t *const *)actor,action,choice,0);
    int score=ffta_ai_original_score(actor,target,action,flags);
    if((uint16_t)action==FFTA_MYK_A12)score=ffta_myk_ai_spellbreak_value(score,scope.actor,*(const uint8_t *const *)target,choice);
    ffta_ai_choice_end(&scope);return score;
}
