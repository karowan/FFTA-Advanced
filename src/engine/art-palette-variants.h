#ifndef FFTA_ART_PALETTE_VARIANTS_H
#define FFTA_ART_PALETTE_VARIANTS_H
#include "art-palette-binding.h"
typedef struct {
    uint8_t key[FFTA_ART_HISTORY_SLOTS], scale[FFTA_ART_HISTORY_SLOTS];
} FFTA_ArtVariants;
void ffta_art_variants_reset(FFTA_ArtVariants *);
/* Before a supported effect starts, track authenticated palettes even if the
 * corresponding character has not yet emitted OAM. Never evicts history. */
void ffta_art_variants_track(FFTA_ArtVariants *, FFTA_ArtBindings *,
    const uint16_t *native, const uint16_t *reference, const uint16_t *custom,
    unsigned first, unsigned last, unsigned enabled, uint16_t *visible);
/* Native copy notification, byte range within the512-byte OBJ shadow.
 * Full authenticated baseline reloads replace current colors but preserve an
 * active native fade's target/errors/progress. Returns explicit refusals. */
unsigned ffta_art_variants_reload(FFTA_ArtVariants *, FFTA_ArtBindings *,
    const uint16_t *native, const uint16_t *reference, const uint16_t *custom,
    unsigned first_byte, unsigned end_byte, unsigned displayed_slots);
/* One slot per simultaneous (class,native bank). New slots require an exact
 * native normal or deployment-dim palette match. Existing bindings retain their
 * recognized fade state. Refusal changes no state, tags, bindings or colors.
 * Native bank masks must come from the authenticated ownership composer. */
unsigned ffta_art_variants_prepare(FFTA_ArtVariants *, FFTA_ArtBindings *,
    uint8_t tags[128], const uint16_t *oam, const uint16_t banks[10],
    const uint16_t *native, const uint16_t *reference, const uint16_t *custom,
    uint16_t *visible);
#endif
