#include "native-unit.h"
#include "chemist-items.h"
#include "registry.h"
#include "job-state.h"
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
extern unsigned ffta_native_free_count(unsigned);
extern int ffta_native_lose_item(unsigned,unsigned);
unsigned ffta_chemist_action(unsigned action) { return action>=FFTA_CHM_A1 && action<=FFTA_CHM_A10; }
unsigned ffta_chemist_recipe(unsigned action,unsigned selected,FFTA_ChemistRecipe *r) {
    if(!r)return 0;
    r->item[0]=r->item[1]=0;r->count=0;r->donor=0;
    switch(action) {
    case FFTA_CHM_A1:r->item[0]=362;r->donor=251;break;
    case FFTA_CHM_A2:
        if(selected==367)r->donor=261;
        else if(selected==368)r->donor=262;
        else if(selected==369)r->donor=257;
        else if(selected==371)r->donor=259;
        else return 0;
        r->item[0]=(uint16_t)selected;break;
    case FFTA_CHM_A3:r->item[0]=375;r->donor=256;break;
    case FFTA_CHM_A4:
        if(selected!=363 && selected!=364)return 0;
        r->item[0]=(uint16_t)selected;r->donor=selected==363?252:253;break;
    case FFTA_CHM_A5:r->item[0]=362;r->item[1]=363;r->donor=251;break;
    case FFTA_CHM_A6:r->item[0]=365;r->donor=254;break;
    case FFTA_CHM_A7:r->item[0]=374;r->donor=264;break;
    case FFTA_CHM_A8:r->item[0]=364;r->item[1]=375;r->donor=256;break;
    case FFTA_CHM_A9:r->item[0]=362;r->item[1]=374;break;
    case FFTA_CHM_A10:r->item[0]=362;r->item[1]=371;break;
    default:return 0;
    }
    r->count=r->item[1]?2:1;return 1;
}
unsigned ffta_chemist_stocked(unsigned action,unsigned selected) {
    FFTA_ChemistRecipe r;
    if(!ffta_chemist_recipe(action,selected,&r))return 0;
    for(unsigned i=0;i<r.count;i++)if(!ffta_native_free_count(r.item[i]))return 0;
    return 1;
}
unsigned ffta_chemist_pay(unsigned action,unsigned selected) {
    FFTA_ChemistRecipe r;
    if(!ffta_chemist_recipe(action,selected,&r) || !ffta_chemist_stocked(action,selected))return 0;
    /* All recipes have distinct ingredients. No native callback or interrupt
     * yields between validation and these two bounded inventory writes. */
    for(unsigned i=0;i<r.count;i++)ffta_native_lose_item(r.item[i],1);
    return 1;
}
extern unsigned ffta_previous_eligibility(const uint8_t *);
unsigned ffta_chemist_eligibility(const uint8_t *c) {
    unsigned action=half(c+12);
    if(!ffta_chemist_action(action))return ffta_previous_eligibility(c);
    const uint8_t *actor=*(const uint8_t *const *)c,*target=*(const uint8_t *const *)(c+4);
    if(!actor || !target || (actor[0xeb]&0x10) || ffta_native_undead(target))return 0;
    unsigned origin=ffta_job_origin(actor);
    if(!origin || origin>24)return 0; /* no enemy access to player stock */
    unsigned side=((half(actor+0x28)>>15)^((actor[0xeb]>>5)&1))&1;
    if(side!=((half(target+0x28)>>15)&1))return 0;
    if(action==FFTA_CHM_A3 || action==FFTA_CHM_A8)
        return ((unsigned (*)(const uint8_t *))0x08130a0du)(c);
    if(((unsigned (*)(const uint8_t *))0x080c8281u)(target))return 0;
    if(action==FFTA_CHM_A2) {
        FFTA_ChemistRecipe r;
        if(!ffta_chemist_recipe(action,half(c+14),&r))return 0;
        unsigned descriptor=((const uint8_t *)0x0855187cu)[r.donor*28+12];
        unsigned effect=((const uint8_t *)0x08553e70u)[descriptor*4+1];
        for(unsigned status=0;status<44;status++)
            if(status!=12 && (target[0xe8+status/8]&(1u<<(status%8))) &&
               ((unsigned (*)(unsigned,unsigned,unsigned))0x081339a9u)(effect,status,1))return 1;
        return 0;
    }
    return 1;
}
static unsigned boosted(const uint8_t *actor,unsigned amount) {
    return actor && ((unsigned (*)(const uint8_t *))0x080cd50du)(actor)==FFTA_CHM_S1 ? amount*3u/2u:amount;
}
int ffta_chemist_hp(const uint8_t *c) {
    unsigned action=half(c+12);
    const uint8_t *actor=*(const uint8_t *const *)c,*target=*(const uint8_t *const *)(c+4);
    if(!actor || !target)return 0;
    unsigned amount;
    if(action==FFTA_CHM_A1)amount=25;
    else if(action==FFTA_CHM_A4) {
        FFTA_ChemistRecipe r;if(!ffta_chemist_recipe(action,half(c+14),&r))return 0;
        amount=r.donor==252?50:150;
    } else if(action==FFTA_CHM_A5) {
        amount=half(target+0x1a)/5u;if(amount<50)amount=50;if(amount>100)amount=100;
    } else {
        int original=((int (*)(const uint8_t *))0x08131961u)(c);
        return action>=251 && action<=253 && original>0 ? (int)boosted(actor,(unsigned)original):original;
    }
    if(ffta_native_undead(target))return 0;
    amount=boosted(actor,amount);
    unsigned hp=half(target+0x18),maximum=half(target+0x1a),missing=hp<maximum?maximum-hp:0;
    return (int)(amount<missing?amount:missing);
}
int ffta_chemist_mp(const uint8_t *c) {
    unsigned action=half(c+12);
    if(action!=FFTA_CHM_A6 && action!=254)return ((int (*)(const uint8_t *))0x0813195du)(c);
    const uint8_t *actor=*(const uint8_t *const *)c,*target=*(const uint8_t *const *)(c+4);
    if(!actor || !target)return 0;
    if(action==254 && ((unsigned (*)(const uint8_t *))0x080cd50du)(actor)!=FFTA_CHM_S1)
        return ((int (*)(const uint8_t *))0x0813195du)(c);
    unsigned amount=boosted(actor,80),mp=half(target+0x1c),max=half(target+0x1e),missing=mp<max?max-mp:0;
    return (int)(amount<missing?amount:missing);
}
int ffta_chemist_revive(const uint8_t *c) {
    /* Both approved revivals use the native Phoenix Down half-max formula;
     * no healing support, item support or numerical 200-HP ceiling applies. */
    return ((int (*)(const uint8_t *))0x08131a61u)(c);
}
/* ffta_chemist_payment_gate lives in chemist-payment.c. */
extern int ffta_chemist_reaction_consumption(unsigned,unsigned,const uint8_t *);
int ffta_chemist_consumption(unsigned item,unsigned amount,const uint8_t *object) {
    /* Native A2E70 is per recipient, not a whole-action cost boundary.
     * The complete recipe was paid at A45C6 before recipient execution. */
    if(object && ffta_chemist_action(half(object+0x10)))return 0;
    return ffta_chemist_reaction_consumption(item,amount,object);
}
extern void ffta_original_chemist_context(uint8_t *,unsigned,unsigned,unsigned);
void ffta_chemist_context(uint8_t *context,unsigned action,unsigned selected,unsigned flags) {
    static const uint8_t antidote[4]={126,1,1,1},eyes[4]={88,1,1,1},
        echo[4]={112,1,1,1},soft[4]={99,1,1,1};
    ffta_original_chemist_context(context,action,selected,flags);
    if((uint16_t)action!=FFTA_CHM_A2)return;
    const uint8_t *vector=selected==367?antidote:selected==368?eyes:selected==369?echo:selected==371?soft:0;
    if(vector)*(const uint8_t **)(context+0x2c)=vector;
}
extern unsigned ffta_previous_geometry(const uint8_t *,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned);
extern unsigned ffta_projectile_los(unsigned,unsigned,unsigned,unsigned);
unsigned ffta_chemist_geometry(const uint8_t *unit,unsigned ax,unsigned ay,unsigned tx,
    unsigned ty,unsigned action,unsigned item,unsigned mode) {
    unsigned result=ffta_previous_geometry(unit,ax,ay,tx,ty,action,item,mode);
    if(!result || !ffta_chemist_action((uint16_t)action))return result;
    return ffta_projectile_los((uint8_t)ax,(uint8_t)ay,(uint8_t)tx,(uint8_t)ty);
}
unsigned ffta_chemist_range(const uint8_t *unit,unsigned action) {
    unsigned range=((unsigned (*)(unsigned,unsigned))0x080ccd51u)(action,4);
    if(!unit || ((unsigned (*)(const uint8_t *))0x080cd50du)(unit)!=FFTA_CHM_S2)return range;
    if(!((action>=251 && action<=264) || (ffta_chemist_action(action) && action!=FFTA_CHM_A5)))return range;
    /* Only this explicit consumable domain is eligible. Preserve encoded
     * range flags and an existing range above five; no weapon/area changes. */
    unsigned radius=range&0x3fu;
    if(radius<4)radius=4;
    else if(radius<5)radius++;
    return (range&~0x3fu)|radius;
}
