#include "art-palette-variants.h"
_Static_assert(sizeof(FFTA_ArtVariants)==2*FFTA_ART_HISTORY_SLOTS,"variant mapping layout");

void ffta_art_variants_reset(FFTA_ArtVariants *v) {
    unsigned i;
    for(i=0;i<FFTA_ART_HISTORY_SLOTS;++i) {v->key[i]=255;v->scale[i]=0;}
}

static unsigned find(const uint8_t *keys, unsigned count, unsigned key) {
    unsigned i;
    for(i=0;i<count;++i)if(keys[i]==key)return i;
    return 255;
}

static unsigned match_scale(const uint16_t *reference, const uint16_t *native) {
    unsigned candidate,i;
    /* Native2C11A calls148104 with0x99: floor(channel*153/256), exactly
     * equivalent to19/32 over five-bit channels. Validate every native color. */
    for(candidate=0;candidate<2;++candidate) {
        unsigned scale=candidate?19:32;
        for(i=0;i<16;++i)if(ffta_art_scale_color(reference[i],scale)!=native[i])break;
        if(i==16)return scale;
    }
    return 0;
}

static unsigned match_class_scale(const uint16_t *reference, unsigned owner,
                                 const uint16_t *native) {
    unsigned scale=match_scale(reference+owner*16,native);
#ifdef FFTA_ART_OPPOSING_PALETTES
    /* Native job property7 selects the high nibble of record+11 for opponents;
     * property6 selects the low nibble. Authenticate all sixteen colors of
     * that exact per-class source too. The placeholder custom palette remains
     * the class palette; bindings retain the actual native source for effects. */
    extern const uint16_t ffta_art_native_opposing_reference[160];
    if(!scale)scale=match_scale(ffta_art_native_opposing_reference+owner*16,native);
#endif
    return scale;
}

void ffta_art_variants_track(FFTA_ArtVariants *v, FFTA_ArtBindings *bindings,
    const uint16_t *native, const uint16_t *reference, const uint16_t *custom,
    unsigned first, unsigned last, unsigned enabled, uint16_t *visible) {
    unsigned owner,bank;
    for(owner=0;owner<10;++owner)if(enabled&(1u<<owner)) {
        for(bank=0;bank<16;++bank) {
            unsigned index=256+bank*16,key=owner*16+bank,slot,scale,i;
            uint16_t colors[16];
            /* Damage flashes animate colors1..15 before the actor switches
             * to that bank. Color0 stays native-transparent; authenticate the
             * whole baseline, but do not require it in the effect range. */
            if(first>index+1 || last<index+15 || find(v->key,FFTA_ART_HISTORY_SLOTS,key)<FFTA_ART_HISTORY_SLOTS)continue;
            scale=match_class_scale(reference,owner,native+bank*16);
            if(!scale)continue;
            slot=owner;
            if(v->key[slot]!=255)slot=find(v->key,FFTA_ART_HISTORY_SLOTS,255);
            if(slot==255)return; /* Capacity remains an explicit appearance gate. */
            for(i=0;i<16;++i)colors[i]=ffta_art_scale_color(custom[owner*16+i],scale);
            bindings->entry[slot].bank=255;
            ffta_art_binding_observe_colors(bindings,slot,bank,native,colors);
            /* Before the first effect tick/DMA, an alternate slot must carry
             * this class's baseline, not reset colors indexed by slot number. */
            for(i=0;i<16;++i)visible[slot*16+i]=colors[i];
            v->key[slot]=key;v->scale[slot]=scale;
        }
    }
}

unsigned ffta_art_variants_reload(FFTA_ArtVariants *v, FFTA_ArtBindings *bindings,
    const uint16_t *native, const uint16_t *reference, const uint16_t *custom,
    unsigned first_byte, unsigned end_byte, unsigned displayed_slots) {
    unsigned slot, failures=0;
    for(slot=0;slot<FFTA_ART_HISTORY_SLOTS;++slot) {
        unsigned key=v->key[slot],bank=key&15,owner=key>>4,scale,i;
        FFTA_ArtBinding *entry=&bindings->entry[slot];
        if(owner>=10 || entry->bank!=bank || first_byte>=bank*32+32 ||
            end_byte<=bank*32)continue;
        scale=match_class_scale(reference,owner,native+bank*16);
        if(first_byte>bank*32 || end_byte<bank*32+32 || !scale) {
            /* Do not keep an apparently valid owner for unrecognized data. */
            v->key[slot]=255;v->scale[slot]=0;entry->bank=255;entry->task=0;
            /* A bank reused after its old variant left the display retires
             * history, not a visible effect. A future appearance must pass
             * prepare's full native-palette authentication again. */
            if(displayed_slots&(1u<<slot)) {++bindings->unsupported;++failures;}
            continue;
        }
        for(i=0;i<16;++i) {
            uint16_t color=ffta_art_scale_color(custom[owner*16+i],scale);
            entry->native_base[i]=native[bank*16+i];
            entry->fade.colors[i]=color;
            bindings->colors[slot*16+i]=color;
        }
        v->scale[slot]=scale;
    }
    return failures;
}

unsigned ffta_art_variants_prepare(FFTA_ArtVariants *v, FFTA_ArtBindings *bindings,
    uint8_t tags[128], const uint16_t *oam, const uint16_t banks[10],
    const uint16_t *native, const uint16_t *reference, const uint16_t *custom,
    uint16_t *visible) {
    uint8_t wanted[FFTA_ART_HISTORY_SLOTS],slots[FFTA_ART_HISTORY_SLOTS],scales[FFTA_ART_HISTORY_SLOTS];
    unsigned count=0,owner,bank,i,used=0,occupied,identity=1;
#ifdef FFTA_ART_NATIVE_OAM_PREFIX
    /* An already authenticated identity mapping needs neither allocation nor
     * remapping. Prove every demanded bank against CURRENT keys; any split,
     * missing key or corrupt dormant owner takes the complete original path.
     * This stores no repeated-frame key and never skips fresh ownership. */
    for(owner=0;owner<10;++owner)if(banks[owner]) {
        unsigned key=v->key[owner];
        if(key>>4!=owner || banks[owner]!=(1u<<(key&15)))break;
        used|=1u<<owner;
    }
    if(owner==10 && used) {
        for(i=0;i<FFTA_ART_HISTORY_SLOTS;++i)
            if(v->key[i]!=255 && v->key[i]>=160)break;
        if(i==FFTA_ART_HISTORY_SLOTS)return used;
    }
    used=0;
#endif
    for(owner=0;owner<10;++owner) {
      unsigned bits=banks[owner];
      for(bank=0;bits;++bank,bits>>=1)if(bits&1) {
        unsigned key=owner*16+bank,slot;
        if(count==FFTA_ART_HISTORY_SLOTS)return 0;
        wanted[count]=key;
        slot=find(v->key,FFTA_ART_HISTORY_SLOTS,key);
        slots[count]=slot;
        if(slot<FFTA_ART_HISTORY_SLOTS) {used|=1u<<slot;scales[count]=v->scale[slot];}
        else {
            scales[count]=match_class_scale(reference,owner,native+bank*16);
            if(!scales[count])return 0;
        }
        ++count;
      }
    }
    if(!count)return 0;
    occupied=used;
    /* A temporarily absent character still needs its in-flight or completed
     * transformed colors when it returns. Only baseline history is disposable. */
    for(i=0;i<FFTA_ART_HISTORY_SLOTS;++i)if(!(used&(1u<<i)) && v->key[i]!=255) {
        FFTA_ArtBinding *entry=&bindings->entry[i];
        unsigned c,source=v->key[i]>>4;
        if(source>=10)return 0;
        if(entry->task) {occupied|=1u<<i;continue;}
        for(c=0;c<16;++c)
            if(entry->fade.colors[c]!=ffta_art_scale_color(custom[source*16+c],v->scale[i]))break;
        if(c<16)occupied|=1u<<i;
    }
    for(i=0;i<count;++i)if(slots[i]==255) {
        unsigned slot=wanted[i]>>4;
        if(occupied&(1u<<slot))for(slot=0;slot<FFTA_ART_HISTORY_SLOTS && (occupied&(1u<<slot));++slot){}
        if(slot==FFTA_ART_HISTORY_SLOTS)return 0;
        slots[i]=slot;used|=1u<<slot;occupied|=1u<<slot;
    }
    for(i=0;i<count;++i)if(slots[i]!=(wanted[i]>>4))identity=0;
    /* The composer already authenticated the bank masks and tags. An identity
     * mapping needs no second OAM walk; validate before changing any tags when
     * a real split/reassignment is necessary. */
    if(!identity)for(i=0;i<128;++i)if(tags[i]!=255) {
        unsigned key=tags[i]*16+(oam[i*4+2]>>12);
        if(tags[i]>=10 || find(wanted,count,key)==255)return 0;
    }
    for(i=0;i<count;++i) {
        unsigned slot=slots[i],key=wanted[i];
        if(v->key[slot]!=key) {
            uint16_t colors[16];unsigned c;
            for(c=0;c<16;++c)colors[c]=ffta_art_scale_color(custom[(key>>4)*16+c],scales[i]);
            bindings->entry[slot].bank=255;
            ffta_art_binding_observe_colors(bindings,slot,key&15,native,colors);
            for(c=0;c<16;++c)visible[slot*16+c]=colors[c];
            v->key[slot]=key;v->scale[slot]=scales[i];
        }
    }
    if(!identity)for(i=0;i<128;++i)if(tags[i]!=255)
        tags[i]=slots[find(wanted,count,tags[i]*16+(oam[i*4+2]>>12))];
    return used;
}
