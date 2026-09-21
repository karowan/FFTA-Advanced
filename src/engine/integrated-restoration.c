#include "native-unit.h"
#include <stdint.h>
#include "registry.h"
#include "samurai-state.h"
#include "chemist-items.h"
#include "bard.h"
#include "dancer.h"
#include "turn-supports.h"
extern int ffta_drk_healing(const uint8_t *);
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static unsigned support(const uint8_t *u){return ((unsigned (*)(const uint8_t *))0x080cd50du)(u);}
/* An explicit evaluated actor/recipient pair owns this decision. No roster
 * lookup, weapon requirement, item user's incoming support or undead inversion. */
unsigned ffta_recuperation_numerator(const uint8_t *actor,const uint8_t *target){
    if(!actor || !target || !half(target+0x18) || ffta_native_undead(target))return 2;
    unsigned a=((actor[0x29]>>7)^((actor[0xeb]>>5)&1u)),t=target[0x29]>>7;
    return (actor==target || a==t) && support(target)==FFTA_SLD_AX_S1?3:2;
}
static unsigned capped(unsigned amount,const uint8_t *target){
    unsigned hp=half(target+0x18),maximum=half(target+0x1a),missing=maximum>hp?maximum-hp:0;
    return amount<missing?amount:missing;
}
static unsigned item_action(unsigned action){return (action>=251 && action<=253) || action==FFTA_CHM_A1 || action==FFTA_CHM_A4 || action==FFTA_CHM_A5;}
int ffta_integrated_item_healing(const uint8_t *c){
    const uint8_t *actor=*(const uint8_t *const *)c,*target=*(const uint8_t *const *)(c+4);
    unsigned action=half(c+12);
    if(!actor || !target)return 0;
    if(!item_action(action))return ((int (*)(const uint8_t *))0x08131961u)(c);
    if(ffta_native_undead(target) && !(action>=251 && action<=253))return 0;
    unsigned base;
    if(action==FFTA_CHM_A4){
        FFTA_ChemistRecipe recipe;if(!ffta_chemist_recipe(action,half(c+14),&recipe))return 0;
        base=recipe.donor==252?50:150;
    }else if(action==FFTA_CHM_A5){
        /* The recipe explicitly floors its 20% base. Combine subsequent
         * support modifiers before their single final division. */
        base=half(target+0x1a)/5u;if(base<50)base=50;if(base>100)base=100;
    }else base=action==252?50:action==253?150:25;
    unsigned pharmacology=support(actor)==FFTA_CHM_S1?3:2;
    unsigned amount=base*pharmacology*ffta_recuperation_numerator(actor,target)/4u;
    /* Ordinary Item keeps its native uncapped display; its HP writer caps
     * actual restoration. New medicines already promise capped previews. */
    return (int)(action>=251 && action<=253?amount:capped(amount,target));
}
int ffta_integrated_technique_healing(const uint8_t *c){
    unsigned action=half(c+12);
    if(action==FFTA_BRD_A1 || action==FFTA_BRD_A5)return ffta_bard_healing(c);
    if(action!=FFTA_SAM_A4 && action!=FFTA_DRK_A4)return ffta_drk_healing(c);
    const uint8_t *actor=*(const uint8_t *const *)c,*target=*(const uint8_t *const *)(c+4);
    if(!actor || !target || !half(target+0x18) || ffta_native_undead(target))return 0;
    unsigned base;
    if(action==FFTA_SAM_A4){
        base=35u*half(target+0x1a);if(base>14000)base=14000;
        return (int)capped(base*ffta_centered_factor(actor,action)*ffta_recuperation_numerator(actor,target)*ffta_turn_healing_numerator(actor)/16000u,target);
    }
    if(actor!=target)return 0;
    base=20u*half(target+0x1a);if(base>10000)base=10000;
    return (int)capped(base*ffta_recuperation_numerator(actor,target)*ffta_turn_healing_numerator(actor)/4000u,target);
}
int ffta_integrated_restoration_stage(int signed_amount,const uint8_t *c){
    if(!c || signed_amount>=0)return signed_amount;
    unsigned action=half(c+12);
    if(item_action(action) || action==FFTA_SAM_A4 || action==FFTA_DRK_A4 || action==FFTA_BRD_A1 || action==FFTA_BRD_A5)return signed_amount;
    const uint8_t *d=*(const uint8_t *const *)(c+0x30);
    if(!d || d[1]>=93 || d[3]==18 || d[3]==40 || d[3]==41)return signed_amount; /* Drain and revival are separate. */
    const uint8_t *app=(const uint8_t *)0x083a87b0u+12u*d[1];
    if(app[4]!=1 || app[8]!=255)return signed_amount; /* No MP, revival or elemental absorption. */
    const uint8_t *actor=*(const uint8_t *const *)c,*target=*(const uint8_t *const *)(c+8);
    return -(int)((unsigned)(-signed_amount)*ffta_recuperation_numerator(actor,target)*ffta_turn_healing_numerator(actor)/40u);
}
extern int ffta_chemist_mp(const uint8_t *);
int ffta_integrated_mp_restoration(const uint8_t *c){return half(c+12)==FFTA_DNC_A2?ffta_dancer_witch_hunt(c):half(c+12)==FFTA_BRD_A7?ffta_bard_mp(c):ffta_chemist_mp(c);}
