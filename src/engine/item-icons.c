#include <stdint.h>
#include "item-icons-payload.h"
/* Distinct 16x16 inventory icons for the 85 expansion weapons (IDs 376..460),
 * approved in src/art/imagegen/new-item-icons-approved.json. Equipment and
 * quest-item IDs overlap, so only the established equipment draw callers and
 * the shared shop in mode 4 (the gate in art-equipment-icons.c) use them;
 * every other caller and ID keeps the previous draw. The palette selector is
 * unchanged: each icon was drawn in its family donor's native palette bank,
 * which native code already selects for these IDs. */
typedef unsigned (*Draw)(void *,unsigned,unsigned,const uint8_t *);
unsigned ffta_item_icon_draw(void *destination,unsigned id,unsigned caller,const uint8_t *shop) {
    unsigned call=(caller&~1u)-4u,owned=0;
    id&=65535u;
    if(id>=376u && id<=460u) {
        switch(call) {
        case 0x0808168a: case 0x0807031c: case 0x080749e8:
        case 0x0808e3f2: case 0x0806e6a4: case 0x080d6614:
            owned=1;break;
        case 0x0806796e:
            owned=(uintptr_t)shop>=0x02000000u && (uintptr_t)shop<0x0203fff7u && shop[8]==4;
            break;
        default:break;
        }
    }
    if(owned) {
        typedef unsigned (*Decode)(const void *,void *,unsigned,unsigned);
        return ((Decode)0x08005319u)(ffta_item_icon_container,destination,id-376u,1);
    }
    return ((Draw)FFTA_PREVIOUS_EQUIPMENT_DRAW)(destination,id,caller,shop);
}
