#include "art-palette-dirty.h"
extern const uint16_t ffta_art_pixel_banks[65536];
_Static_assert(sizeof(FFTA_ArtPaletteCache)==2124,"existing cache ABI");

void ffta_art_dirty_begin(FFTA_ArtPaletteCache *cache) {
    unsigned i;
    for(i=0;i<16;i++)cache->pixels[i]=0;
    cache->reserved[0]=0x4454;cache->reserved[1]=0x5931;
    cache->valid=FFTA_ART_DIRTY_MAGIC;
}

void ffta_art_dirty_write(FFTA_ArtPaletteCache *cache,unsigned destination,unsigned bytes) {
    unsigned end=destination+bytes,first,last,i;
    if(cache->valid!=FFTA_ART_DIRTY_MAGIC || !bytes)return;
    if(end<destination) {ffta_art_dirty_begin(cache);return;}
    if(destination>=0x07000000u || end<=0x06000000u)return;
    /* Only ordinary non-mirrored ranges admit selective invalidation. */
    if(destination<0x06000000u || end>0x06018000u) {ffta_art_dirty_begin(cache);return;}
    if(end<=0x06010000u)return;
    first=destination<=0x06010000u?0:(destination-0x06010000u)/64;
    last=(end-0x06010000u+63)/64;
    for(i=first;i<last;i++)cache->pixels[i/32]&=~(1u<<(i%32));
}

void ffta_art_dirty_dma(FFTA_ArtPaletteCache *cache,unsigned destination,unsigned control) {
    unsigned count=control&65535u,width=(control&0x04000000u)?4:2;
    unsigned mode=(control>>21)&3,bytes;
    if(!(control&0x80000000u) || cache->valid!=FFTA_ART_DIRTY_MAGIC)return;
    /* Delayed/repeating DMA can modify pixels after this call. Block reuse
     * until a heap/reset boundary; exact uncached reads remain available. */
    if(control&0x32000000u) {cache->valid=0xffffffffu;return;}
    if(!count)count=65536;
    bytes=count*width;
    if(mode==1) {
        if(destination<bytes-width) {ffta_art_dirty_begin(cache);return;}
        destination-=bytes-width;
    } else if(mode==2)bytes=width;
    ffta_art_dirty_write(cache,destination,bytes);
}

unsigned ffta_art_dirty_mask(FFTA_ArtPaletteCache *cache,const uint32_t *pixels,unsigned tile) {
    uint16_t *masks=(uint16_t *)(cache->pixels+16);
    unsigned used=0,i;
    if(cache->valid==FFTA_ART_DIRTY_MAGIC && tile<512 &&
       (cache->pixels[tile/32]&(1u<<(tile%32))))return masks[tile];
    for(i=0;i<32;i++)used|=ffta_art_pixel_banks[((const uint16_t *)pixels)[i]];
    if(cache->valid==FFTA_ART_DIRTY_MAGIC && tile<512) {
        masks[tile]=used;cache->pixels[tile/32]|=1u<<(tile%32);
    }
    return used;
}
