#include "art-palette-fade.h"
_Static_assert(sizeof(FFTA_ArtFade) == 212, "fade sidecar layout");

unsigned ffta_art_fade_start(FFTA_ArtFade *state, const uint16_t *colors,
                            const uint16_t *target, unsigned duration) {
    unsigned i, channel;
    if (duration > 255) return 0;
    for (i = 0; i < 16; ++i) {
        state->colors[i] = colors[i];
        state->target[i] = target[i];
        for (channel = 0; channel < 3; ++channel) {
            unsigned shift = channel * 5;
            state->error[i][channel] = duration / 2;
            state->delta[i][channel] = ((target[i] >> shift) & 31) -
                                       ((colors[i] >> shift) & 31);
        }
    }
    state->remaining = state->total = duration ? duration : 1;
    return 1;
}

unsigned ffta_art_fade_step(FFTA_ArtFade *state, unsigned skip_transparent) {
    return ffta_art_fade_step_masked(state,skip_transparent,65535);
}

unsigned ffta_art_fade_step_masked(FFTA_ArtFade *state,unsigned skip_transparent,unsigned colors) {
    unsigned i, channel;
    if (!state->remaining) return 0;
    if (state->remaining == 1) {
        for (i = 0; i < 16; ++i)if(colors&(1u<<i))state->colors[i] = state->target[i];
        state->remaining = 0;
        return 1;
    }
    for (i = skip_transparent ? 1 : 0; i < 16; ++i) {
        if(!(colors&(1u<<i)))continue;
        unsigned result = 0;
        for (channel = 0; channel < 3; ++channel) {
            int value = (state->colors[i] >> (channel * 5)) & 31;
            int delta = state->delta[i][channel];
            int direction = delta < 0 ? -1 : 1;
            /* Native endpoints do not consume the channel accumulator. */
            if ((direction < 0 && value) || (direction > 0 && value != 31)) {
                int error = state->error[i][channel] - (delta < 0 ? -delta : delta);
                while (error < 0) {
                    value += direction;
                    error += state->total;
                }
                state->error[i][channel] = error;
            }
            result |= (unsigned)value << (channel * 5);
        }
        state->colors[i] = result;
    }
    --state->remaining;
    return 1;
}
