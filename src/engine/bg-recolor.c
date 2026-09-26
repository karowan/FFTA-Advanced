#include <stdint.h>
/* Native 0808B890 (layer, map pointer, count, palette bits) recolors `count`
 * map entries in a row and the row below: entry = (entry & 0x0FFF) | palette.
 * Menu setup (e.g. 0807EA00 in the unit menu) un-highlights the previous row
 * 2*previous+2 without checking the constructor's 0xFF "no previous row", so
 * the pointer lands 512 rows (about 12 KiB) past the window's map buffers. In
 * the original heap that hit free memory; with the expansion's lower heap end
 * it ran through the fixed state at 0x0203F000 and wrapped past the end of
 * EWRAM into the party's unit records (0x020405DE -> 0x020005DE: a Viera's
 * ability bytes read as mastered and its equipped fields became 192).
 * This replacement performs the identical recolor only when both rows lie
 * inside the layer's own map buffers; otherwise it does nothing. */
typedef struct {
    uint8_t unknown[0x18];
    uint16_t *front,*back;
    uint8_t unknown2[8];
    uint8_t width,height;
    uint8_t rest[76-0x2a];
} Layer;
_Static_assert(sizeof(Layer)==76,"native BG layer record");
#define LAYERS ((const Layer *)0x030009e0u)

static unsigned inside(uintptr_t p,unsigned bytes,uintptr_t lo,uintptr_t hi) {
    return !(p&1u) && p>=lo && p<=hi && bytes<=hi-p;
}
void ffta_bg_recolor(unsigned layer,uint16_t *map,unsigned count,unsigned palette) {
    count&=0xffffu;palette&=0xffffu;
    if(!count || layer>=8)return;
    const Layer *l=&LAYERS[layer];
    uintptr_t a=(uintptr_t)l->front,b=(uintptr_t)l->back;
    uintptr_t lo=a<b?a:b,hi=(a<b?b:a)+2u*l->width*l->height;
    uintptr_t p=(uintptr_t)map,stride=2u*l->width;
    /* Layer maps live in EWRAM (window layers) or VRAM (layers 0/1). */
    if(!((lo>=0x02000000u && hi<=0x02040000u) || (lo>=0x06000000u && hi<=0x06010000u)))return;
    if(!inside(p,2u*count,lo,hi) || !inside(p+stride,2u*count,lo,hi))return;
    uint16_t *below=(uint16_t *)(p+stride);
    for(unsigned i=0;i<count;i++) {
        map[i]=(uint16_t)((map[i]&0x0fffu)|palette);
        below[i]=(uint16_t)((below[i]&0x0fffu)|palette);
    }
}
