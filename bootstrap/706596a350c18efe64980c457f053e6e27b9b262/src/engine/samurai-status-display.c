#include <stdint.h>
#include "blade-wound.h"

extern unsigned ffta_status_icon(const uint8_t *,unsigned);
extern unsigned ffta_status_next_key(const uint8_t *,unsigned);
extern unsigned ffta_status_visual(uint8_t *,unsigned);

unsigned ffta_wound_status_icon(const uint8_t *unit,unsigned key) {
    key=(uint16_t)key;
    if(key==27)return ffta_wound_record_remaining(ffta_owned_wound((uint8_t *)unit))?27:0;
    return ffta_status_icon(unit,key);
}
unsigned ffta_wound_status_next_key(const uint8_t *unit,unsigned previous) {
    if(!ffta_wound_status_icon(unit,27))return ffta_status_next_key(unit,previous);
    unsigned next=(uint8_t)(previous+1);
    return (int8_t)next>27?1:next;
}
/* Three distinct diagonal cuts. Nibbles are native status-palette indices;
 * zero is transparent. Two dedicated8x8 OBJ tiles form one8x16 glyph. */
static const uint32_t wound_rows[16]={
    0x00000000,0x00000110,0x00001361,0x00013610,
    0x00136110,0x01361361,0x13613610,0x16136110,
    0x01361361,0x13613610,0x16136100,0x01361000,
    0x13610000,0x16100000,0x01000000,0x00000000
};
static const uint16_t wound_shape[]={1,0x80f8,0x01fc,0};
unsigned ffta_wound_status_visual(uint8_t *sprite,unsigned icon) {
    if(icon!=27)return ffta_status_visual(sprite,icon);
    volatile uint32_t *tiles=(volatile uint32_t *)0x06013c80u;
    for(unsigned i=0;i<16;++i)tiles[i]=wound_rows[i];
    *(const uint16_t **)(sprite+0x28)=wound_shape;
    return 0x1e4;
}
