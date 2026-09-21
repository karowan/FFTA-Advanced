#ifndef FFTA_ART_PALETTE_BINDING_H
#define FFTA_ART_PALETTE_BINDING_H
#include "art-palette-fade.h"
#include "art-palette-limits.h"
typedef struct {
    FFTA_ArtFade fade;
    uint16_t native_base[16];
    uint32_t task, bank;
} FFTA_ArtBinding;
typedef struct {
    FFTA_ArtBinding entry[FFTA_ART_HISTORY_SLOTS];
    uint16_t colors[FFTA_ART_HISTORY_SLOTS*16];
    uint32_t started, completed, unsupported;
} FFTA_ArtBindings;

void ffta_art_bindings_reset(FFTA_ArtBindings *, const uint16_t *base);
void ffta_art_binding_observe(FFTA_ArtBindings *, unsigned owner, unsigned bank,
                              const uint16_t *native, const uint16_t *base);
void ffta_art_binding_observe_colors(FFTA_ArtBindings *, unsigned slot, unsigned bank,
                                     const uint16_t *native, const uint16_t colors[16]);
static inline uint16_t ffta_art_scale_color(uint16_t color, unsigned scale) {
    return (((color & 31u) * scale) >> 5) |
           (((((color >> 5) & 31u) * scale) >> 5) << 5) |
           (((((color >> 10) & 31u) * scale) >> 5) << 10);
}
void ffta_art_binding_invalidate(FFTA_ArtBindings *, unsigned first, unsigned last,
                                 uint32_t task, unsigned recognized);
/* kind 1 black, 2 white, 3 explicit native palette. Explicit targets must be
 * uniform or exactly match this owner's authenticated unfaded native bank. */
void ffta_art_binding_start(FFTA_ArtBindings *, unsigned first, unsigned last,
                            unsigned duration, uint32_t task, unsigned kind,
                            const uint16_t *native_target, const uint16_t *base);
/* Mapping is HISTORY_SLOTS (class*16+native_bank) keys followed by that many
 * RGB factors/32. Extra history slots need a mapping for source-table targets.
 * A null mapping retains the original class-indexed binding API. */
void ffta_art_binding_start_mapped(FFTA_ArtBindings *, unsigned first, unsigned last,
                            unsigned duration, uint32_t task, unsigned kind,
                            const uint16_t *native_target, const uint16_t *base,
                            const uint8_t *mapping);
void ffta_art_binding_tick(FFTA_ArtBindings *, uint32_t task, unsigned before,
                           unsigned after, unsigned alive, unsigned flags);
void ffta_art_binding_tick_range(FFTA_ArtBindings *,uint32_t task,unsigned before,
    unsigned after,unsigned alive,unsigned flags,unsigned first,unsigned last);
void ffta_art_binding_rotate(FFTA_ArtBindings *,unsigned first,unsigned last,
    unsigned right,unsigned steps,unsigned feed,unsigned value);
/* Native target operations:4 gray,5/6 RGB multipliers,7 solid,8 blend,
 *9 brighten,10 darken,11/12 exposure with native source-channel floor3.
 * Transform the current generated colors, including interrupted fades. */
void ffta_art_binding_transform(FFTA_ArtBindings *, unsigned first, unsigned last,
    unsigned duration, uint32_t task, unsigned kind, unsigned red, unsigned green,
    unsigned blue);
/*13 exposure and14 blend derive targets from a recognized source table.
 * Source table and current interpolation colors are never modified. */
void ffta_art_binding_table_transform(FFTA_ArtBindings *, unsigned first,unsigned last,
    unsigned duration,uint32_t task,unsigned kind,const uint16_t *table,
    unsigned red,unsigned green,unsigned blue,const uint16_t *base,const uint8_t *mapping);
#endif
