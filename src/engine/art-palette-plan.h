#ifndef FFTA_ART_PALETTE_PLAN_H
#define FFTA_ART_PALETTE_PLAN_H
#include <stdint.h>
#include "art-palette-limits.h"
typedef struct {
 uint16_t occupied;
 FFTA_ArtSlotMask requested;
 uint8_t bank[FFTA_ART_HISTORY_SLOTS];
 uint16_t reserved;
} FFTA_ArtPalettePlan;
typedef struct {
 uint16_t *oam;                 /* Complete128-entry native OAM frame. */
 const uint8_t *obj;            /* Complete32KiB OBJ tile memory, word aligned. */
 const uint8_t *owner;          /*128 tags:0..9 authenticated custom owner,255 other. */
 uint16_t *palette;             /*256 native OBJ colors, before any overlay. */
 const uint16_t *custom;        /*custom_count contiguous16-color palettes. */
 FFTA_ArtPalettePlan *plan;
 unsigned one_dimensional,custom_count;
} FFTA_ArtPaletteFrame;
/* Current composition only. Requested starts as class bits during ownership,
 * then becomes authenticated history bits before palette planning. */
typedef struct {
 unsigned occupied,requested,count;
 uint8_t indices[128];
} FFTA_ArtOamDemands;
/* Exact-byte cache for the first32 visible tiles of an8bpp object. Entries
 * may survive position/layout changes because every complete tile is compared
 * before reuse. No coordinate key, hash or stale-frame assumption is used. */
typedef struct {
 uint32_t pixels[512];
 uint16_t masks[32], reserved[4];
 uint32_t valid;
} FFTA_ArtPaletteCache;
/* Pure frame planning/application. Caller must authenticate owner tags and
 * supply fresh native OAM/palettes. No native hook/lifetime is implied here. */
unsigned ffta_art_palette_plan(const FFTA_ArtPaletteFrame *frame);
unsigned ffta_art_palette_apply(FFTA_ArtPaletteFrame *frame);
unsigned ffta_art_palette_apply_cached(FFTA_ArtPaletteFrame *frame, FFTA_ArtPaletteCache *cache);
/* Optional single-owner preferred-bank path. Validate all current unowned
 * consumers before writes. Zero means the caller must run the full planner.
 * occupied remains the last full-plan diagnostic, not a freshly computed mask. */
unsigned ffta_art_palette_reapply(FFTA_ArtPaletteFrame *frame);
/* Back up only validated allocated banks before applying the current frame. */
unsigned ffta_art_palette_live_apply(FFTA_ArtPaletteFrame *frame,
                                    FFTA_ArtPaletteCache *cache, uint16_t *backup);
#endif
