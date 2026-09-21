#include "chemist-state.h"
extern unsigned ffta_previous_status_icon(const uint8_t *,unsigned);
extern unsigned ffta_previous_status_next_key(const uint8_t *,unsigned);
extern unsigned ffta_previous_status_visual(uint8_t *,unsigned);
unsigned ffta_chemist_status_icon(const uint8_t *unit,unsigned key) {
 key=(uint16_t)key;
 if(key==30)return ffta_inoculated_active(unit)?30:0;
 if(key==28 || key==29)return 0; /* Reserved peer keys, not native aliases. */
 return ffta_previous_status_icon(unit,key);
}
unsigned ffta_chemist_status_next_key(const uint8_t *unit,unsigned previous) {
 if(!ffta_inoculated_active(unit))return ffta_previous_status_next_key(unit,previous);
 unsigned next=(uint8_t)(previous+1);return (int8_t)next>30?1:next;
}
/* Preventive medicine: a cross inside a shield, native palette indices.
 * Central allocation reserves exactly OBJ1EA..1EB for this8x16 glyph. */
static const uint32_t inoculated_rows[16]={
 0,0x00111100,0x01777710,0x17733771,0x17733771,0x17333371,
 0x17333371,0x17733771,0x17733771,0x01777710,0x00177100,
 0x00011000,0,0,0,0
};
static const uint16_t inoculated_shape[]={1,0x80f8,0x01fc,0};
unsigned ffta_chemist_status_visual(uint8_t *sprite,unsigned icon) {
 if(icon!=30)return ffta_previous_status_visual(sprite,icon);
 volatile uint32_t *tiles=(volatile uint32_t *)0x06013d40u;
 for(unsigned i=0;i<16;i++)tiles[i]=inoculated_rows[i];
 *(const uint16_t **)(sprite+0x28)=inoculated_shape;return 0x1ea;
}
unsigned ffta_chemist_beneficial(const uint8_t *unit) { return ffta_inoculated_active(unit); }
