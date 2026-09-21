#include <stdint.h>
#include "registry.h"
#include "icons.h"

/* Preserve native CABA8's first-invalid-hand-slot error convention. This
 * guard only adds the approved Axe exclusion; native layout validation still
 * owns every permission, support and armor rule. */
unsigned ffta_axe_layout_guard(const uint8_t *gear,unsigned invalid_slot) {
    unsigned hands=0,second=0,axe=0;
    const uint8_t *table=*(const uint8_t * const *)0x08079aecu;
    for(unsigned slot=0;slot<5;++slot) {
        unsigned id=gear[slot*2]|((unsigned)gear[slot*2+1]<<8);
        if(!id||id>FFTA_MAX_ITEM)continue;
        unsigned type=table[id*32+8];
        if(type==31)axe=1;
        if((type>=1&&type<=20)||type==31) {
            ++hands;
            if(hands==2)second=slot;
        }
    }
    if(axe&&hands>1)return 1u|(((invalid_slot&255u)==second)?128u:0u);
    return 0;
}

/* Equipment and quest-item IDs overlap. Remap only verified equipment
 * render callsites, never the generic icon namespace. */
static unsigned icon_id(unsigned id,unsigned return_address,const uint8_t *shop) {
    id&=65535u;
    if(id<376||id>FFTA_MAX_ITEM)return id;
    unsigned call=(return_address&~1u)-4u;
    unsigned equipment=0;
    switch(call) {
    case 0x0808160e: case 0x0808168a:
    case 0x0807031c: case 0x08070370: case 0x08070392:
    case 0x080749b0: case 0x080749e8:
    case 0x0808e3de: case 0x0808e3f2:
    case 0x0806e6a4: case 0x0806e81e:
    /* Thrown equipment projectile: D5FD8 palette and D65D4 tile decoder. */
    case 0x080d601a: case 0x080d6614:
    case 0x08067514:equipment=1;break;
    case 0x0806796e:
        equipment=(uintptr_t)shop>=0x02000000u && (uintptr_t)shop<0x0203fff7u && shop[8]==4;
        break;
    default:break;
    }
    return equipment?ffta_item_icon_donors[id-376]:id;
}

unsigned ffta_equipment_icon_draw(void *destination,unsigned id,unsigned return_address,const uint8_t *shop) {
    typedef unsigned (*Decode)(const void *,void *,unsigned,unsigned);
    return ((Decode)0x08005319u)((void *)0x083c83fcu,destination,icon_id(id,return_address,shop),1);
}
unsigned ffta_equipment_icon_palette(unsigned id,unsigned return_address,const uint8_t *shop) {
    const uint8_t *bank=(const uint8_t *)0x083c7fe4u;
    return bank[icon_id(id,return_address,shop)*2+4]>>4;
}
