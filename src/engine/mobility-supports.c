#include <stdint.h>
#include "registry.h"

extern int ffta_original_move(const uint8_t *unit);

int ffta_move_with_support(const uint8_t *unit) {
    int movement=ffta_original_move(unit);
    unsigned support=((unsigned (*)(const uint8_t *))0x080cd50du)(unit);
    /* This getter feeds both displayed movement and the native path budget.
     * Occupancy, movement mode, height and action availability remain native.
     * Preserve the native signed-byte result domain at its upper boundary. */
    if(support==FFTA_DNC_S2 && movement<127)++movement;
    return movement;
}

int ffta_grace_evade_divisor(int divisor,const uint8_t *unit) {
    unsigned support=((unsigned (*)(const uint8_t *))0x080cd50du)(unit);
    /* Native A-type accuracy divides Evade by1/2/2/4 for front/side/rear.
     * Keep frontal Evade only; later status/accuracy modifiers remain native.
     * The independent SRes path never calls this multiplier. */
    return support==FFTA_DNC_S1 ? 1 : divisor;
}
