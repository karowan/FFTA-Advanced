#include <stdint.h>
#include "art-equipment-payload.h"

/* Equipment IDs overlap quest icon IDs. Keep the established caller gate;
 * the generated axe is never substituted into the generic quest namespace. */
unsigned ffta_art_equipment_draw(void *destination,unsigned id,unsigned caller,const uint8_t *shop) {
    unsigned call=(caller&~1u)-4u,owned=0;
    id&=65535u;
    if((id>=392u && id<=399u) || id==448u || (id>=453u && id<=460u)) {
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
        return ((Decode)0x08005319u)(ffta_art_axe_container,destination,0,1);
    }
    typedef unsigned (*Original)(void *,unsigned,unsigned,const uint8_t *);
    return ((Original)FFTA_ORIGINAL_EQUIPMENT_DRAW)(destination,id,caller,shop);
}
