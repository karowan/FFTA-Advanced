#include <stdint.h>
#include "registry.h"
#include "samurai-state.h"
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
extern unsigned ffta_primary_weapon(const uint8_t *);
unsigned ffta_samurai_restoration_action(unsigned action) {
    return action==FFTA_SAM_A4 || action==FFTA_SAM_A5;
}
unsigned ffta_samurai_restoration_eligibility(const uint8_t *context) {
    const uint8_t *actor=*(const uint8_t *const *)context;
    const uint8_t *target=*(const uint8_t *const *)(context+4);
    if(!actor || !target || !half(target+0x18) || (actor[0xeb]&0x10))return 0;
    if(half(context+12)==FFTA_SAM_A4 && (target[0xe8]&4))return 0;
    unsigned side=((half(actor+0x28)>>15)^((actor[0xeb]>>5)&1))&1;
    if(side!=((half(target+0x28)>>15)&1))return 0;
    unsigned weapon=ffta_primary_weapon(actor);
    return weapon && ((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(weapon,3)==9;
}
int ffta_murasame_magnitude(const uint8_t *context) {
    if(half(context+12)!=FFTA_SAM_A4)
        return ((int (*)(const uint8_t *))0x08131839u)(context);
    const uint8_t *actor=*(const uint8_t *const *)context;
    const uint8_t *target=*(const uint8_t *const *)(context+4);
    if(!actor || !target || !half(target+0x18) || (target[0xe8]&4))return 0;
    unsigned maximum=half(target+0x1a),hp=half(target+0x18);
    if(hp>=maximum)return 0;
    /* Cap the rational base at140 before applying Centered. Divide only once
     * so a fractional35% base is not rounded away before the25% bonus. */
    unsigned base=35u*maximum;
    if(base>14000u)base=14000u;
    unsigned recovery=base*ffta_centered_factor(actor,FFTA_SAM_A4)/400u;
    unsigned missing=maximum-hp;
    return (int)(recovery<missing ? recovery : missing);
}
