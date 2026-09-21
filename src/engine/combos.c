#include <stdint.h>
#include "registry.h"

extern unsigned ffta_primary_weapon(const uint8_t *unit);
extern unsigned ffta_original_combo_chance(const uint8_t *,const uint8_t *,unsigned);
extern unsigned ffta_original_combo_range(const uint8_t *);
extern unsigned ffta_original_combo_power(const uint8_t *);

/* Assigned slots contain racial lesson indices, not global combo IDs. Keep
 * the actual evaluated unit, including native simulation/selection copies. */
static unsigned custom_combo(const uint8_t *unit) {
    if (!unit || !unit[0x3c] || unit[6]>=24) return 0;
    typedef const uint8_t *(*Lesson)(unsigned,unsigned);
    const uint8_t *record=((Lesson)0x080cd481u)(unit[6],unit[0x3c]);
    unsigned id=record[4]|((unsigned)record[5]<<8);
    return record[6]==5 && id>=FFTA_SAM_C1 && id<=FFTA_MYK_C1 ? id : 0;
}

unsigned ffta_combo_permitted(const uint8_t *unit) {
    unsigned combo=custom_combo(unit);
    if (!combo) return 1;
    unsigned weapon=ffta_primary_weapon(unit);
    if (!weapon) return 0;
    unsigned category=((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(weapon,3);
    switch (combo) {
    case FFTA_SAM_C1: return category==9;
    case FFTA_DRK_C1: return category==1 || category==5 || category==6;
    case FFTA_VIK_C1: return category==31;
    case FFTA_GEO_C1: return category==11 || category==12;
    case FFTA_CHM_C1: return category==7 || category==12;
    case FFTA_BRD_C1: return category==16;
    case FFTA_DNC_C1: return category==7 || category==8;
    case FFTA_MYK_C1: return category==8 || category==3;
    default: return 0;
    }
}

unsigned ffta_combo_assigned(const uint8_t *unit) {
    return unit && ffta_combo_permitted(unit) ? unit[0x3c] : 0;
}
unsigned ffta_combo_chance(const uint8_t *unit,const uint8_t *target,unsigned mode) {
    if (!ffta_combo_permitted(unit)) return 0;
    return ffta_original_combo_chance(unit,target,mode);
}
unsigned ffta_combo_range(const uint8_t *unit) {
    if (!ffta_combo_permitted(unit)) return 0;
    return ffta_original_combo_range(unit);
}
unsigned ffta_combo_power(const uint8_t *unit) {
    if (!ffta_combo_permitted(unit)) return 0;
    return ffta_original_combo_power(unit);
}
