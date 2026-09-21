#include <stdint.h>
#include "battle-state.h"

static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }

/* Shared custom physical finalizers combine this exact numerator/5 with
 * their other rational factors BEFORE division. The supplied unit is the
 * explicit evaluated incoming recipient, never an inferred live identity. */
unsigned ffta_exposed_incoming_numerator(int damage,const uint8_t *recipient) {
    if(damage<=0)return 5;
    const uint8_t *owned=ffta_owned_exposed((uint8_t *)recipient);
    return owned && (*owned&1) ? 6 : 5;
}
static int incoming(int damage,const uint8_t *recipient) {
    if(ffta_exposed_incoming_numerator(damage,recipient)==5)return damage;
    uint64_t product=(uint64_t)(unsigned)damage*6u/5u;
    return product>999u ? 999 : (int)product;
}
static unsigned custom_physical(unsigned action) {
    /* These coefficients are applied once in the shared custom finalizer. */
    return action==357 || action==358 || (action>=424 && action<=431);
}
unsigned ffta_exposed_native_physical(const uint8_t *context) {
    if(!context)return 0;
    const uint8_t *descriptor=*(const uint8_t *const *)(context+0x30);
    if(!descriptor || ((const uint8_t *)0x083a87b0u)[descriptor[1]*12u+4]!=1)return 0;
    unsigned action=half(context+12),selector=descriptor[3];
    if(custom_physical(action))return 0;
    if(action==148 && selector==36)return 1; /* native Throw */
    if(action==211 && selector==38)return 1; /* native Hurl */
    if(action && !((unsigned (*)(unsigned,unsigned))0x080ccd51u)(action,29))return 0;
    /* Native damage-producing physical classes only. Selector42 is the
     * Backdraft/BodySlam self-cost;18 copies a prior drain for recovery;35
     * restores HP. Kind2 MP, native neutral percentages and fixed effects
     * do not become physical merely because their result is positive. */
    return selector==12 || selector==24 || selector==30 || selector==31 ||
        selector==39 || selector==43 || selector==44;
}
int ffta_exposed_native_stage(int damage,const uint8_t *context) {
    if(damage<=0 || !ffta_exposed_native_physical(context))return damage;
    return incoming(damage,*(const uint8_t *const *)(context+8));
}
extern int ffta_original_exposed_preview(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned,unsigned);
int ffta_exposed_preview(const uint8_t *actor,const uint8_t *target,unsigned action,
                         unsigned item,unsigned index,unsigned mode) {
    int damage=ffta_original_exposed_preview(actor,target,action,item,index,mode);
    return (uint16_t)action==0 ? incoming(damage,target) : damage;
}
extern int ffta_original_exposed_combo(const uint8_t *,const uint8_t *,unsigned);
int ffta_exposed_combo(const uint8_t *actor,const uint8_t *target,unsigned strength) {
    return incoming(ffta_original_exposed_combo(actor,target,strength),target);
}

/* Approved custom harmful-status policy: native Immunity support11 prevents
 * this drawback, making431 unavailable. No native status-ID alias, broad boss
 * immunity inference or Inoculation interception is used. */
unsigned ffta_exposed_can_apply(uint8_t *unit) {
    return unit && ffta_owned_exposed(unit) &&
        ((unsigned (*)(const uint8_t *))0x080cd50du)(unit)!=11;
}
unsigned ffta_exposed_paid_commit(uint8_t *unit,unsigned action) {
    if(action!=431)return 1;
    if(!ffta_exposed_can_apply(unit))return 0;
    *ffta_owned_exposed(unit)|=1;
    return 1;
}

/* Lifecycle-only layer. These entry points neither enable Fell Cleave nor
 * guess an owner for a foreign unit. Evaluation containers are independent. */
void ffta_exposed_clear(uint8_t *unit) {
    uint8_t *state=ffta_owned_exposed(unit);
    if(state)*state&=(uint8_t)~1u;
}
/* Composition point for the separately owned Centered layer. Missing weak
 * handler is deliberately inert in isolated Exposed builds. Each handler owns
 * its mask; event6 is broad remedy and must not erase beneficial Centered. */
extern void ffta_centered_event(uint8_t *,unsigned) __attribute__((weak));
void ffta_exposed_expire(uint8_t *unit,unsigned event) {
    ffta_exposed_clear(unit);
    if(ffta_centered_event)ffta_centered_event(unit,event);
}
void ffta_exposed_battle_end(void) {
    for(unsigned i=0;i<24;i++)ffta_exposed_expire((uint8_t *)(0x02000080u+264u*i),4);
    for(unsigned i=0;i<12;i++)ffta_exposed_expire((uint8_t *)(0x02002fc4u+264u*i),4);
}
void ffta_exposed_job_change(uint8_t *unit,unsigned job) {
    if(unit && unit[7]!=(uint8_t)job)ffta_exposed_expire(unit,5);
}
void ffta_exposed_native_status(uint8_t *unit,unsigned status,unsigned value) {
    /* Native CD92C reads E8 bit6; CDDD0 and CD884 write this Petrify bit. */
    if((uint16_t)status==6 && (uint8_t)value)ffta_exposed_expire(unit,3);
}
uint8_t *ffta_exposed_cureall(uint8_t *context) {
    /* Native broad-remedy effect11 (Esuna family) and79 (Cureall) use no-op
     * callbacks. The dispatcher removes original ailments separately. Bit10 is
     * the native query-only guard used by the neighboring effect handlers. */
    if(context && !(context[0x26]&0x10))
        ffta_exposed_expire(*(uint8_t **)(context+8),6);
    return context;
}
