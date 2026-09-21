#include <stdint.h>
#include "registry.h"
#include "action-snapshot.h"
#include "dark-knight-state.h"
#include "dark-knight-imports.h"
#include "unit-query.h"

static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
extern unsigned ffta_physical_eligibility(const uint8_t *);
extern unsigned ffta_primary_weapon(const uint8_t *);
unsigned ffta_drk_law_weapons(const uint8_t *actor,uint16_t *weapons,unsigned action) {
    if(action!=FFTA_DRK_A1 && action!=FFTA_DRK_A5 && action!=FFTA_DRK_A6 && action!=FFTA_DRK_A7 && action!=FFTA_DRK_A8)
        return ((unsigned (*)(const uint8_t *,uint16_t *,unsigned))DRK_PRIOR_LAW_WEAPONS)(actor,weapons,action);
    unsigned primary=ffta_primary_weapon(actor);
    if(primary)weapons[0]=(uint16_t)primary;
    return primary!=0;
}
extern int ffta_drk_direct_stage(int,const uint8_t *);
int ffta_drk_stage(int damage,const uint8_t *context) {
    return ffta_drk_direct_stage(damage,context);
}
unsigned ffta_drk_weapon_valid(unsigned action,unsigned item) {
    if(action!=FFTA_DRK_A1 && action!=FFTA_DRK_A5 && action!=FFTA_DRK_A6 && action!=FFTA_DRK_A7 && action!=FFTA_DRK_A8)
        return ((unsigned (*)(unsigned,unsigned))DRK_PRIOR_WEAPON)(action,item);
    if(action==FFTA_DRK_A5)return item && !((unsigned (*)(unsigned))0x08130621u)(item);
    unsigned type=((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(item,3);
    return type==1 || type==5 || type==6;
}
static unsigned ffta_drk_sacrifice_cost(const uint8_t *actor,unsigned action) {
    if(!actor || (action!=FFTA_DRK_A1 && action!=FFTA_DRK_A7 && action!=FFTA_DRK_A8 && action!=FFTA_DRK_A9))return 0;
    unsigned amount=(half(actor+0x1a)*(action==FFTA_DRK_A8?20u:action==FFTA_DRK_A7?15u:10u)+99)/100;
    return amount?amount:1;
}
/* Magnitude receives the explicit evaluated units. Native preview B5678..
 * B56AC temporarily supplies their wrapper positions before B572C calls the
 * formula, then restores the old positions. Range admission still uses the
 * separate evaluated-coordinate geometry ABI. Never resolve these pointers
 * to roster owners or infer distance from a selected area center. */
unsigned ffta_drk_line_numerator(const uint8_t *actor,const uint8_t *target) {
    if(!actor || !target)return 0;
    unsigned ax=actor[0xf6],ay=actor[0xf7],tx=target[0xf6],ty=target[0xf7];
    if(ax>15 || ay>15 || tx>15 || ty>15)return 0;
    unsigned dx=ax>tx?ax-tx:tx-ax,dy=ay>ty?ay-ty:ty-ay;
    unsigned distance=dx+dy;
    if((dx && dy) || distance<1 || distance>3)return 0;
    return 155u-15u*distance;
}
extern int ffta_drk_original_mp_cost(const uint8_t *,unsigned);
static unsigned bloodcasting(const uint8_t *actor) {
    return actor && (actor[6]==1 || actor[6]==2) &&
        ((unsigned (*)(const uint8_t *))0x080cd50du)(actor)==FFTA_DRK_S2;
}
int ffta_drk_mp_cost(const uint8_t *actor,unsigned action) {
    if(bloodcasting(actor) && ffta_action_origin()!=FFTA_ACTION_NATIVE_REACTION)return 0;
    return ffta_drk_original_mp_cost(actor,action);
}
unsigned ffta_drk_hp_cost(const uint8_t *actor,unsigned action) {
    unsigned cost=ffta_drk_sacrifice_cost(actor,action);
    if(bloodcasting(actor) && ffta_action_origin()!=FFTA_ACTION_NATIVE_REACTION) {
        int mp=ffta_drk_original_mp_cost(actor,action);
        if(mp>0)cost+=2u*(unsigned)mp;
    }
    return cost;
}
unsigned ffta_drk_paid(uint8_t *actor,unsigned action) {
    unsigned cost=ffta_drk_hp_cost(actor,action);
    if(cost && (!actor || half(actor+0x18)<=cost))return 0;
    if(!((unsigned (*)(uint8_t *,unsigned))DRK_PRIOR_PAID)(actor,action))return 0;
    /* The native HP writer computes critical-state transitions but does not
     * dispatch reactions. Costs have no target-result row or injury event. */
    if(cost)((unsigned (*)(uint8_t *,int))0x080a2211u)(actor,(int)cost);
    return 1;
}
extern unsigned ffta_drk_original_usable(uint8_t *,unsigned,unsigned);
unsigned ffta_drk_usable(uint8_t *actor,unsigned action,unsigned item) {
    unsigned cost=ffta_drk_hp_cost(actor,(uint16_t)action);
    if(cost && (!actor || half(actor+0x18)<=cost))return 0;
    return ffta_drk_original_usable(actor,action,item);
}

extern int ffta_physical_magnitude(const uint8_t *);
static unsigned rider_action(unsigned action) { return action==FFTA_DRK_A6 || action==FFTA_DRK_A8; }
/* Real staged effects use measured native HP loss. Preview/law queries predict
 * the preceding physical stage on a private context and restore native RNG. */
unsigned ffta_drk_rider_eligible(const uint8_t *context) {
    const uint8_t *actor=*(const uint8_t *const *)context;
    const uint8_t *target=*(const uint8_t *const *)(context+4);
    unsigned action=half(context+12);
    if(!actor || !target || !ffta_physical_eligibility(context))return 0;
    if(!(context[0x26]&0x10) && ffta_action_phase()==FFTA_ACTION_RESULT && ffta_action_id()==action)
        return ffta_action_hp_lost(target)>0;
    uint8_t query[0x34],saved_context[0x34];
    volatile uint8_t *native_context=(volatile uint8_t *)0x0200f3f0u;
    for(unsigned i=0;i<sizeof(query);++i) {
        query[i]=context[i];saved_context[i]=native_context[i];
    }
    query[0x26]|=0x10;query[0x28]=0;
    *(const uint8_t **)(query+0x30)=(const uint8_t *)DRK_DESCRIPTOR_BANK+63*4;
    volatile uint32_t *rng=(volatile uint32_t *)0x030034b0u;
    uint32_t saved=*rng;
    unsigned damages=ffta_physical_magnitude(query)>0;
    if(damages && ((unsigned (*)(const uint8_t *))0x0812e6a5u)(target)==13 &&
       ((unsigned (*)(const uint8_t *,const uint8_t *,unsigned,unsigned))0x0812e6e1u)(actor,target,action,13))damages=0;
    *rng=saved;
    for(unsigned i=0;i<sizeof(saved_context);++i)native_context[i]=saved_context[i];
    return damages;
}
/* Dark Mind is a martial self-only action. Its two ordinary native stages
 * retain the game's Shell compatibility, removal mask and timer machinery.
 * Only the admission and rational healing amount differ from native donors. */
unsigned ffta_drk_eligibility(const uint8_t *context) {
    unsigned action=half(context+12);
    if(rider_action(action) && context[0x28])return ffta_drk_rider_eligible(context);
    if(action==433 || action==434) {
        const uint8_t *actor=*(const uint8_t *const *)context;
        const uint8_t *target=*(const uint8_t *const *)(context+4);
        if(!actor || !target || !half(actor+0x18) || !half(target+0x18) || (target[0xe8]&0x40u))return 0;
        return action==433?actor==target:actor!=target;
    }
    if(action==FFTA_DRK_A5 || action==FFTA_DRK_A9) {
        const uint8_t *actor=*(const uint8_t *const *)context;
        const uint8_t *target=*(const uint8_t *const *)(context+4);
        if(!actor || !target || !half(actor+0x18) || !half(target+0x18) ||
           (actor[0xeb]&0x10u) || (target[0xe8]&0x40u))return 0;
        if(action==FFTA_DRK_A5) {
            if(actor==target || context[0x28])return 1;
            return ffta_physical_eligibility(context);
        }
        unsigned side=((actor[0x29]>>7)^((actor[0xeb]>>5)&1u));
        return side==(target[0x29]>>7) && ffta_job_origin(actor) && ffta_job_state((uint8_t *)target)!=0;
    }
    if(action!=FFTA_DRK_A4)return ffta_physical_eligibility(context);
    const uint8_t *actor=*(const uint8_t *const *)context;
    const uint8_t *target=*(const uint8_t *const *)(context+4);
    return ffta_query_same_unit(context,actor,target) && half(actor+0x18) && !(actor[0xeb]&0x10);
}

int ffta_drk_healing(const uint8_t *context) {
    if(half(context+12)!=FFTA_DRK_A4)
        return ((int (*)(const uint8_t *))DRK_PRIOR_HEALING)(context);
    const uint8_t *actor=*(const uint8_t *const *)context;
    const uint8_t *target=*(const uint8_t *const *)(context+4);
    if(!ffta_query_same_unit(context,actor,target) || !half(actor+0x18))return 0;
    unsigned hp=half(actor+0x18),maximum=half(actor+0x1a);
    if(hp>=maximum)return 0;
    unsigned recovery=maximum/5;
    if(recovery>100)recovery=100;
    return (int)(recovery<maximum-hp?recovery:maximum-hp);
}

extern int ffta_drk_reaction_magnitude(const uint8_t *);
int ffta_drk_zero_magnitude(const uint8_t *context) {
    if(half(context+12)==434)return ffta_drk_reaction_magnitude(context);
    return ((int (*)(const uint8_t *))DRK_PRIOR_ZERO_MAGNITUDE)(context);
}
