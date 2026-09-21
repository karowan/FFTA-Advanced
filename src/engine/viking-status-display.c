#include <stdint.h>
#include "viking-state.h"
extern unsigned ffta_previous_viking_status_icon(const uint8_t *,unsigned);
extern unsigned ffta_previous_viking_status_next_key(const uint8_t *,unsigned);
extern unsigned ffta_previous_viking_status_visual(uint8_t *,unsigned);
unsigned ffta_viking_status_icon(const uint8_t *unit,unsigned key) {
    key=(uint16_t)key;
    if(key==31)return ffta_viking_war_cry(unit)?31:0;
    if(key==32)return ffta_viking_challenger(unit)?32:0;
    return ffta_previous_viking_status_icon(unit,key);
}
unsigned ffta_viking_status_next_key(const uint8_t *unit,unsigned previous) {
    unsigned limit=ffta_viking_challenger(unit)?32:(ffta_viking_war_cry(unit)?31:0);
    if(!limit)return ffta_previous_viking_status_next_key(unit,previous);
    unsigned next=(uint8_t)(previous+1);
    return (int8_t)next>(int)limit?1:next;
}
/* War Cry: a horn and sound waves. Challenged: crossed axes. Native status
 * palette, transparent zero; separate two-tile glyphs reserved by root. */
static const uint32_t rows[2][16]={
 {0,0x00100000,0x01310000,0x13610000,0x13611000,0x13613610,0x13613661,0x13613610,
  0x13611000,0x13610000,0x01310000,0x00100000,0x00000000,0,0,0},
 {0,0x01100110,0x13611631,0x13611631,0x01166110,0x00166100,0x00066000,0x00066000,
  0x00166100,0x01611610,0x16100161,0x11000011,0,0,0,0}
};
static const uint16_t shape[]={1,0x80f8,0x01fc,0};
unsigned ffta_viking_status_visual(uint8_t *sprite,unsigned icon) {
    if(icon!=31 && icon!=32)return ffta_previous_viking_status_visual(sprite,icon);
    unsigned index=icon-31;
    volatile uint32_t *tiles=(volatile uint32_t *)(0x06013d80u+64u*index);
    for(unsigned i=0;i<16;i++)tiles[i]=rows[index][i];
    *(const uint16_t **)(sprite+0x28)=shape;
    return 0x1ecu+2u*index;
}
