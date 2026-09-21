#include <stdint.h>
#include "persistent.h"

static const uint8_t original_counts[6]={0,142,77,95,85,88};
static const uint8_t expanded_counts[6]={0,178,111,124,118,116};
extern uint8_t *ffta_owned_extra_ap(uint8_t *,unsigned);
extern int ffta_native_give_item(unsigned,unsigned);
extern void ffta_quin_prepare(uint8_t *);
extern unsigned ffta_original_import_abilities(uint8_t *,const uint8_t *);

/* Publish only after the native template importer has finished its original
 * bitmap. C9ED8 must retain the original bounds: templates have no new bits. */
void ffta_publish_unit_count(uint8_t *unit) {
    if (!unit || !unit[4] || ffta_storage_format((uint8_t *)0x02000000u)!=1) return;
    unsigned race=unit[6];
    if (!race || race>5) return;
    if (race==1 && !ffta_owned_extra_ap(unit,144)) return;
    if (unit[0x34]==original_counts[race] || unit[0x34]==expanded_counts[race])
        unit[0x34]=expanded_counts[race];
}
void ffta_publish_roster_counts(uint8_t *state,unsigned first_conversion) {
    if (ffta_storage_format(state)!=1) return;
    for (unsigned slot=0;slot<24;++slot) {
        uint8_t *unit=state+0x80+264*slot;
        unsigned race=unit[6];
        if (!unit[4] || !race || race>5) continue;
        if (unit[0x34]!=original_counts[race] && unit[0x34]!=expanded_counts[race]) continue;
        /* Native saves did not own these nonhuman inline bytes as AP. Once
         * converted, preserve them even if an older prototype left old counts. */
        if (first_conversion && race!=1)
            for (unsigned i=original_counts[race];i<expanded_counts[race];++i) unit[0x40+i]=0;
        unit[0x34]=expanded_counts[race];
    }
}
int ffta_load_migrate_abilities(uint8_t *state) {
    unsigned first=ffta_storage_format(state)==0;
    int result=ffta_migrate_inventory(state);
    if (result>=0) { ffta_publish_roster_counts(state,first);ffta_quin_prepare(state); }
    return result;
}
int ffta_give_with_abilities(unsigned id,unsigned amount) {
    unsigned first=ffta_storage_format((uint8_t *)0x02000000u)==0;
    int result=ffta_native_give_item(id,amount);
    ffta_publish_roster_counts((uint8_t *)0x02000000u,first);
    ffta_quin_prepare((uint8_t *)0x02000000u);
    return result;
}
unsigned ffta_import_with_abilities(uint8_t *unit,const uint8_t *template) {
    unsigned result=ffta_original_import_abilities(unit,template);
    ffta_publish_unit_count(unit);
    return result;
}
