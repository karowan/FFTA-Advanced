#include <stdint.h>
#include "dark-knight-state.h"
extern unsigned ffta_drk_previous_status_icon(const uint8_t *,unsigned);
extern unsigned ffta_drk_previous_status_next_key(const uint8_t *,unsigned);
extern unsigned ffta_drk_previous_status_visual(uint8_t *,unsigned);
unsigned ffta_drk_status_icon(const uint8_t *unit,unsigned key) {
    key=(uint16_t)key;
    if(key==28)return ffta_drk_last_resort(unit)?28:0;
    if(key==29)return ffta_drk_tbn(unit)?29:0;
    return ffta_drk_previous_status_icon(unit,key);
}
unsigned ffta_drk_status_next_key(const uint8_t *unit,unsigned previous) {
    unsigned limit=ffta_drk_tbn(unit)?29:ffta_drk_last_resort(unit)?28:0;
    if(!limit)return ffta_drk_previous_status_next_key(unit,previous);
    unsigned next=(uint8_t)(previous+1);
    return (int8_t)next>(int)limit?1:next;
}
static const uint32_t rows[2][16]={
 {0,0x00011000,0x00066100,0x00066100,0x00066100,0x00066100,0x00066100,0x00066100,
  0x01666610,0x00166100,0x00011000,0x00066000,0x00166100,0x00011000,0,0},
 {0,0x00111100,0x01366310,0x13666631,0x13611631,0x13611631,0x13611631,0x13611631,
  0x13611631,0x13666631,0x01366310,0x00166100,0x00011000,0,0,0}
};
static const uint16_t shape[]={1,0x80f8,0x01fc,0};
unsigned ffta_drk_status_visual(uint8_t *sprite,unsigned icon) {
    if(icon!=28 && icon!=29)return ffta_drk_previous_status_visual(sprite,icon);
    unsigned index=icon-28,tile=0x1e6u+2u*index;
    volatile uint32_t *tiles=(volatile uint32_t *)(0x06010000u+tile*32u);
    for(unsigned i=0;i<16;++i)tiles[i]=rows[index][i];
    *(const uint16_t **)(sprite+0x28)=shape;return tile;
}
