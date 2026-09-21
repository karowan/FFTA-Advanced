#ifndef FFTA_ART_PALETTE_PROVISIONAL_H
#define FFTA_ART_PALETTE_PROVISIONAL_H
#include "art-palette-variants.h"
void ffta_art_provisional_confirm(const FFTA_ArtVariants *,uint8_t *,unsigned);
void ffta_art_provisional_reconcile(FFTA_ArtVariants *,FFTA_ArtBindings *,uint8_t *,
    unsigned,unsigned,const uint16_t *);
#endif
