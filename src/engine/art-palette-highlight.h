#ifndef FFTA_ART_PALETTE_HIGHLIGHT_H
#define FFTA_ART_PALETTE_HIGHLIGHT_H
#include "art-palette-variants.h"

/* Only B70F2's exact shared target-palette load establishes this ownership.
 * A bank number or a vaguely similar color is not sufficient evidence. */
static inline unsigned ffta_art_highlight_copy(unsigned caller,unsigned destination,
    unsigned source,unsigned count,const uint16_t *copied,const uint16_t *reference) {
    unsigned i;
    if(caller!=0x080b70f7u || destination!=0x03003b80u ||
       source!=0x03003c40u || count!=32)return 0;
    for(i=0;i<16;++i)if(copied[i]!=reference[i])return 0;
    return 1;
}

static inline unsigned ffta_art_highlight_retire(FFTA_ArtVariants *v,FFTA_ArtBindings *b) {
    unsigned slot,retired=0;
    for(slot=0;slot<FFTA_ART_HISTORY_SLOTS;++slot)if(v->key[slot]!=255 && (v->key[slot]&15)==9) {
        v->key[slot]=255;v->scale[slot]=0;
        b->entry[slot].bank=255;b->entry[slot].task=0;
        retired|=1u<<slot;
    }
    return retired;
}

static inline unsigned ffta_art_highlight_filter(uint8_t tags[128],
    const uint16_t *oam,uint16_t banks[10]) {
    unsigned i,requested=0;
    for(i=0;i<10;++i) {
        banks[i]&=~(1u<<9);
        if(banks[i])requested|=1u<<i;
    }
    for(i=0;i<128;++i)if(tags[i]!=255 && (oam[i*4+2]>>12)==9)tags[i]=255;
    return requested;
}
#endif
