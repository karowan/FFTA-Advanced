#ifndef FFTA_ART_PALETTE_DIRTY_H
#define FFTA_ART_PALETTE_DIRTY_H
#include "art-palette-plan.h"
/* Private writer-tracking experiment. Cache storage replaces, not extends,
 * the existing tile pixels. Generic planner callers retain exact-byte caching. */
#define FFTA_ART_DIRTY_MAGIC 0x44545931u
#define FFTA_ART_DIRTY_CACHE(c) ((c)->reserved[0]==0x4454 && (c)->reserved[1]==0x5931)
void ffta_art_dirty_begin(FFTA_ArtPaletteCache *cache);
void ffta_art_dirty_write(FFTA_ArtPaletteCache *cache,unsigned destination,unsigned bytes);
void ffta_art_dirty_dma(FFTA_ArtPaletteCache *cache,unsigned destination,unsigned control);
unsigned ffta_art_dirty_mask(FFTA_ArtPaletteCache *cache,const uint32_t *pixels,unsigned tile);
#endif
