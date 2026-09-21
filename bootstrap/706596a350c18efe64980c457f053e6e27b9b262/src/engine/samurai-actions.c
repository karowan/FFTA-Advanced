#include <stdint.h>
#include "registry.h"
#include "samurai-state.h"
#include "execution-scope.h"
#include "action-snapshot.h"

static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
static void put_half(uint8_t *p,unsigned v) { p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8); }
extern unsigned ffta_exposed_paid_commit(uint8_t *,unsigned) __attribute__((weak));
/* One shared payment gate. Reject Fell before changing MP or consuming
 * Centered; the optional binding keeps private Samurai builds independent. */
unsigned ffta_custom_physical_paid(uint8_t *actor,unsigned action) {
    if(ffta_exposed_paid_commit && !ffta_exposed_paid_commit(actor,action))return 0;
    ffta_centered_paid(actor,action);
    return 1;
}
extern unsigned ffta_dark_weapon_valid(unsigned,unsigned);
extern unsigned ffta_primary_weapon(const uint8_t *);
extern unsigned ffta_dark_law_weapons(const uint8_t *,uint16_t *,unsigned);
unsigned ffta_samurai_law_weapons(const uint8_t *actor,uint16_t *weapons,unsigned action) {
    if(!ffta_samurai_direct_action(action))return ffta_dark_law_weapons(actor,weapons,action);
    unsigned primary=ffta_primary_weapon(actor);
    if(primary)weapons[0]=(uint16_t)primary;
    return primary!=0;
}
unsigned ffta_samurai_weapon_valid(unsigned action,unsigned weapon) {
    if(!ffta_samurai_direct_action(action))return ffta_dark_weapon_valid(action,weapon);
    return ((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(weapon,3)==9;
}

extern unsigned ffta_dark_sword_apply(uint8_t *,int,uint8_t *,uint8_t *);
extern void ffta_higanbana_commit(uint8_t *,unsigned,uint8_t *,uint8_t *);
unsigned ffta_samurai_apply(uint8_t *target,int delta,uint8_t *object,uint8_t *row) {
    unsigned before=half(target+0x18);
    unsigned result=ffta_dark_sword_apply(target,delta,object,row);
    unsigned after=half(target+0x18),action=half(object+0x10);
    ffta_higanbana_commit(target,before,object,row);
    if(!ffta_samurai_direct_action(action) || before<=after)return result;
    uint8_t *actor=**(uint8_t ***)object;
    if(!actor || actor==target)return result;
    unsigned side=((half(actor+0x28)>>15)^((actor[0xeb]>>5)&1))&1;
    if(side==((half(target+0x28)>>15)&1))return result;
    if(action==FFTA_SAM_A1)ffta_centered_grant(actor,1);
    else if(action==FFTA_SAM_A3) {
        unsigned amount=half(target+0x1c);
        if(amount>10)amount=10;
        put_half(target+0x1c,half(target+0x1c)-amount);
        if(amount) {
            put_half(row+0xc,half(row+0xc)|2);
            put_half(row+0x20,amount);
        }
    }
    return result;
}

/* A4672 is after both native result-generation attempts. The original status
 * compatibility check and exact Protect setters/timer are retained;
 * damage/healing calculations cannot invoke this function. */
void ffta_samurai_after_attempt(uint8_t *actor,unsigned action,unsigned valid) {
    if(action!=FFTA_SAM_A6 || !valid || !actor || !half(actor+0x18))return;
    /* The compatibility table takes effect82 (Protect), not status bit25. */
    if(!((unsigned (*)(uint8_t *,unsigned))0x08133a59u)(actor,82))return;
    /* Native Protect handler1335C0 uses these setters with1 and3. */
    ((void (*)(uint8_t *,unsigned))0x080ce095u)(actor,1);
    ((void (*)(uint8_t *,unsigned))0x080ce449u)(actor,3);
    /* Preserve the native effect's status-removal mask (including Invisible),
     * timer cleanup and derived-unit refresh, without an extra weapon proc. */
    ((void (*)(unsigned,uint8_t *))0x08131c29u)(82,actor);
    ((void (*)(uint8_t *))0x08131c59u)(actor);
    ((void (*)(uint8_t *))0x080ca2e9u)(actor);
}

void ffta_samurai_regen(uint8_t *actor) {
    if(!actor || !half(actor+0x18) ||
       !((unsigned (*)(uint8_t *,unsigned))0x08133a59u)(actor,31))return;
    ((void (*)(uint8_t *,unsigned))0x080cdd65u)(actor,1);
    ((void (*)(unsigned,uint8_t *))0x08131c29u)(31,actor);
    ((void (*)(uint8_t *))0x08131c59u)(actor);
    ((void (*)(uint8_t *))0x080ca2e9u)(actor);
}

void ffta_samurai_completed_results(uint8_t *actor,unsigned action,unsigned valid,const uint8_t *object) {
    if(action!=FFTA_SAM_A8 || !valid || !actor || !object || object[0x2c0]>15)return;
    unsigned side=((half(actor+0x28)>>15)^((actor[0xeb]>>5)&1))&1;
    for(unsigned i=0;i<object[0x2c0];++i) {
        const uint8_t *row=object+0x20+0x2c*i;
        const uint8_t *wrapper=*(const uint8_t *const *)row;
        const uint8_t *target=wrapper?*(const uint8_t *const *)wrapper:0;
        if(target && target!=actor && side!=((half(target+0x28)>>15)&1) &&
           (half(row+0xc)&1u) && (int16_t)half(row+0x1e)>0) {
            ffta_samurai_regen(actor);
            return;
        }
    }
}

extern unsigned ffta_physical_law_hit(const uint8_t *,unsigned,const uint8_t *,unsigned);
extern unsigned ffta_physical_eligibility(const uint8_t *);
extern int ffta_physical_magnitude(const uint8_t *);
static unsigned moon_predicted_hp_damage(const uint8_t *context) {
    const uint8_t *actor=*(const uint8_t *const *)context;
    const uint8_t *target=*(const uint8_t *const *)(context+4);
    if(!actor || !target || !ffta_physical_eligibility(context))return 0;
    uint8_t query[0x34];
    for(unsigned i=0;i<sizeof(query);++i)query[i]=context[i];
    query[0x26]|=0x10;
    /* The native formula samples RNG even on this query path. Our added
     * prediction must not introduce another sample into native law handling. */
    volatile uint32_t *rng=(volatile uint32_t *)0x030034b0u;
    uint32_t saved_rng=*rng;
    unsigned damages=ffta_physical_magnitude(query)>0;
    /* Preserve the native reaction's own MP/status/admission rules. */
    if(damages && ((unsigned (*)(const uint8_t *))0x0812e6a5u)(target)==13 &&
       ((unsigned (*)(const uint8_t *,const uint8_t *,unsigned,unsigned))0x0812e6e1u)(actor,target,FFTA_SAM_A8,13))damages=0;
    *rng=saved_rng;
    return damages;
}
extern unsigned ffta_original_samurai_law_status(uint8_t *,uint8_t *,unsigned,unsigned,unsigned,unsigned);
unsigned ffta_samurai_law_status(uint8_t *actor,uint8_t *target,unsigned action,
                                 unsigned item,unsigned status,unsigned removal) {
    if((action!=FFTA_SAM_A6 && action!=FFTA_SAM_A8) || !removal || status>=44)
        return ffta_original_samurai_law_status(actor,target,action,item,status,removal);
    /* Native1342CC's removal precheck reads the target. Guarding Draw's
     * secondary Protect instead belongs to the actor; simulate its ordinary
     * removal mask on that caller-owned law copy, with action admission. */
    uint8_t context[0x34];
    for(unsigned i=0;i<sizeof(context);++i)context[i]=0;
    *(uint8_t **)context=actor;*(uint8_t **)(context+4)=target;
    put_half(context+12,action);
    if(!actor || !target || !ffta_physical_eligibility(context))return 0;
    unsigned mask=1u<<(status&7),offset=0xe8u+(status>>3);
    unsigned before=actor[offset]&mask;
    if(action==FFTA_SAM_A8) {
        if(!moon_predicted_hp_damage(context))return 0;
        ffta_samurai_regen(actor);
    } else ffta_samurai_after_attempt(actor,action,1);
    return before && !(actor[offset]&mask);
}
unsigned ffta_samurai_law_hit(const uint8_t *context,unsigned removal,
                              const uint8_t *status_byte,unsigned bit) {
    if(half(context+12)==FFTA_SAM_A8 && context[0x28]==0) {
        uint8_t *actor=*(uint8_t *const *)context;
        if(!moon_predicted_hp_damage(context) ||
           !((unsigned (*)(uint8_t *,unsigned))0x08133a59u)(actor,31))return 0;
        ffta_samurai_regen(actor);
        return !removal && status_byte==context+0x10 && bit==3;
    }
    if(half(context+12)!=FFTA_SAM_A6 || context[0x28]!=0)
        return ffta_physical_law_hit(context,removal,status_byte,bit);
    uint8_t *actor=*(uint8_t *const *)context;
    if(!actor || !half(actor+0x18) ||
       !((unsigned (*)(uint8_t *,unsigned))0x08133a59u)(actor,82))return 0;
    /* Native1343C8 supplies independent owned actor/recipient copies here.
     * Guarding Draw grants Protect on an admitted attempt, including misses;
     * its native status law therefore queries that self-grant, not the enemy.
     * Apply the same setters to the evaluated actor, never a live substitute. */
    ffta_samurai_after_attempt(actor,FFTA_SAM_A6,1);
    return !removal && status_byte==context+0x13 && bit==1;
}

extern unsigned ffta_original_samurai_execute(uint8_t *,uint8_t *,unsigned,unsigned,
    unsigned,unsigned,unsigned,unsigned);
unsigned ffta_samurai_execute(uint8_t *output,uint8_t *wrapper,unsigned x,unsigned y,
    unsigned action,unsigned item,unsigned mode,unsigned last) {
    uint8_t *actor=wrapper?*(uint8_t **)wrapper:0;
    unsigned nested=ffta_centered_factor(actor,FFTA_SAM_A3)==5 && !ffta_centered_active(actor);
    FFTA_ExecutionScope scope;
    unsigned opened=ffta_execution_open(&scope,actor,action);
    FFTA_ActionSnapshot snapshot;
    unsigned snapshotted=ffta_snapshot_begin(&snapshot,actor,0,1);
    unsigned result=ffta_original_samurai_execute(output,wrapper,x,y,action,item,mode,last);
    ffta_samurai_completed_results(actor,action,1,output);
    if(!nested)ffta_centered_retire(actor);
    if(opened)ffta_execution_close(&scope);
    if(snapshotted)ffta_snapshot_end(&snapshot);
    return result;
}
