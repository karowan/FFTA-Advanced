#include "battle-state.h"
#include "persistent.h"

uint8_t *ffta_state_exposed(uint8_t *state,const uint8_t *unit) {
    if (!state || !unit || ffta_storage_format(state)!=1) return 0;
    uintptr_t relative=(uintptr_t)unit-(uintptr_t)state;
    uintptr_t delta=relative-0x80u;
    if (delta<24u*264u && delta%264u==0)
        return state+FFTA_EXPOSED_OFFSET+delta/264u;
    delta=relative-0x2fc4u;
    if (delta<12u*264u && delta%264u==0)
        return state+FFTA_EXPOSED_OFFSET+24u+delta/264u;
    return 0;
}
void ffta_state_exposed_swap(uint8_t *state,unsigned a,unsigned b) {
    if (a>=24 || b>=24 || ffta_storage_format(state)!=1) return;
    uint8_t value=state[FFTA_EXPOSED_OFFSET+a];
    state[FFTA_EXPOSED_OFFSET+a]=state[FFTA_EXPOSED_OFFSET+b];
    state[FFTA_EXPOSED_OFFSET+b]=value;
}
void ffta_state_exposed_clear(uint8_t *state,const uint8_t *unit) {
    uint8_t *owned=ffta_state_exposed(state,unit);
    if (owned) *owned=0;
}
