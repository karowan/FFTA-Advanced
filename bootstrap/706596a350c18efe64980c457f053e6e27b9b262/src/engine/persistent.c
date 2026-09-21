#include <stdint.h>
#include "registry.h"
#include "battle-state.h"
#include "blade-wound.h"

/* All offsets are relative to a native state block. Save previews use a
 * staging block, so the persistence code must not assume live EWRAM. */
#define INVENTORY 0x1940u
#define INVENTORY_BYTES 0x5dcu
#define EXTRA_AP 0x1b40u
#define METADATA 0x1e70u
#define UNIT_START 0x80u
#define UNIT_SIZE 0x108u
#define UNIT_COUNT 24u

static const uint8_t format_magic[8] = {'F','F','T','A','E','X','P','1'};

int ffta_storage_format(const uint8_t *state) {
    for (unsigned i=0; i<8; ++i)
        if (state[METADATA+i] != format_magic[i]) return 0;
    return state[METADATA+8] == 1 ? 1 : -1;
}

/* Return 1 after migration, 0 if already current, negative on invalid input.
 * Validate before writing; a failure never partially converts a save. */
int ffta_migrate_inventory(uint8_t *state) {
    int format=ffta_storage_format(state);
    if (format) return format==1 ? 0 : -2;
    uint8_t counts[512] = {0};
    uint8_t seen[48] = {0};
    for (unsigned n=0; n<375; ++n) {
        const uint8_t *entry=state+INVENTORY+n*4;
        unsigned id=entry[0] | ((unsigned)entry[1]<<8);
        if (!id) continue;
        if (id>375 || entry[2]>99 || entry[3]>entry[2]) return -1;
        /* Valid native inventories have one record per item. Do not silently
         * merge ambiguous or damaged saves and hide a corruption problem. */
        if (seen[id>>3] & (1u<<(id&7))) return -1;
        seen[id>>3] |= (uint8_t)(1u<<(id&7));
        counts[id]=entry[2];
    }
    for (unsigned i=0; i<INVENTORY_BYTES; ++i) state[INVENTORY+i]=0;
    for (unsigned i=0; i<512; ++i) state[INVENTORY+i]=counts[i];
    for (unsigned i=0; i<8; ++i) state[METADATA+i]=format_magic[i];
    state[METADATA+8]=1;
    return 1;
}

unsigned ffta_owned(const uint8_t *state, unsigned id) {
    id=(uint16_t)id;
    return id && id<=FFTA_MAX_ITEM ? state[INVENTORY+id] : 0;
}

/* Same ordinary-call contract as CA900, with well-defined saturation even
 * for large quantities. There is no wraparound above 255 or negative overflow. */
int ffta_give_item(uint8_t *state, unsigned id, unsigned amount) {
    id=(uint16_t)id;
    amount=(uint8_t)amount;
    if (!id || id>FFTA_MAX_ITEM || !amount) return -1;
    unsigned total=state[INVENTORY+id]+amount;
    state[INVENTORY+id]=(uint8_t)(total>99 ? 99 : total);
    return total>99 ? (int)(total-99) : 0;
}

int ffta_lose_item(uint8_t *state, unsigned id, unsigned amount) {
    id=(uint16_t)id;
    amount=(uint8_t)amount;
    if (!amount) return 0;
    if (!id || id>FFTA_MAX_ITEM) return -1;
    unsigned owned=state[INVENTORY+id];
    state[INVENTORY+id]=(uint8_t)(amount>=owned ? 0 : owned-amount);
    return 0;
}

/* A single caller validates all ingredients before committing a recipe. This
 * also handles repeated ingredient IDs without spending an unavailable copy.
 * Count refers to entries, not distinct IDs. Equipped copies are excluded by
 * passing the independently counted equipped quantities for each entry. */
int ffta_pay_recipe(uint8_t *state, const uint16_t *ids,
                    const uint8_t *amounts, const uint8_t *equipped, unsigned count) {
    if (!count || count>8) return 0;
    for (unsigned i=0; i<count; ++i) {
        if (ids[i]<362 || ids[i]>375 || !amounts[i]) return 0;
        unsigned required=0;
        for (unsigned j=0; j<count; ++j)
            if (ids[i]==ids[j]) required+=amounts[j];
        unsigned owned=state[INVENTORY+ids[i]];
        if (owned<equipped[i] || owned-equipped[i]<required) return 0;
    }
    for (unsigned i=0; i<count; ++i) state[INVENTORY+ids[i]]-=amounts[i];
    return 1;
}

uint8_t *ffta_party_ap_address(uint8_t *state, uint8_t *unit, unsigned index) {
    static const uint8_t counts[6]={0,178,111,124,118,116};
    uintptr_t relative=(uintptr_t)unit-(uintptr_t)(state+UNIT_START);
    if (relative>=UNIT_SIZE*UNIT_COUNT || relative%UNIT_SIZE) return 0;
    unsigned race=unit[6];
    if (!race || race>5 || !index || index>=counts[race]) return 0;
    if (race==1 && index>=142) {
        if (index<FFTA_HUMAN_AP_FIRST) return 0;
        unsigned slot=relative/UNIT_SIZE;
        return state+EXTRA_AP+slot*FFTA_HUMAN_AP_COUNT+index-FFTA_HUMAN_AP_FIRST;
    }
    return unit+0x40+index;
}

int ffta_swap_extra(uint8_t *state, unsigned a, unsigned b) {
    if (a>=UNIT_COUNT || b>=UNIT_COUNT) return 0;
    for (unsigned i=0; i<FFTA_HUMAN_AP_COUNT; ++i) {
        uint8_t *left=state+EXTRA_AP+a*FFTA_HUMAN_AP_COUNT+i;
        uint8_t *right=state+EXTRA_AP+b*FFTA_HUMAN_AP_COUNT+i;
        uint8_t temporary=*left;
        *left=*right;
        *right=temporary;
    }
    /* Per-unit Auto-Potion preference lives after the format header. */
    uint8_t choice=state[METADATA+16+a];
    state[METADATA+16+a]=state[METADATA+16+b];
    state[METADATA+16+b]=choice;
    ffta_state_exposed_swap(state,a,b);
    ffta_state_wound_swap(state,a,b);
    return 1;
}

int ffta_clear_extra(uint8_t *state, unsigned slot) {
    if (slot>=UNIT_COUNT) return 0;
    for (unsigned i=0; i<FFTA_HUMAN_AP_COUNT; ++i)
        state[EXTRA_AP+slot*FFTA_HUMAN_AP_COUNT+i]=0;
    state[METADATA+16+slot]=0;
    ffta_state_exposed_clear(state,state+UNIT_START+slot*UNIT_SIZE);
    ffta_state_wound_clear(state,state+UNIT_START+slot*UNIT_SIZE);
    return 1;
}

/* The native clear dispatcher is shared by constructors and roster removal.
 * Exact whole roster records clear AP/preferences. Exposed additionally tracks
 * whole enemy records inside bulk resets; partial unit fields preserve it. */
void ffta_on_unit_clear(uint8_t *destination,unsigned count) {
    extern void ffta_copy_owners_reset(void);
    extern void ffta_clear_copy_extra(uint8_t *);
    uintptr_t address=(uintptr_t)destination;
    if ((address==0x020159d0u || address==0x0201f550u || address==0x0200f3c4u) &&
        count==0x0203f800u-address) ffta_copy_owners_reset();
    /* Bulk enemy resets also own state. Only complete canonical records
     * contained by the cleared span qualify; partial fields never clear it. */
    uint8_t *live=(uint8_t *)0x02000000u;
    uintptr_t end=address+count;
    if (count>=UNIT_SIZE && end>=address &&
        ((address<0x02001940u && end>0x02000080u) ||
         (address<0x02003c24u && end>0x02002fc4u)) &&
        ffta_storage_format(live)==1) {
        for (unsigned i=0;i<36;++i) {
            uint8_t *unit=live+(i<24 ? 0x80u+i*264u : 0x2fc4u+(i-24)*264u);
            if (address<=(uintptr_t)unit && end>=(uintptr_t)unit+264u) {
                ffta_state_exposed_clear(live,unit);
                ffta_state_wound_clear(live,unit);
            }
        }
    }
    if (count!=UNIT_SIZE) return;
    ffta_clear_copy_extra(destination);
    uintptr_t relative=(uintptr_t)destination-0x02000080u;
    if (relative>=UNIT_SIZE*UNIT_COUNT || relative%UNIT_SIZE) return;
    uint8_t *state=(uint8_t *)0x02000000u;
    if (ffta_storage_format(state)==1) ffta_clear_extra(state,relative/UNIT_SIZE);
}
