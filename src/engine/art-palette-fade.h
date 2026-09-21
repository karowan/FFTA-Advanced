#ifndef FFTA_ART_PALETTE_FADE_H
#define FFTA_ART_PALETTE_FADE_H
#include <stdint.h>

/* Caller-owned sidecar for one generated palette. This is not a RAM reservation
 * or an installed hook. Target construction and native effect ownership are
 * separate from the exact native RGB555 interpolation primitive. */
typedef struct {
    uint16_t colors[16], target[16];
    int16_t error[16][3];
    int8_t delta[16][3];
    uint16_t remaining, total;
} FFTA_ArtFade;

/* Native 146E54 initializes half-duration accumulators and normalizes zero to
 * one. Its update uses an eight-bit total; refuse larger unsupported durations
 * without writes instead of reproducing a zero-total infinite loop. */
unsigned ffta_art_fade_start(FFTA_ArtFade *, const uint16_t *colors,
                            const uint16_t *target, unsigned duration);
/* Native flag 0x10 skips transparent index zero during intermediate steps;
 * native finalization writes the complete target including that index. */
unsigned ffta_art_fade_step(FFTA_ArtFade *, unsigned skip_transparent);
unsigned ffta_art_fade_step_masked(FFTA_ArtFade *,unsigned skip_transparent,unsigned colors);
#endif
