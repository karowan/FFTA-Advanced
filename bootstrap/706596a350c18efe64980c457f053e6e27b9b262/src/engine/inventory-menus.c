#include <stdint.h>
#include "persistent.h"
#include "registry.h"
#include "stock.h"

#define LIVE ((uint8_t *)0x02000000u)
extern unsigned ffta_equipped(const uint8_t *,unsigned);
extern unsigned ffta_free_count(const uint8_t *,unsigned);

static uint8_t *item_data(unsigned id) {
    return *(uint8_t * const *)0x08079aecu+id*32;
}
static unsigned item_tab(unsigned id) {
    static const uint8_t tabs[33]={255,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
                                  3,0,0,0,1,1,1,4,4,4,5,2,255};
    if (!id || id>FFTA_MAX_ITEM) return 255;
    unsigned type=item_data(id)[8];
    return type<33 ? tabs[type] : 255;
}
static void put16(uint8_t *p,unsigned n) { p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8); }
static void put32(uint8_t *p,unsigned n) {
    put16(p,n);put16(p+2,n>>16);
}
static unsigned get16(const uint8_t *p) { return p[0] | ((unsigned)p[1]<<8); }

static void menu_header(uint8_t *destination,int equip) {
    put32(destination+4,*(uint32_t *)(equip?0x08079ad4u:0x0808ccc8u));
    destination[12]=0;destination[13]=0;
    destination[14]=(uint8_t)(equip?21:22);
    destination[15]=(uint8_t)(equip?13:11);
    put16(destination+16,0x229);put16(destination+18,0);
    put16(destination+20,0);put16(destination+22,16);
    put32(destination+24,(uintptr_t)(destination+0x230));
}

/* Full-width counts and expanded buffers avoid the native weapon-tab limit
 * of255 entries. Native grey/unusable entries remain visible. */
unsigned ffta_party_item_list(unsigned tab,uint8_t *destination) {
    unsigned count=0;
    menu_header(destination,0);
    for (unsigned id=1;id<=FFTA_MAX_ITEM;++id) {
        unsigned owned=ffta_owned(LIVE,id);
        if (!owned || item_tab(id)!=(uint16_t)tab) continue;
        uint8_t *entry=destination+0x230+count*20;
        for (unsigned n=0;n<20;++n)entry[n]=0;
        put16(entry,count);put32(entry+4,id);
        const uint8_t *data=item_data(id);
        put16(entry+8,get16(data));put16(entry+12,get16(data+2));
        entry[14]=(uint8_t)(tab==5?255:ffta_equipped(LIVE,id));
        entry[15]=(uint8_t)owned;
        put16(entry+18,id);
        ++count;
    }
    put32(destination,count);
    return count;
}

unsigned ffta_equip_item_list(unsigned tab,uint8_t *destination) {
    unsigned count=ffta_party_item_list(tab,destination);
    menu_header(destination,1);
    uint8_t *context=*(uint8_t **)0x03002818u;
    uint8_t *unit=*(uint8_t **)(context+0x1d0c);
    unsigned gear_slot=context[0xc1f];
    typedef unsigned (*CanEquip)(uint8_t *,unsigned,unsigned);
    for (unsigned n=0;n<count;++n) {
        uint8_t *entry=destination+0x230+n*20;
        unsigned id=get16(entry+4);
        unsigned forbidden=((CanEquip)0x080cb48du)(unit,id,gear_slot)&1;
        if (!ffta_free_count(LIVE,id))forbidden=1;
        put16(entry+2,forbidden);
    }
    if (!count && context[0xc1e]==tab)context[0xc1e]=255;
    return count;
}

static void stock_entry(uint8_t *entry,unsigned id) {
    put16(entry,id);
    entry[2]=(uint8_t)ffta_owned(LIVE,id);
    entry[3]=(uint8_t)ffta_equipped(LIVE,id);
}

/* Preserve both native ordinary stock and native appended special stock.
 * The new teaching-weapon stock is integrated separately with mission gates;
 * it must never inherit the native tier bits by accident. */
unsigned ffta_shop_buy_list(uint8_t *destination,unsigned tab,unsigned tier_key,unsigned special_key) {
    typedef unsigned (*OneArg)(unsigned);
    typedef unsigned (*TwoArgs)(unsigned,unsigned);
    typedef unsigned (*NoArgs)(void);
    unsigned tier=(uint8_t)((OneArg)0x080cc8b5u)((uint16_t)tier_key);
    unsigned mask=tier==0?16:tier==1?32:64;
    unsigned count=0;
    for (unsigned id=1;id<=375;++id) {
        if (!(item_data(id)[12]&mask) || item_tab(id)!=(uint8_t)tab)continue;
        stock_entry(destination+count*4,id);++count;
    }
    unsigned limit=(uint8_t)((NoArgs)0x080cecf5u)();
    for (unsigned i=0;i<=limit;++i) {
        unsigned id=(uint16_t)((TwoArgs)0x080cc9f1u)((uint8_t)special_key,(uint8_t)i);
        if (!id || id>375 || item_tab(id)!=(uint8_t)tab)continue;
        stock_entry(destination+count*4,id);++count;
    }
    // special_key is the native town identity (2 Cyril,3 Sprohm,4 Muscadet,
    // 5 Cadoan,6 Baguba Port). Completion flags persist independently of the
    // original battle/turf stock rules. Merely accepting a mission is not a
    // completion and cannot satisfy this separate additive pass.
    unsigned town=(uint8_t)special_key;
    if((uintptr_t)item_data(0)>=0x09000000u && tab==2 && town>=2 && town<=6)for(unsigned i=0;i<85;++i) {
        if(!(ffta_stock[i].towns&(1u<<town)))continue;
        unsigned flag=ffta_stock[i].flag;
        if(flag&&!((OneArg)0x080c9541u)(flag))continue;
        stock_entry(destination+count*4,ffta_stock[i].item);++count;
    }
    return count;
}

unsigned ffta_shop_sell_list(uint8_t *destination,unsigned tab) {
    unsigned count=0;
    for (unsigned id=1;id<=FFTA_MAX_ITEM;++id) {
        if (!ffta_owned(LIVE,id) || item_tab(id)!=(uint8_t)tab)continue;
        stock_entry(destination+count*4,id);++count;
    }
    return count;
}
