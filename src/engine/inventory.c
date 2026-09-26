#include "persistent.h"

#include "registry.h"

#define LIVE ((uint8_t *)0x02000000u)
/* Globally excluded from all three native heaps before their clear passes. */
#define VIEW ((struct InventoryEntry *)0x0203f800u)
#define EQUIPMENT_SLOTS (FFTA_MAX_ITEM-14u)

struct InventoryEntry { uint16_t id; uint8_t owned, equipped; };
_Static_assert(sizeof(struct InventoryEntry)==4,"Native inventory record layout");
/* One entry per item; the copy-owner root (unit-copies.c) starts at 0x0203FF30. */
_Static_assert(0x0203f800u+FFTA_MAX_ITEM*sizeof(struct InventoryEntry)<=0x0203ff30u,"inventory view below the copy-owner root");

static unsigned view_index(unsigned item) {
    return item<=361 ? item-1 : item<=375 ? EQUIPMENT_SLOTS+item-362 : item-15;
}

static void refresh_owned(unsigned id) {
    id=(uint16_t)id;
    if (id && id<=FFTA_MAX_ITEM) {
        /* Retained native list pointers observe grants/removal immediately.
         * Do not materialize an unused view: CB210 initializes it on demand. */
        struct InventoryEntry *entry=VIEW+view_index(id);
        if (entry->id==id) entry->owned=(uint8_t)ffta_owned(LIVE,id);
    }
}

unsigned ffta_equipped(const uint8_t *state, unsigned id) {
    id=(uint16_t)id;
    if (!id || id>FFTA_MAX_ITEM) return 0;
    unsigned count=0;
    for (unsigned slot=0; slot<24; ++slot) {
        const uint8_t *unit=state+0x80+slot*0x108;
        if (!unit[4]) continue;
        for (unsigned gear=0; gear<5; ++gear) {
            unsigned offset=0x2a+gear*2;
            unsigned worn=unit[offset] | ((unsigned)unit[offset+1]<<8);
            if (worn==id) ++count;
        }
    }
    return count;
}

unsigned ffta_free_count(const uint8_t *state, unsigned id) {
    unsigned owned=ffta_owned(state,id),equipped=ffta_equipped(state,id);
    return owned>equipped ? owned-equipped : 0;
}

/* A compatibility view for surviving native READERS of CB210. All surviving
 * writers must use count operations; returning this view alone is not a port.
 * It keeps native APIs and Item restrictions while adding equipment IDs. */
struct InventoryEntry *ffta_inventory_view(const uint8_t *state, unsigned id,
                                           unsigned *count, struct InventoryEntry *view) {
    uint8_t equipped[512]={0};
    for (unsigned slot=0; slot<24; ++slot) {
        const uint8_t *unit=state+0x80+slot*0x108;
        if (!unit[4]) continue;
        for (unsigned gear=0; gear<5; ++gear) {
            unsigned offset=0x2a+gear*2;
            unsigned item=unit[offset] | ((unsigned)unit[offset+1]<<8);
            if (item && item<=FFTA_MAX_ITEM) ++equipped[item];
        }
    }
    for (unsigned item=1; item<=FFTA_MAX_ITEM; ++item) {
        unsigned index=view_index(item);
        view[index].id=(uint16_t)item;
        view[index].owned=(uint8_t)ffta_owned(state,item);
        view[index].equipped=equipped[item];
    }
    id=(uint16_t)id;
    if (id>=362 && id<=375) {
        if (count) *count=14;
        return view+EQUIPMENT_SLOTS;
    }
    if (count) *count=EQUIPMENT_SLOTS;
    return view;
}

int ffta_native_give_item(unsigned id,unsigned amount) {
    /* Native new-game grants call this too, after the state block is cleared.
     * Migration is lazy there; successful gameplay loads have explicit hooks. */
    if (ffta_migrate_inventory(LIVE)<0) return -1;
    int result=ffta_give_item(LIVE,id,amount);
    refresh_owned(id);
    return result;
}
int ffta_native_lose_item(unsigned id,unsigned amount) {
    int result=ffta_lose_item(LIVE,id,amount);
    refresh_owned(id);
    return result;
}
unsigned ffta_native_owned(unsigned id) { return ffta_owned(LIVE,id); }
unsigned ffta_native_equipped(unsigned id) { return ffta_equipped(LIVE,id); }
unsigned ffta_native_free_count(unsigned id) { return ffta_free_count(LIVE,id); }
unsigned ffta_native_has_item(unsigned id) { return ffta_owned(LIVE,id)!=0; }
unsigned ffta_native_at_cap(unsigned id) { return ffta_owned(LIVE,id)==99; }
void ffta_native_equipment_event(unsigned id,unsigned equipping) {
    id=(uint16_t)id;
    if (!id || id>FFTA_MAX_ITEM) return;
    struct InventoryEntry *entry=VIEW+view_index(id);
    if (entry->id!=id) return;
    if ((uint8_t)equipping) {
        if (entry->equipped<entry->owned) ++entry->equipped;
    } else if (entry->equipped) --entry->equipped;
}

unsigned ffta_native_has_transferable(void) {
    for (unsigned id=1; id<=FFTA_MAX_ITEM; ++id) {
        if (id==0x33 || id==0x94 || id==0x11e || id==0x12e) continue;
        if (ffta_free_count(LIVE,id)) return 1;
    }
    return 0;
}
struct InventoryEntry *ffta_native_inventory(unsigned id,unsigned *count) {
    return ffta_inventory_view(LIVE,id,count,VIEW);
}

/* Item type, not the original numeric ID cutoff, decides new weapon status.
 * Type0x1f is the expansion's axe category. Original Souls are weapons too. */
unsigned ffta_native_is_weapon(unsigned id) {
    id=(uint16_t)id;
    if (!id || id>FFTA_MAX_ITEM) return 0;
    const uint8_t *table=*(const uint8_t * const *)0x08079aecu;
    unsigned type=table[id*32+8];
    return (type>=1 && type<=19) || type==31;
}
