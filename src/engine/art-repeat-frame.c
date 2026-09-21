#include "art-repeat-frame.h"
_Static_assert(FFTA_ART_HISTORY_SLOTS==20,"repeat frame uses the complete twenty-history layout");
_Static_assert(sizeof(FFTA_ArtRepeat)==928,"repeat frame fits existing reservation");
typedef struct {
    const uint16_t *oam;
    uint32_t *ab;
    uint16_t *c;
    const uint8_t *obj;
    const uint32_t *pixels;
    const uint16_t *tiles;
    unsigned count,operation;
    const uint8_t *owners;
} Probe;
extern unsigned ffta_art_repeat_probe(const Probe *);

static unsigned probe(FFTA_ArtRepeat *s,const FFTA_ArtPaletteFrame *f,
                      const FFTA_ArtPaletteCache *cache,unsigned operation) {
    Probe p={f->oam,s->ab,s->c,f->obj,cache?cache->pixels:0,s->tiles,operation==1?0:s->count,operation,f->owner};
    return ffta_art_repeat_probe(&p);
}
static unsigned equal(const void *left,const void *right,unsigned words) {
    typedef uint32_t Word __attribute__((may_alias));
    const Word *a=left,*b=right;
    for(unsigned i=0;i<words;++i)if(a[i]!=b[i])return 0;
    return 1;
}
static unsigned pixels_valid(const FFTA_ArtRepeat *s,const FFTA_ArtPaletteCache *cache) {
    if(s->count>32)return 0;
    unsigned mask=s->count==32?~0u:((1u<<s->count)-1u);
    return (cache->valid&mask)==mask;
}

void ffta_art_repeat_begin(FFTA_ArtRepeat *s,const FFTA_ArtPaletteFrame *f) {
    unsigned previous=s->valid,count=s->count;
    s->valid=0;s->count=0;
    unsigned captured=probe(s,f,0,1);
    if(!captured)s->count=33; /* Never publish a partially captured key. */
    else if(previous && count<=32 && captured==1)s->count=count|0x80000000u;
}

void ffta_art_repeat_finish(FFTA_ArtRepeat *s,const FFTA_ArtPaletteFrame *f,
        const FFTA_ArtPaletteCache *cache,const FFTA_ArtVariants *variants,unsigned highlight) {
    static const uint8_t widths[12]={8,16,32,64,16,32,32,64,8,8,16,32};
    static const uint8_t heights[12]={8,16,32,64,8,8,16,32,16,32,32,64};
    if(s->count==33)return;
    unsigned count=s->count&0x80000000u?s->count&0x7fffffffu:0;
    if(!(s->count&0x80000000u))for(unsigned i=0;i<128;++i) {
        unsigned a=s->ab[i]&65535,b=s->ab[i]>>16,c=s->c[i];
        if(c&0xe000)continue; /* Authenticated disabled/custom/native4bpp key. */
        unsigned shape=a>>14,index=shape*4+(b>>14);
        if(shape==3)return;
        unsigned width=widths[index],height=heights[index],start=(c&1022)*32;
        if(start+width*height>32768)return;
        int x=b&511,y=a&255;
        if(x>=256)x-=512;
        if(y>=160)y-=256;
        for(unsigned row=0;row<height;row+=8)for(unsigned col=0;col<width;col+=8) {
            int px=x+(int)((b&0x1000)?width-8-col:col);
            int py=y+(int)((b&0x2000)?height-8-row:row);
            if(!(a&0x1100) && (px>=240 || px+8<=0 || py>=160 || py+8<=0))continue;
            if(count==32)return;
            s->tiles[count++]=(start+row*width+col*8)/64;
        }
    }
    s->count=count;
    /* Multiple objects may alias the old per-object cache. Require all actual
     * bytes to match our complete ordered footprint; otherwise do not reuse. */
    if(!pixels_valid(s,cache) || !probe(s,f,cache,2))return;
    for(unsigned i=0;i<20;++i) {
        s->variants.key[i]=variants->key[i];s->variants.scale[i]=variants->scale[i];
    }
    s->plan=*f->plan;s->mode=f->one_dimensional;s->highlight=highlight;
    s->valid=1;
}

unsigned ffta_art_repeat_hit(FFTA_ArtRepeat *s,const FFTA_ArtPaletteFrame *f,
        const FFTA_ArtPaletteCache *cache,const FFTA_ArtVariants *variants,unsigned highlight) {
    if(!s->valid || f->custom_count!=20 || f->one_dimensional!=s->mode ||
       highlight!=s->highlight || !pixels_valid(s,cache) ||
       !equal(&s->variants,variants,10) || !equal(&s->plan,f->plan,8) ||
       !probe(s,f,cache,0)) {++s->misses;return 0;}
    /* Fresh ownership tags are class IDs; the saved plan uses history slots.
     * Identity is common, but native-bank variants must be mapped explicitly. */
    uint8_t *tags=(uint8_t *)f->owner;
    unsigned identity=1;
    for(unsigned slot=0;slot<20;++slot)if((f->plan->requested&(1u<<slot)) && (variants->key[slot]>>4)!=slot)identity=0;
    if(identity) {++s->hits;return 1;}
    /* Validate split identities before changing any tags on a miss. */
    for(unsigned i=0;i<128;++i)if(tags[i]!=255) {
        unsigned key=tags[i]*16+(f->oam[i*4+2]>>12),slot=tags[i];
        if(variants->key[slot]!=key)
            for(slot=0;slot<20 && variants->key[slot]!=key;++slot){}
        if(slot==20) {++s->misses;return 0;}
    }
    for(unsigned i=0;i<128;++i)if(tags[i]!=255) {
        unsigned key=tags[i]*16+(f->oam[i*4+2]>>12),slot=tags[i];
        if(variants->key[slot]!=key)
            for(slot=0;slot<20 && variants->key[slot]!=key;++slot){}
        tags[i]=slot;
    }
    ++s->hits;return 1;
}
