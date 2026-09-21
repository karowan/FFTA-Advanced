#include <stdint.h>
#include "samurai-state.h"

extern unsigned ffta_primary_weapon(const uint8_t *);
extern void ffta_original_centered_equipment(uint8_t *,unsigned,unsigned);
extern void ffta_original_centered_equipment_quiet(uint8_t *,unsigned,unsigned);

/* Compare the completed native transaction, including native teaching/AP and
 * inventory updates. An armor/offhand edit that preserves the ordered primary
 * is not a stance break. Explicit evaluated owners retain private state. */
void ffta_centered_equipment(uint8_t *unit,unsigned item,unsigned slot) {
    unsigned before=ffta_primary_weapon(unit);
    ffta_original_centered_equipment(unit,item,slot);
    if(before!=ffta_primary_weapon(unit))ffta_centered_event(unit,8);
}
void ffta_centered_equipment_quiet(uint8_t *unit,unsigned item,unsigned slot) {
    unsigned before=ffta_primary_weapon(unit);
    ffta_original_centered_equipment_quiet(unit,item,slot);
    if(before!=ffta_primary_weapon(unit))ffta_centered_event(unit,8);
}

/* Native Dispel's effect53 callback is empty; the common dispatcher owns all
 * original status masks. Preserve its query guard and explicit recipient. */
uint8_t *ffta_centered_dispel(uint8_t *context) {
    if(context && !(context[0x26]&0x10))
        ffta_centered_event(*(uint8_t **)(context+8),7);
    return context;
}
