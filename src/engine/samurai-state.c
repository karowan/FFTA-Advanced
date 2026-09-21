#include "samurai-state.h"
#include "battle-state.h"
#include "registry.h"

static unsigned centered_value(const uint8_t *unit) {
    uint8_t *owned=ffta_owned_exposed((uint8_t *)unit);
    return owned ? (*owned&FFTA_CENTERED_MASK)>>1 : 0;
}
static void centered_store(uint8_t *unit,unsigned value) {
    uint8_t *owned=ffta_owned_exposed(unit);
    if(owned)*owned=(uint8_t)((*owned&~FFTA_CENTERED_MASK)|((value<<1)&FFTA_CENTERED_MASK));
}
unsigned ffta_samurai_direct_action(unsigned action) {
    return action==FFTA_SAM_A1 || action==FFTA_SAM_A2 || action==FFTA_SAM_A3 ||
        action==FFTA_SAM_A6 || action==FFTA_SAM_A7 || action==FFTA_SAM_A8 || action==FFTA_SAM_A9;
}
unsigned ffta_centered_consuming_action(unsigned action) {
    /* All approved consuming Iaido are explicit. Kiyomori, Ashura and every
     * non-Iaido/counter effect stay outside this predicate. Defining the
     * predicate does not enable any action record or callback. */
    return action==FFTA_SAM_A2 || action==FFTA_SAM_A3 ||
        action==FFTA_SAM_A4 || action==FFTA_SAM_A6 ||
        action==FFTA_SAM_A7 || action==FFTA_SAM_A8 || action==FFTA_SAM_A9;
}
unsigned ffta_centered_active(const uint8_t *unit) {
    unsigned value=centered_value(unit);
    return (value&3u)!=0 && (value&3u)<=2;
}
unsigned ffta_centered_factor(const uint8_t *unit,unsigned action) {
    if(!ffta_centered_consuming_action(action))return 4;
    unsigned value=centered_value(unit);
    return (value==7 || ffta_centered_active(unit))?5:4;
}
void ffta_centered_grant(uint8_t *unit,unsigned application_is_own_turn) {
    centered_store(unit,2u|(application_is_own_turn?4u:0u));
}
void ffta_centered_clear(uint8_t *unit) { centered_store(unit,0); }
void ffta_centered_turn_end(uint8_t *unit) {
    unsigned value=centered_value(unit);
    if(value==7 || (value&3u)>2)centered_store(unit,0);
    else if(value&4u)centered_store(unit,value&3u);
    else if(value)centered_store(unit,value-1);
}
unsigned ffta_centered_paid(uint8_t *unit,unsigned action) {
    if(!ffta_centered_consuming_action(action)||!ffta_centered_active(unit))return 0;
    centered_store(unit,7);
    return 1;
}
void ffta_centered_retire(uint8_t *unit) {
    if(centered_value(unit)==7)centered_store(unit,0);
}
void ffta_centered_event(uint8_t *unit,unsigned event) {
    /* Shared explicit-unit lifecycle: KO/Petrify/battle end/job change,
     * Dispel and primary-weapon change. Start turn and broad harmful-status
     * remedies do not remove a T2 beneficial status. */
    if((event>=2 && event<=5)||event==7||event==8)ffta_centered_clear(unit);
}
