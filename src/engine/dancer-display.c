#include <stdint.h>
static const uint32_t rows[3][16]={
 {0,0x00111100,0x00166100,0x00100100,0x00100100,0x00100100,0x01100100,0x16600100,0x16611110,0x01166610,0x00011110,0,0,0,0,0},
 {0,0x00111000,0x01666100,0x16666610,0x01666100,0x00161000,0x00161000,0x00111110,0x00166610,0x00111110,0,0,0,0,0,0},
 {0,0x01000100,0x01601610,0x01666610,0x00166100,0x01666610,0x01611610,0x01100110,0,0,0,0,0,0,0,0}
};
static const uint16_t shape[]={1,0x80f8,0x01fc,0};
unsigned ffta_dancer_status_visual(uint8_t *sprite,unsigned icon){
 if(!sprite||icon<36||icon>38)return 0;
 unsigned index=icon-36;volatile uint32_t *tiles=(volatile uint32_t *)(0x06013ec0u+64u*index);
 for(unsigned i=0;i<16;i++)tiles[i]=rows[index][i];
 *(const uint16_t **)(sprite+0x28)=shape;return 0x1f6u+2u*index;
}
