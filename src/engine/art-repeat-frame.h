#ifndef FFTA_ART_REPEAT_FRAME_H
#define FFTA_ART_REPEAT_FRAME_H
#include "art-palette-plan.h"
#include "art-palette-variants.h"
/* Caller freshly authenticates ownership before every lookup. Current palette-
 * relevant OAM, class/bank identities, history mapping, plan and every8bpp
 * source byte must match. Position/tile changes of4bpp bodies do not affect
 * allocation. Borrow the exact pixel cache without overwriting its keys. */
typedef struct {
    uint32_t valid,hits,misses;
    uint32_t ab[128];
    uint16_t c[128];
    FFTA_ArtVariants variants;
    FFTA_ArtPalettePlan plan;
    uint16_t tiles[32];
    uint32_t count,mode,highlight;
} FFTA_ArtRepeat;
void ffta_art_repeat_begin(FFTA_ArtRepeat *,const FFTA_ArtPaletteFrame *);
void ffta_art_repeat_finish(FFTA_ArtRepeat *,const FFTA_ArtPaletteFrame *,
                          const FFTA_ArtPaletteCache *,const FFTA_ArtVariants *,unsigned);
unsigned ffta_art_repeat_hit(FFTA_ArtRepeat *,const FFTA_ArtPaletteFrame *,
                            const FFTA_ArtPaletteCache *,const FFTA_ArtVariants *,unsigned);
#endif
