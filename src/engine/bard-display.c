#include <stdint.h>
/* March: strong note; Inspired: paired notes. Each uses two reserved tiles
 * and the existing native status palette and renderer shape. */
static const uint32_t rows[3][16]={
 {0,0x00011100,0x00013610,0x00013610,0x00013610,0x00013610,0x00013610,0x01113610,
  0x13613610,0x13613610,0x01111100,0,0,0,0,0},
 {0,0x00111100,0x00166100,0x00100100,0x00100100,0x00100100,0x01101100,0x16616610,
  0x16616610,0x01101100,0,0,0,0,0,0},
 {0,0x00011000,0x00016100,0x00166100,0x01666110,0x16666610,0x01166100,0x00161000,
  0x00110000,0,0,0,0,0,0,0}
};
static const uint16_t shape[]={1,0x80f8,0x01fc,0};
unsigned ffta_bard_status_visual(uint8_t *sprite,unsigned icon){
    if(!sprite || icon<33 || icon>35)return 0;
    unsigned index=icon-33;volatile uint32_t *tiles=(volatile uint32_t *)(0x06013e00u+64u*index);
    for(unsigned i=0;i<16;i++)tiles[i]=rows[index][i];
    *(const uint16_t **)(sprite+0x28)=shape;return 0x1f0u+2u*index;
}
