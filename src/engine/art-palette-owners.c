#include "art-palette-owners.h"
#ifdef FFTA_ART_SCOPED_FRAME
#include "art-frame-fast.h"
#endif

#define READY 0x4152544fu
#ifdef FFTA_ART_GROUPED_PALETTES
extern const unsigned char ffta_art_palette_group[10];
#endif

void ffta_art_owners_reset(FFTA_ArtOwners *s, unsigned bank) {
    unsigned i;
    if (bank > 1) return;
    for (i = 0; i < 128; ++i) s->entries[bank][i].owner = 255;
    s->ready[bank] = READY;
}

unsigned ffta_art_owners_record(FFTA_ArtOwners *s, unsigned bank,
                              const uint16_t *source, unsigned before,
                              unsigned after, unsigned resource) {
    unsigned i, j, owner = 255;
    if (bank > 1 || s->ready[bank] != READY || before > after || after > 128)
        return 0;
    if (resource >= 256 && resource < 276) owner = (resource - 256) / 2;
#ifdef FFTA_ART_GROUPED_PALETTES
    if (owner < 10) owner = ffta_art_palette_group[owner];
#endif
    for (i = before; i < after; ++i) {
        FFTA_ArtOwnerEntry *entry = &s->entries[bank][i];
        unsigned a = source[i * 4], b = source[i * 4 + 1];
        entry->owner = 255;
        /* Only the imported ordinary 32x32 4bpp bodies have this contract.
         * Preserve the native renderer's clipping; zero emissions is valid. */
        if (owner == 255 || (a & 0xe300) || (b >> 14) != 2) continue;
        for (j = 0; j < 3; ++j) entry->attributes[j] = source[i * 4 + j];
        entry->owner = owner;
    }
    return 1;
}

static unsigned word(const uint8_t *p) {
    return p[0] | ((unsigned)p[1] << 8) | ((unsigned)p[2] << 16) |
           ((unsigned)p[3] << 24);
}

static unsigned compose(const FFTA_ArtOwners *s, const uint8_t *iw,
                        const uint16_t *hardware, uint8_t *output,
                        unsigned enabled, uint16_t *native_banks) {
    unsigned bank, other, front, ui, main, shown, offset, i, j, requested = 0;
    const uint16_t *source;
    if (iw[0x28] > 1 || iw[0x2f58] > 1) return 0;
    bank = iw[0x28] ^ 1;
    other = iw[0x2f58] ^ 1;
    if (s->ready[bank] != READY) return 0;
    front = word(iw + 0x2c50 + bank * 4);
    ui = word(iw + 0x2f60 + other * 4);
    main = word(iw + 0x20 + bank * 4);
    /* Native capacities: 48 priority objects, 32 UI, 128 main, 16 tail.
     * Reject corrupt counters rather than reproducing a native overrun. */
    if (front > 48 || ui > 32 || main > 128 ||
        word(iw + 0x3168 + other * 4) > 16) return 0;
    /* Native 135C reserves main objects before clipping the UI group. */
    if (front + main >= 128) ui = 0;
    else if (ui > 128 - main - front) ui = 128 - main - front;
    offset = front + ui;
    shown = main;
    if (shown > 128 - offset) shown = 128 - offset;
    source = (const uint16_t *)(iw + 0x30 + bank * 1024);
    /* Validate the entire copied main span before publishing any tags.
     * Attr3 belongs to native affine matrices and is deliberately excluded. */
    for (i = 0; i < shown; ++i) {
        const uint16_t *actual=hardware+(offset+i)*4,*expected=source+i*4;
        if((actual[0]^expected[0]) | (actual[1]^expected[1]) |
           (actual[2]^expected[2]))return 0;
    }
    if(!((uintptr_t)output&3u)) {
        typedef uint32_t TagWord __attribute__((may_alias));
        TagWord *tags=(TagWord *)output;
        for(i=0;i<32;++i)tags[i]=0xffffffffu;
    } else for (i = 0; i < 128; ++i) output[i] = 255;
    if (native_banks) for (i = 0; i < 10; ++i) native_banks[i] = 0;
    for (i = 0; i < shown; ++i) {
        const FFTA_ArtOwnerEntry *entry = &s->entries[bank][i];
        if (entry->owner >= 10 || !(enabled & (1u << entry->owner))) continue;
        for (j = 0; j < 3; ++j)
            if (entry->attributes[j] != source[i * 4 + j]) break;
        if (j == 3) {
            output[offset + i] = entry->owner;
            requested |= 1u << entry->owner;
            if (native_banks) native_banks[entry->owner] |= 1u << (source[i * 4 + 2] >> 12);
        }
    }
    return 0x80000000u | requested;
}

unsigned ffta_art_owners_compose(const FFTA_ArtOwners *s, const uint8_t *iw,
                               const uint16_t *hardware, uint8_t *output) {
    return compose(s, iw, hardware, output, 1023, 0) != 0;
}

unsigned ffta_art_owners_compose_filtered(const FFTA_ArtOwners *s, const uint8_t *iw,
        const uint16_t *hardware, uint8_t *output, unsigned enabled, uint16_t banks[10]) {
#ifdef FFTA_ART_SCOPED_FRAME
    if(!((uintptr_t)iw&3u)) {
        FFTA_ArtOwnerFrame frame={s,iw,hardware,output,enabled,banks};
        return ffta_art_frame_owners(&frame);
    }
#endif
    return compose(s, iw, hardware, output, enabled, banks) & 1023;
}

#ifdef FFTA_ART_NATIVE_OWNER_PRODUCER
unsigned ffta_art_owners_compose_native(const FFTA_ArtOwners *s,const uint8_t *iw,
        const uint16_t *hardware,uint8_t *output,unsigned enabled,uint16_t banks[10]) {
    FFTA_ArtOwnerFrame frame={s,iw,hardware,output,enabled,banks};
    if((uintptr_t)iw&3u)return compose(s,iw,hardware,output,enabled,banks)&1023;
    return ffta_art_frame_native_owners(&frame);
}
#endif

#ifdef FFTA_ART_FUSED_COMPOSE
unsigned ffta_art_owners_compose_fused(const FFTA_ArtOwners *s,const uint8_t *iw,
        const uint16_t *hardware,uint8_t *output,unsigned enabled,uint16_t banks[10],
        FFTA_ArtOamDemands *demands,unsigned *extent) {
    FFTA_ArtFusedOwnerFrame frame={{s,iw,hardware,output,enabled,banks},demands,extent};
#ifdef FFTA_ART_FUSED_WORD_READS
    if(((uintptr_t)iw|(uintptr_t)s|(uintptr_t)hardware)&3u)return 0;
#else
    if((uintptr_t)iw&3u)return 0;
#endif
    return ffta_art_frame_fused_owners(&frame);
}
#endif

#ifdef FFTA_ART_NATIVE_OAM_PREFIX
/* Valid ONLY immediately after authenticated native12BC has initialized all
 *128 slots and DMA-copied priority/UI/main/tail in that order. The native
 * function clips UI to reserve main space, then clips main/tail at128.
 * Attr3 affine updates cannot enable a sentinel or change its palette bank.
 * Unknown counters conservatively retain the complete128-entry walk. */
unsigned ffta_art_owners_native_count(const uint8_t *iw) {
    unsigned bank,other,front,ui,main,tail,count;
    if(iw[0x28]>1 || iw[0x2f58]>1)return 128;
    bank=iw[0x28]^1;other=iw[0x2f58]^1;
    front=word(iw+0x2c50+bank*4);ui=word(iw+0x2f60+other*4);
    main=word(iw+0x20+bank*4);tail=word(iw+0x3168+other*4);
    if(front>48 || ui>32 || main>128 || tail>16)return 128;
    if(front+main>=128)ui=0;
    else if(ui>128-main-front)ui=128-main-front;
    count=front+ui+main+tail;
    return count>128?128:count;
}
#endif
