#include <stdint.h>

/* Reserved persistent metadata byte. Bit 0 also conservatively blocks legacy
 * saves whose completed original offer cannot distinguish failure from death. */
#define HISTORY 0x1e79u
#define INITIALIZED 2u
#define SEEN 1u

static int current(const uint8_t *state) {
    static const uint8_t magic[8]={'F','F','T','A','E','X','P','1'};
    for (unsigned i=0;i<8;++i) if (state[0x1e70+i]!=magic[i]) return 0;
    return state[0x1e78]==1;
}
static int present(const uint8_t *state) {
    for (unsigned i=0;i<24;++i) {
        const uint8_t *u=state+0x80+264*i;
        /* Native named-character identity, independent of current job/level. */
        if (u[4] && u[6]==3 && u[0]==0x5f && u[1]==0x16 &&
            u[2]==0x55 && u[3]==0x08) return 1;
    }
    return 0;
}
/* Call on every successfully decoded native/expanded normal or suspend load,
 * and before new-game missions become playable. Staging blocks are supported. */
void ffta_quin_prepare(uint8_t *state) {
    if (!current(state)) return;
    if (!(state[HISTORY]&INITIALIZED)) {
        unsigned uncertain=(state[0x1fd8]&2)!=0; /* flag 0x341: Missing Prof */
        state[HISTORY]=(uint8_t)((state[HISTORY]&~3u)|INITIALIZED|
                                ((uncertain || present(state)) ? SEEN : 0));
    } else if (present(state)) state[HISTORY]|=SEEN;
}
/* Only accepted native roster commits call this; candidate/preview generation
 * must not mark a failed or declined offer as accepted. */
void ffta_quin_observe(uint8_t *state) {
    if (current(state) && present(state)) state[HISTORY]|=INITIALIZED|SEEN;
}
int ffta_quin_retry_blocked(const uint8_t *state) {
    return !current(state) || !(state[HISTORY]&INITIALIZED) ||
           (state[HISTORY]&SEEN) || present(state);
}
int ffta_quin_candidate(unsigned mission,uint8_t *output) {
    extern int ffta_original_recruit(unsigned,uint8_t *);
    if ((uint16_t)mission==111 &&
        ffta_quin_retry_blocked((const uint8_t *)0x02000000u)) {
        /* Same native no-candidate output contract, with no RNG consumption. */
        for (unsigned i=0;i<264;++i) output[i]=0;
        return 0;
    }
    return ffta_original_recruit(mission,output);
}
