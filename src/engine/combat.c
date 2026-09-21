#include <stdint.h>
#include "registry.h"

static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
typedef unsigned (*ItemValue)(unsigned,unsigned);
typedef struct { unsigned action,numerator,denominator; } PhysicalDefinition;
extern unsigned ffta_dark_weapon_valid(unsigned,unsigned);
extern unsigned ffta_exposed_can_apply(uint8_t *);
extern unsigned ffta_exposed_incoming_numerator(int,const uint8_t *);
static const PhysicalDefinition physical_definitions[]={
    {FFTA_DRK_A2,95,100},{FFTA_DRK_A3,75,100},
    {FFTA_SLD_AX_A1,11,10},
    {FFTA_SLD_AX_A2,9,10},
    {FFTA_SLD_AX_A3,9,10},
    {FFTA_SLD_AX_A4,1,1},
    {FFTA_GLD_AX_A1,1,1},
    {FFTA_GLD_AX_A2,11,10},
    {FFTA_GLD_AX_A3,1,10},
    {FFTA_GLD_AX_A4,18,10}
};
static const PhysicalDefinition *physical_definition(unsigned action) {
    for(unsigned i=0;i<sizeof(physical_definitions)/sizeof(physical_definitions[0]);++i)
        if(physical_definitions[i].action==action)return physical_definitions+i;
    return 0;
}

/* Same ordered search as native12E4F4, bounded to five slots and one result.
 * Do not use12E55C: it sorts dual weapons by attack instead of equipment order. */
unsigned ffta_primary_weapon(const uint8_t *unit) {
    if (!unit) return 0;
    ItemValue value=(ItemValue)0x080ca7a5u;
    for (unsigned slot=0;slot<5;++slot) {
        unsigned item=half(unit+0x2a+2*slot);
        if (!item || item>460) continue;
        unsigned hands=value(item,6);
        if (hands>=1 && hands<=2 && value(item,3)!=20) return item;
    }
    return 0;
}

unsigned ffta_physical_eligibility(const uint8_t *context) {
    unsigned action=half(context+12);
    if (!physical_definition(action))
        return ((unsigned (*)(const uint8_t *))0x08130a95u)(context);
    const uint8_t *actor=*(const uint8_t *const *)context;
    const uint8_t *target=*(const uint8_t *const *)(context+4);
    if (!actor || !target || actor==target || !half(target+0x18) || (actor[0xeb]&0x10)) return 0;
    /* Native AI reverses only the acting unit's allegiance under Charm.
     * Confusion normally selects Fight; reject a direct confused custom
     * invocation without introducing RNG into preview/eligibility. */
    unsigned acting_side=((half(actor+0x28)>>15)^((actor[0xeb]>>5)&1))&1;
    if (action!=FFTA_SLD_AX_A3 && action!=FFTA_GLD_AX_A2 &&
        acting_side==((half(target+0x28)>>15)&1)) return 0;
    /* Range and height belong to native A0014/9FEF0/12E1A8, which receive
     * evaluated coordinates explicitly. Unit F6/F7 still hold the old tile
     * during an uncommitted Move; reading them here breaks legal previews.
     * Do not resolve copied units back to live owners to infer a position. */
    if(action==FFTA_GLD_AX_A4 && !ffta_exposed_can_apply((uint8_t *)actor))return 0;
    unsigned weapon=ffta_primary_weapon(actor);
    return weapon && ffta_dark_weapon_valid(action,weapon);
}

/* The native dispatcher still owns compatibility, accuracy and application.
 * This wrapper changes only explicitly enabled physical actions; all
 * original descriptor users execute their untouched native callback. */
extern int ffta_physical_rider_reference(const uint8_t *,unsigned,unsigned);
int ffta_physical_magnitude(const uint8_t *context) {
    unsigned action=half(context+12);
    if (!physical_definition(action))
        return ((int (*)(const uint8_t *))0x0813189du)(context);
    const uint8_t *actor=*(const uint8_t *const *)context;
    const uint8_t *target=*(const uint8_t *const *)(context+4);
    unsigned weapon=ffta_primary_weapon(actor);
    if (!actor || !target || !weapon || !ffta_dark_weapon_valid(action,weapon)) return 0;
    return ffta_physical_rider_reference(context,weapon,(half(context+0x26)&0x10)?2:0);
}

/* One final multiplier phase after the native physical-hit reference has
 * resolved defense, elements, support inputs and variance, before its cap.
 * Only definitions above are enabled. Later distinct applicable
 * modifiers must join this product before this division, not round in series.
 * No evaluated unit or persistent state is mutated by this calculation. */
extern unsigned ffta_finisher_numerator(unsigned,const uint8_t *);
int ffta_physical_final(int reference,unsigned action,const uint8_t *actor,const uint8_t *target) {
    const PhysicalDefinition *definition=physical_definition(action);
    if (!definition) return reference;
    int64_t signed_reference=reference;
    uint64_t magnitude=(uint64_t)(signed_reference<0 ? -signed_reference : signed_reference);
    unsigned numerator=action==FFTA_GLD_AX_A3 ? ffta_finisher_numerator(action,target) : definition->numerator;
    unsigned primary=ffta_primary_weapon(actor);
    unsigned restorative=primary && ((unsigned (*)(unsigned))0x08130621u)(primary);
    /* Resolve healing/absorption before admitting incoming physical factors.
     * Target is the explicit evaluated defender, including an owned Shatter
     * scope. Combine its Exposed factor with this art's coefficient once. */
    unsigned incoming=restorative ? 5 : ffta_exposed_incoming_numerator(reference,target);
    magnitude=magnitude*numerator*incoming/(definition->denominator*5u);
    if (magnitude>0x7fffffffu) magnitude=0x7fffffffu;
    /* Restorative weapons remain restorative on custom actions even when
     * native elemental absorption and the weapon's healing reversal would
     * otherwise cancel each other and produce positive damage. */
    return signed_reference<0 || restorative ? -(int)magnitude : (int)magnitude;
}
