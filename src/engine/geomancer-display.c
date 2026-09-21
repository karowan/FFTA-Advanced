#include <stdint.h>
/* Four pairs precede the relocated dynamic pool. Updraft, Wisp and Steady
 * belong to recipients; the field cross belongs only to its caster. */
static const uint32_t rows[4][16]={
 {0,0x00011000,0x00166100,0x01666610,0x11166111,0x00066000,0x00066000,0x01111110,
  0x16666661,0x01111110,0,0,0,0,0,0},
 {0,0x00111100,0x00166100,0x00166100,0x11166111,0x16666661,0x16666661,0x11166111,
  0x00166100,0x00166100,0x00111100,0,0,0,0,0},
 {0,0x00010000,0x00161000,0x01666100,0x16666610,0x16336661,0x16333661,0x01633610,
  0x00166100,0x00011000,0x00066000,0x00011000,0,0,0,0},
 {0,0x01111110,0x16666661,0x11666611,0x01166110,0x00166100,0x00166100,0x00166100,
  0x01166110,0x16666661,0x11111111,0,0,0,0,0}
};
static const uint16_t shape[]={1,0x80f8,0x01fc,0};
unsigned ffta_geo_status_visual(uint8_t *sprite,unsigned icon){
 if(!sprite||icon<39||icon>42)return 0;
 unsigned index=icon-39;volatile uint32_t *tiles=(volatile uint32_t *)(0x06013f80u+64u*index);
 for(unsigned i=0;i<16;i++)tiles[i]=rows[index][i];
 *(const uint16_t **)(sprite+0x28)=shape;return 0x1fcu+2u*index;
}
