#include "mystic-knight.h"
#include "registry.h"

extern unsigned ffta_primary_weapon(const uint8_t *);
unsigned ffta_myk_visual_item(const uint8_t *result){
 unsigned action=result[0x10]|((unsigned)result[0x11]<<8);
 if(action==FFTA_MYK_A12){
  const uint8_t *wrapper=*(const uint8_t *const *)result;
  const uint8_t *unit=wrapper?*(const uint8_t *const *)wrapper:0;
  return unit?ffta_primary_weapon(unit):0;
 }
 return result[0x12]|((unsigned)result[0x13]<<8);
}

/* Native status cycling, not a new saved status. Eleven blade monograms and
 * M+/P+ identify the next eligible Spellweave damage category. Their tiles
 * precede the relocated native dynamic pool; no native graphic is reused. */
unsigned ffta_myk_status_icon(const uint8_t *u,unsigned key){
 if(key>=43 && key<=53)return ffta_myk_enchantment(u)==key-42?key:0;
 unsigned sequence=ffta_myk_sequence(u);
 return (key==54 && sequence==1) || (key==55 && sequence==2)?key:0;
}
static const char labels[13][2]={
 {'F','I'},{'I','C'},{'T','H'},{'P','O'},{'S','L'},{'S','I'},
 {'D','R'},{'F','L'},{'S','W'},{'O','S'},{'H','O'},{'M','+'},{'P','+'}
};
static const char letters[]="CDFHILMOPRSTW+";
static const uint8_t glyphs[][5]={
 {15,16,16,16,15},{30,17,17,17,30},{31,16,30,16,16},
 {17,17,31,17,17},{31,4,4,4,31},{16,16,16,16,31},
 {17,27,21,17,17},{14,17,17,17,14},{30,17,30,16,16},
 {30,17,30,18,17},{15,16,14,1,30},{31,4,4,4,4},
 {17,17,21,27,17},{0,4,14,4,0}
};
static unsigned mask(char c,unsigned row){
 if(row>=5)return 0;
 for(unsigned i=0;i<sizeof(letters)-1;i++)if(letters[i]==c)return glyphs[i][row]<<1;
 return 0;
}
static const uint16_t shape[]={1,0x80f8,0x01fc,0};
unsigned ffta_myk_status_visual(uint8_t *sprite,unsigned icon){
 if(!sprite || icon<43 || icon>55)return 0;
 unsigned index=icon-43;
 volatile uint32_t *tiles=(volatile uint32_t *)(0x06014080u+64u*index);
 for(unsigned y=0;y<16;y++){
  char c=labels[index][y/8];unsigned row=y%8;
  unsigned ink=mask(c,row-1),edge=ink|(ink<<1)|(ink>>1)|mask(c,row-2)|mask(c,row);
  unsigned pixels=0;
  for(unsigned x=0;x<8;x++)pixels|=((ink&(1u<<(7-x)))?6u:(edge&(1u<<(7-x)))?1u:0u)<<(4*x);
  tiles[y]=pixels;
 }
 *(const uint16_t **)(sprite+0x28)=shape;return 0x204u+2u*index;
}
