#include <stdint.h>
#include "battle-state.h"
#include "samurai-state.h"

extern unsigned ffta_original_status_icon(const uint8_t *,unsigned);

unsigned ffta_status_icon(const uint8_t *unit,unsigned key) {
    key=(uint16_t)key;
    if(key==25) {
        uint8_t *state=ffta_owned_exposed((uint8_t *)unit);
        return state && (*state&1u) ? 25 : 0;
    }
    if(key==26)return ffta_centered_active(unit)?26:0;
    return ffta_original_status_icon(unit,key);
}
unsigned ffta_status_next_key(const uint8_t *unit,unsigned previous) {
    unsigned limit=(ffta_status_icon(unit,25)||ffta_status_icon(unit,26))?26:24;
    unsigned next=(uint8_t)(previous+1);
    /* Native selector is an s8, including wrap at FF. Preserve that behavior
     * outside the added keys; the stable state machine starts at one. */
    return (int8_t)next>(int)limit?1:next;
}

/* The battle graphics constructor reserves four extra tiles by moving its
 * upper dynamic pool from1E0 to1E4. Original fixed tiles120..1DF and the
 * lower dynamic pool are unchanged. Never reuse native visual slot zero:
 * unrelated fixed UI descriptors also reference those tiles. */
static const uint16_t narrow_shape[]={1,0x80f8,0x01fc,0};
#include "status-glyphs.h"
unsigned ffta_status_visual(uint8_t *sprite,unsigned icon) {
    if(icon==25 || icon==26) {
        volatile uint16_t *tiles=(volatile uint16_t *)0x06013c00u;
        for(unsigned i=0;i<64;++i)tiles[i]=ffta_status_glyphs[i];
        *(const uint16_t **)(sprite+0x28)=narrow_shape;
        return 0x1e0u+2u*(icon-25u);
    }
    return (uint16_t)(0x143u+4u*(int8_t)icon);
}
