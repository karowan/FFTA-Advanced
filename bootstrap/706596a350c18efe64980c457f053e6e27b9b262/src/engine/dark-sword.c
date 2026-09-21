#include <stdint.h>
#include "registry.h"

static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
static void put_half(uint8_t *p,unsigned v) { p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8); }
static unsigned smaller(unsigned a,unsigned b) { return a<b?a:b; }
unsigned ffta_dark_sword_action(unsigned action) {
    return action==FFTA_DRK_A2 || action==FFTA_DRK_A3;
}
unsigned ffta_dark_weapon_valid(unsigned action,unsigned weapon) {
    unsigned type=((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(weapon,3);
    return ffta_dark_sword_action(action) ? type==1 || type==5 || type==6 : type==31;
}
extern unsigned ffta_primary_weapon(const uint8_t *);
unsigned ffta_dark_law_weapons(const uint8_t *actor,uint16_t *weapons,unsigned action) {
    if(!ffta_dark_sword_action(action))
        return ((unsigned (*)(const uint8_t *,uint16_t *))0x0812f0d9u)(actor,weapons);
    unsigned primary=ffta_primary_weapon(actor);
    if(primary)weapons[0]=(uint16_t)primary;
    return primary!=0;
}

/* Pure resource plan. HP was observed immediately around the native HP
 * application, so overkill, misses, absorption and MP redirection cannot
 * manufacture recovery. Packed output: low16 target MP loss; high16 signed
 * actor resource delta (positive is loss, negative is recovery).
 * The caller owns phase-specific mutation and native result bookkeeping. */
uint32_t ffta_dark_sword_plan(unsigned action,const uint8_t *actor,
    const uint8_t *target,unsigned removed) {
    if(!ffta_dark_sword_action(action) || !actor || !target || !removed || actor==target)
        return 0;
    unsigned side=((half(actor+0x28)>>15)^((actor[0xeb]>>5)&1))&1;
    if(side==((half(target+0x28)>>15)&1))return 0;
    unsigned undead=(target[0xe8]&4)!=0;
    if(action==FFTA_DRK_A2) {
        unsigned amount=smaller(removed/2,half(actor+0x1a)/5);
        if(!undead)amount=smaller(amount,half(actor+0x1a)>half(actor+0x18) ? half(actor+0x1a)-half(actor+0x18):0);
        return (uint32_t)(uint16_t)(undead?(int)amount:-(int)amount)<<16;
    }
    unsigned removed_mp=smaller(smaller(removed/5,16),half(target+0x1c));
    unsigned amount=undead ? smaller(removed_mp,half(actor+0x1c)) :
        smaller(removed_mp,half(actor+0x1e)>half(actor+0x1c) ? half(actor+0x1e)-half(actor+0x1c):0);
    return removed_mp|((uint32_t)(uint16_t)(undead?(int)amount:-(int)amount)<<16);
}

/* Only the ordinary battle executor calls this at A315A. The native HP
 * function runs exactly once on the explicit result recipient. Prediction
 * and law callbacks do not call this entry. No global ownership registry or
 * persistent temporary state is needed for these immediate riders. */
unsigned ffta_dark_sword_apply(uint8_t *target,int delta,uint8_t *object,uint8_t *row) {
    unsigned before=half(target+0x18);
    unsigned result=((unsigned (*)(uint8_t *,int))0x080a2211u)(target,delta);
    unsigned after=half(target+0x18),action=half(object+0x10);
    if(!ffta_dark_sword_action(action) || before<=after)return result;
    uint8_t *actor=**(uint8_t ***)object;
    uint32_t plan=ffta_dark_sword_plan(action,actor,target,before-after);
    int actor_delta=(int16_t)(plan>>16);
    if(action==FFTA_DRK_A2) {
        /* Native A487A -> A22F0 applies this accumulated actor HP delta,
         * including recovery clamp, critical-state and undead reversal KO.
         * It never enters the enemy reaction dispatcher for this recovery. */
        put_half(object+6,(unsigned)((int16_t)half(object+6)+actor_delta));
    } else {
        unsigned removed_mp=plan&0xffff;
        put_half(target+0x1c,half(target+0x1c)-removed_mp);
        put_half(actor+0x1c,(unsigned)((int)half(actor+0x1c)-actor_delta));
        if(removed_mp) {
            put_half(row+0xc,half(row+0xc)|2);
            put_half(row+0x20,removed_mp);
        }
    }
    return result;
}
