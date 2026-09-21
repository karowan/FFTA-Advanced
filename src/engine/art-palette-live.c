#include "art-palette-owners.h"
#include "art-palette-plan.h"
#include "art-palette-binding.h"
#include "art-palette-variants.h"
#include "art-palette-highlight.h"
#include <stddef.h>
#ifdef FFTA_ART_REPEAT_FRAME
#include "art-repeat-frame.h"
#endif
#ifdef FFTA_ART_DMA_TILE_CACHE
#include "art-palette-dirty.h"
#endif
#ifdef FFTA_ART_PROVISIONAL_HISTORY
#include "art-palette-provisional.h"
#endif

/* Private integration stage reserves these pages by lowering all three
 * native heap limits. It is transient and never enters saved unit records. */
typedef struct {
    uint32_t magic;
    FFTA_ArtOwners owners;
    uint16_t native_colors[256];
    uint32_t active, applied, restored, failed;
    uint16_t start_line, end_line;
    FFTA_ArtPalettePlan plan;
    uint8_t tags[128];
    uint16_t display_line, display_flags;
    FFTA_ArtBindings bindings;
    uint32_t fade_command;
    uint32_t emitted[2];
    uint32_t compose_phase;
    uint16_t visible_colors[FFTA_ART_HISTORY_SLOTS*16];
    FFTA_ArtPaletteCache cache;
    uint16_t after_owners, after_observe, after_copy, after_plan;
    uint32_t variant_refusals, setup_refusals, target_refusals, tick_refusals;
    FFTA_ArtVariants variants;
#ifdef FFTA_ART_PROVISIONAL_HISTORY
    uint8_t confirmed_keys[FFTA_ART_HISTORY_SLOTS];
#endif
#if FFTA_ART_HISTORY_SLOTS == 20
    uint32_t native_highlight;
#endif
#ifdef FFTA_ART_REPEAT_FRAME
    FFTA_ArtRepeat repeat;
#endif
} Live;
#ifndef FFTA_ART_LIVE_BASE
#define FFTA_ART_LIVE_BASE 0x0203d000u
#define FFTA_ART_LIVE_BYTES 8192
#endif
_Static_assert(sizeof(Live) <= FFTA_ART_LIVE_BYTES, "palette state reservation");
#if FFTA_ART_HISTORY_SLOTS == 10
_Static_assert(sizeof(Live) == 8096 && offsetof(Live, active) == 2572 &&
               offsetof(Live, start_line) == 2588 && offsetof(Live, plan.requested) == 2594,
               "palette observation layout");
#else
/* Export the compiled layout; tests/builders must not guess shifted offsets. */
const unsigned ffta_art_live_layout[]={sizeof(Live),offsetof(Live,bindings),
    offsetof(Live,visible_colors),offsetof(Live,after_owners),
    offsetof(Live,variant_refusals),offsetof(Live,variants),offsetof(Live,tags),
    offsetof(Live,display_line),offsetof(Live,fade_command),offsetof(Live,emitted),
    offsetof(Live,compose_phase),offsetof(FFTA_ArtBindings,started)
#ifdef FFTA_ART_PROVISIONAL_HISTORY
    ,offsetof(Live,confirmed_keys)
#endif
#if FFTA_ART_HISTORY_SLOTS == 20
    ,offsetof(Live,native_highlight)
#endif
};
#endif
#ifdef FFTA_ART_REPEAT_FRAME
const unsigned ffta_art_repeat_layout[]={offsetof(Live,repeat),sizeof(FFTA_ArtRepeat)};
#endif
static Live *const live = (Live *)FFTA_ART_LIVE_BASE;
#define MAGIC 0x50414c31u
extern const uint16_t ffta_art_custom_colors[160];
extern const uint16_t ffta_art_native_reference[160];
extern const unsigned ffta_art_custom_mask;
#ifdef FFTA_ART_GROUPED_PALETTES
extern const unsigned char ffta_art_palette_group[10];
#endif
extern void ffta_art_copy_words(void *, const void *, unsigned);
extern void ffta_art_original_begin(void);
extern void ffta_art_original_end(void);
extern void ffta_art_original_reset(void);
extern void ffta_art_original_compose(void);
extern void ffta_art_original_render(const uint8_t *, const uint8_t *);
extern void ffta_art_original_battle_render(const uint8_t *, const uint8_t *);
extern uint32_t ffta_art_original_fade_setup(unsigned, unsigned, unsigned, unsigned);
extern uint32_t ffta_art_original_fade_black(unsigned, unsigned, unsigned);
extern uint32_t ffta_art_original_fade_white(unsigned, unsigned, unsigned);
extern uint32_t ffta_art_original_fade_table(unsigned, unsigned, unsigned, const uint16_t *);
extern void ffta_art_original_fade_tick(uint16_t *);
extern uint32_t ffta_art_original_fade_gray(unsigned, unsigned, unsigned);
extern uint32_t ffta_art_original_fade_tint(unsigned, unsigned, unsigned);
extern uint32_t ffta_art_original_fade_rgb(unsigned, unsigned, unsigned, unsigned, unsigned, unsigned);
extern uint32_t ffta_art_original_fade_solid(unsigned, unsigned, unsigned, unsigned, unsigned, unsigned);
extern uint32_t ffta_art_original_fade_blend(unsigned, unsigned, unsigned, unsigned, unsigned, unsigned);
extern uint32_t ffta_art_original_fade_brighten(unsigned, unsigned, unsigned, unsigned);
extern uint32_t ffta_art_original_fade_darken(unsigned, unsigned, unsigned, unsigned);
extern uint32_t ffta_art_original_fade_exposure(unsigned, unsigned, unsigned, unsigned);
extern uint32_t ffta_art_original_fade_exposure_rgb(unsigned, unsigned, unsigned, unsigned, unsigned, unsigned);
extern uint32_t ffta_art_original_fade_table_exposure(unsigned,unsigned,unsigned,const uint16_t *,unsigned,unsigned,unsigned);
extern uint32_t ffta_art_original_fade_table_blend(unsigned,unsigned,unsigned,const uint16_t *,unsigned,unsigned,unsigned);
extern void ffta_art_original_fade_cancel(unsigned,unsigned,unsigned);
extern void ffta_art_original_fade_delete(uint32_t);
extern uint32_t ffta_art_original_fade_collect(uint32_t);
extern void ffta_art_original_fade_delete_all(void);
extern void ffta_art_original_fade_rotate(uint16_t *);
extern void ffta_art_original_fade_cycle(uint16_t *);

uint32_t ffta_art_live_palette_copy(void *destination, const void *source, unsigned count) {
    /* The authenticated native copy epilogue pops its caller's LR into r0.
     * Preserve that observable return register across the nested call. */
    uint32_t result=(uint32_t)__builtin_return_address(0);
    /* Keep the Thumb bit in an explicit function pointer. An untyped absolute
     * linker symbol may generate ARM LDR-PC interworking, invalid on ARMv4T. */
    ((void (*)(void *,const void *,unsigned))0x091046c9u)(destination,source,count);
    unsigned first=(unsigned)destination,end=first+count;
    if(live->magic==MAGIC && count && end>=first && first<0x03003c60u && end>0x03003a60u) {
        first=first<0x03003a60u?0:first-0x03003a60u;
        end=end>0x03003c60u?512:end-0x03003a60u;
#if FFTA_ART_HISTORY_SLOTS == 20
        if(first<320 && end>288) {
            live->native_highlight=ffta_art_highlight_copy(result,(unsigned)destination,
                (unsigned)source,count,(const uint16_t *)0x03003b80u,
                (const uint16_t *)0x08419f40u);
            if(live->native_highlight) {
                /* This native consumer deliberately gives every target the
                 * same pulsing palette. Keep custom shapes, native colors.
                 * Retire any earlier deployment-dim ownership of bank9. */
                unsigned retired=ffta_art_highlight_retire(&live->variants,&live->bindings);
                live->plan.requested&=~retired;
                live->cache.valid=0;
            }
        }
#endif
        live->variant_refusals+=ffta_art_variants_reload(&live->variants,&live->bindings,
            (const uint16_t *)0x03003a60u,ffta_art_native_reference,ffta_art_custom_colors,
            first,end,live->plan.requested);
#ifdef FFTA_ART_PROVISIONAL_HISTORY
        ffta_art_provisional_confirm(&live->variants,live->confirmed_keys,0);
#endif
    }
    return result;
}

static void restore(void) {
    volatile uint16_t *hardware = (volatile uint16_t *)0x05000200u;
    unsigned bank;
    if (live->magic != MAGIC) return;
    if (live->active) {
        for (bank = 0; bank < 16; ++bank) if (live->active & (1u << bank))
            ffta_art_copy_words((void *)(hardware+bank*16),live->native_colors+bank*16,8);
        ++live->restored;
        live->active = 0;
    }
}

void ffta_art_heap_reset(void) {
    restore();
#ifdef FFTA_ART_REPEAT_FRAME
    live->repeat.valid=live->repeat.hits=live->repeat.misses=0;
#endif
    live->owners.ready[0] = live->owners.ready[1] = 0;
    live->active = live->applied = live->restored = live->failed = 0;
    live->start_line = live->end_line = 0;
    live->display_line = live->display_flags = 0;
    ffta_art_bindings_reset(&live->bindings, ffta_art_custom_colors);
    live->fade_command = 0;
    live->emitted[0] = live->emitted[1] = 0;
    live->compose_phase = 0;
#if FFTA_ART_HISTORY_SLOTS == 20
    live->native_highlight=0;
#endif
#if FFTA_ART_HISTORY_SLOTS == 10
    ffta_art_copy_words(live->visible_colors, ffta_art_custom_colors, 80);
#else
    ffta_art_copy_words(live->visible_colors,live->bindings.colors,FFTA_ART_HISTORY_SLOTS*8);
#endif
    live->cache.valid = 0;
#ifdef FFTA_ART_DMA_TILE_CACHE
    ffta_art_dirty_begin(&live->cache);
#endif
    live->plan.requested = 0;
    live->variant_refusals = live->setup_refusals = 0;
    live->target_refusals = live->tick_refusals = 0;
    ffta_art_variants_reset(&live->variants);
#ifdef FFTA_ART_PROVISIONAL_HISTORY
    for(unsigned slot=0;slot<FFTA_ART_HISTORY_SLOTS;slot++)live->confirmed_keys[slot]=255;
#endif
    live->magic = MAGIC;
#ifdef FFTA_ART_PARTY_ROOT
    extern void ffta_art_party_heap_reset(void);
    ffta_art_party_heap_reset();
#endif
}

void ffta_art_live_begin(void) {
    ffta_art_original_begin(); /* Native forced blank precedes restoration. */
    if (live->magic != MAGIC) ffta_art_heap_reset();
    restore(); /* Before native queued writes/full palette DMA. */
}

#ifdef FFTA_ART_DMA_TILE_CACHE
void ffta_art_live_obj_write(const unsigned *descriptor) {
    if(live->magic==MAGIC)
        ffta_art_dirty_dma(&live->cache,descriptor[2],descriptor[3]);
}
#endif

void ffta_art_live_end(void) {
    ffta_art_original_end();
    if (live->magic != MAGIC) return;
    live->display_line = *(volatile uint16_t *)0x04000006u;
    live->display_flags = *(volatile uint16_t *)0x04000000u;
}

void ffta_art_live_reset(void) {
    unsigned bank = *(volatile uint8_t *)0x03000028u;
    ffta_art_original_reset();
    if (live->magic != MAGIC) ffta_art_heap_reset();
    if (bank < 2) {
        /* Initialize the full entry array only if this frame emits an enabled
         * custom body. Native-only frames must not pay a 128-entry reset. */
        live->owners.ready[bank] = 0;
        live->emitted[bank] = 0;
    }
}

static void render(const uint8_t *actor, const uint8_t *context,
                   void (*original)(const uint8_t *, const uint8_t *)) {
    unsigned bank = *(volatile uint8_t *)0x03000028u;
    const volatile unsigned *counts = (const volatile unsigned *)0x03000020u;
    unsigned resource = actor[6] | ((unsigned)actor[7] << 8);
#ifdef FFTA_ART_GROUPED_PALETTES
    unsigned palette_owner = resource >= 256 && resource < 276 ?
                            ffta_art_palette_group[(resource - 256) / 2] : 255;
    unsigned custom = palette_owner < 10 &&
                      (ffta_art_custom_mask & (1u << palette_owner));
#else
    unsigned custom = resource >= 256 && resource < 276 &&
                      (ffta_art_custom_mask & (1u << ((resource - 256) / 2)));
#endif
    unsigned before;
    if (live->magic != MAGIC || bank > 1 || (!custom && !live->emitted[bank])) {
        original(actor, context);
        return;
    }
    if (!live->owners.ready[bank]) ffta_art_owners_reset(&live->owners, bank);
    before = counts[bank];
    original(actor, context);
    if (live->magic != MAGIC || bank > 1 || bank != *(volatile uint8_t *)0x03000028u) return;
    if (!ffta_art_owners_record(&live->owners, bank,
            (const uint16_t *)(0x03000030u + bank * 1024), before, counts[bank], resource))
        ++live->failed;
    else if (counts[bank] > before && resource >= 256 && resource < 276)
#ifdef FFTA_ART_GROUPED_PALETTES
        live->emitted[bank] |= (1u << palette_owner) & ffta_art_custom_mask;
#else
        live->emitted[bank] |= (1u << ((resource - 256) / 2)) & ffta_art_custom_mask;
#endif
}

void ffta_art_live_render(const uint8_t *actor, const uint8_t *context) {
    render(actor, context, ffta_art_original_render);
}

void ffta_art_live_battle_render(const uint8_t *actor, const uint8_t *context) {
    render(actor, context, ffta_art_original_battle_render);
}

void ffta_art_live_compose(void) {
    unsigned i, requested = 0;
    uint16_t native_banks[10];
    FFTA_ArtPaletteFrame frame;
#ifdef FFTA_ART_FUSED_COMPOSE
    FFTA_ArtOamDemands demands;
    unsigned extent=128,fused=0;
#endif
    ffta_art_original_compose();
    if (live->magic != MAGIC) return;
    live->compose_phase = 1;
    /* The selected native source bank is the opposite of the write bank.
     * With no enabled custom emissions, no ownership scan or remap is needed.
     * A conservative mask may retain invalidated/clipped emissions; the full
     * authenticated bridge still checks those frames before any palette write. */
    i = *(volatile uint8_t *)0x03000028u;
    /* Native palette DMA runs even while no custom actor is visible. Keep
     * effect history at that same displayed phase for a later appearance. */
    if(!*(volatile uint16_t *)0x03000e10u) {
        unsigned slot;
        /* Empty slots have no displayed history. Both acquisition paths set
         * their initial latch explicitly before publishing a new key. Rotation
         * history must latch even with no fade starts or visible emissions. */
        for(slot=0;slot<FFTA_ART_HISTORY_SLOTS;++slot)if(live->variants.key[slot]!=255)
            ffta_art_copy_words(live->visible_colors+slot*16,live->bindings.colors+slot*16,8);
    }
    if (i > 1 || !live->emitted[i ^ 1]) return;
    /* 04CE skips palette DMA on ordinary repeated battle frames too.
     * Recompose their OAM and reapply the last displayed custom color phase;
     * removing the overlay here produces a two-out-of-three-frame flicker. */
    live->compose_phase = 2;
    live->compose_phase = 3;
    live->start_line = *(volatile uint16_t *)0x04000006u;
#ifdef FFTA_ART_FUSED_COMPOSE
    /* Native targeting intentionally changes ownership after this point.
     * Keep its existing full classification path. Other demands live only in
     * this stack frame; no native OAM/source writer intervenes before use. */
    if(!live->native_highlight) {
        extern unsigned ffta_art_owners_compose_fused(const FFTA_ArtOwners *,const uint8_t *,const uint16_t *,uint8_t *,unsigned,uint16_t *,FFTA_ArtOamDemands *,unsigned *);
        requested=ffta_art_owners_compose_fused(&live->owners,(const uint8_t *)0x03000000u,
            (const uint16_t *)0x07000000u,live->tags,ffta_art_custom_mask,native_banks,&demands,&extent);
        fused=1;
    } else
#endif
    {
#ifdef FFTA_ART_NATIVE_OWNER_PRODUCER
    /* No OAM/source writer occurs between original_compose and this call.
     * The verified native producer establishes the complete copied span. */
    extern unsigned ffta_art_owners_compose_native(const FFTA_ArtOwners *,const uint8_t *,const uint16_t *,uint8_t *,unsigned,uint16_t *);
    requested = ffta_art_owners_compose_native(&live->owners, (const uint8_t *)0x03000000u,
#else
    requested = ffta_art_owners_compose_filtered(&live->owners, (const uint8_t *)0x03000000u,
#endif
                               (const uint16_t *)0x07000000u, live->tags,
                               ffta_art_custom_mask, native_banks);
    }
    live->after_owners = *(volatile uint16_t *)0x04000006u;
    live->compose_phase = 4;
    if (!requested) return;
#if FFTA_ART_HISTORY_SLOTS == 20
    if(live->native_highlight) {
        requested=ffta_art_highlight_filter(live->tags,
            (const uint16_t *)0x07000000u,native_banks);
        if(!requested)return;
    }
#endif
    live->compose_phase = 5;
#ifdef FFTA_ART_REPEAT_FRAME
    /* Reauthenticate current ownership first. This permits new native draws
     * with unchanged palette demands, without assuming producer lifetimes. */
    frame.oam=(uint16_t *)0x07000000u;frame.obj=(const uint8_t *)0x06010000u;
    frame.owner=live->tags;frame.palette=(uint16_t *)0x05000200u;
    frame.custom=live->visible_colors;frame.plan=&live->plan;
    frame.one_dimensional=(*(volatile uint16_t *)0x03000940u&64u)!=0;
    frame.custom_count=FFTA_ART_HISTORY_SLOTS;
    if(ffta_art_repeat_hit(&live->repeat,&frame,&live->cache,&live->variants,live->native_highlight)) {
        extern void ffta_art_palette_apply_validated(FFTA_ArtPaletteFrame *,uint16_t *);
        ffta_art_palette_apply_validated(&frame,live->native_colors);
        live->after_observe=live->after_copy=*(volatile uint16_t *)0x04000006u;
        goto applied;
    }
    ffta_art_repeat_begin(&live->repeat,&frame);
#endif
    requested = ffta_art_variants_prepare(&live->variants, &live->bindings,
            live->tags, (const uint16_t *)0x07000000u, native_banks,
            (const uint16_t *)0x03003a60u, ffta_art_native_reference,
            ffta_art_custom_colors, live->visible_colors);
    if (!requested) {
        ++live->bindings.unsupported;
        ++live->variant_refusals;
        return;
    }
#ifdef FFTA_ART_PROVISIONAL_HISTORY
    ffta_art_provisional_confirm(&live->variants,live->confirmed_keys,requested);
#endif
    live->after_observe = *(volatile uint16_t *)0x04000006u;
    frame.oam = (uint16_t *)0x07000000u;
    frame.obj = (const uint8_t *)0x06010000u;
    frame.owner = live->tags;
    frame.palette = (uint16_t *)0x05000200u;
    frame.custom = live->visible_colors;
    frame.plan = &live->plan;
    frame.one_dimensional = (*(volatile uint16_t *)0x03000940u & 64u) != 0;
    frame.custom_count = FFTA_ART_HISTORY_SLOTS;
    live->after_copy = *(volatile uint16_t *)0x04000006u;
    live->compose_phase = 6;
#ifdef FFTA_ART_FUSED_COMPOSE
    if(fused) {
        extern unsigned ffta_art_palette_live_apply_fused(FFTA_ArtPaletteFrame *,FFTA_ArtPaletteCache *,uint16_t *,const FFTA_ArtOamDemands *,unsigned);
        demands.requested=requested; /* Current authenticated history mapping. */
        if(!ffta_art_palette_live_apply_fused(&frame,&live->cache,live->native_colors,&demands,extent)) {++live->failed;return;}
    } else
#endif
    {
#ifdef FFTA_ART_NATIVE_OAM_PREFIX
    {
        extern unsigned ffta_art_owners_native_count(const uint8_t *);
        extern unsigned ffta_art_palette_live_apply_prefix(FFTA_ArtPaletteFrame *,FFTA_ArtPaletteCache *,uint16_t *,unsigned);
        unsigned count=ffta_art_owners_native_count((const uint8_t *)0x03000000u);
        if(!ffta_art_palette_live_apply_prefix(&frame,&live->cache,live->native_colors,count)) {++live->failed;return;}
    }
#else
    if (!ffta_art_palette_live_apply(&frame, &live->cache, live->native_colors)) { ++live->failed; return; }
#endif
    }
#ifdef FFTA_ART_REPEAT_FRAME
    ffta_art_repeat_finish(&live->repeat,&frame,&live->cache,&live->variants,live->native_highlight);
applied:
#endif
    live->after_plan = *(volatile uint16_t *)0x04000006u;
    for (i = 0; i < FFTA_ART_HISTORY_SLOTS; ++i) if (live->plan.requested & (1u << i))
        live->active |= 1u << live->plan.bank[i];
    ++live->applied;
    live->end_line = *(volatile uint16_t *)0x04000006u;
    live->compose_phase = 7;
}

uint32_t ffta_art_live_fade_setup(unsigned first, unsigned last, unsigned duration, unsigned flags) {
    uint32_t task = ffta_art_original_fade_setup(first, last, duration, flags);
    if (live->magic == MAGIC) {
        unsigned before = live->bindings.unsupported;
        ffta_art_binding_invalidate(&live->bindings, first & 65535, last & 65535,
                                     task, live->fade_command);
        live->setup_refusals += live->bindings.unsupported - before;
    }
    return task;
}

static uint32_t fade(unsigned first, unsigned count, unsigned duration,
                     const uint16_t *table, unsigned kind) {
    uint32_t task, previous;
    unsigned last, before;
    if (live->magic != MAGIC) ffta_art_heap_reset();
    last=((first&65535)+(count&65535)-1)&65535;
    if(last>511)last=511;
    ffta_art_variants_track(&live->variants,&live->bindings,
        (const uint16_t *)0x03003a60u,ffta_art_native_reference,ffta_art_custom_colors,
        first&65535,last,ffta_art_custom_mask,live->visible_colors);
    previous = live->fade_command;
    live->fade_command = kind;
    if (kind == 1) task = ffta_art_original_fade_black(first, count, duration);
    else if (kind == 2) task = ffta_art_original_fade_white(first, count, duration);
    else task = ffta_art_original_fade_table(first, count, duration, table);
    live->fade_command = previous;
    first &= 65535;
    last = (first + (count & 65535) - 1) & 65535;
    if (last > 511) last = 511;
    before = live->bindings.unsupported;
#ifdef FFTA_ART_PROVISIONAL_HISTORY
    if(kind==3 && (duration&65535)<=255 && task)
        ffta_art_provisional_reconcile(&live->variants,&live->bindings,
            live->confirmed_keys,first,last,table);
#endif
    ffta_art_binding_start_mapped(&live->bindings, first, last, duration & 65535,
                            task, kind, table, ffta_art_custom_colors, live->variants.key);
    live->target_refusals += live->bindings.unsupported - before;
#ifdef FFTA_ART_TRACE_TARGET
    if(live->bindings.unsupported!=before) {
        volatile unsigned *trace=(volatile unsigned *)((uintptr_t)live+sizeof(*live));
        trace[0]=0x54415247;trace[2]=first;trace[3]=last;trace[4]=duration;
        trace[5]=task;trace[6]=kind;trace[7]=(uintptr_t)table;
        trace[8]=(uintptr_t)&live->bindings;trace[9]=(uintptr_t)&live->variants;
        trace[1]=4;
        for(;;)__asm__ volatile("nop");
    }
#endif
    return task;
}

uint32_t ffta_art_live_fade_black(unsigned first, unsigned count, unsigned duration) {
    return fade(first, count, duration, (const uint16_t *)0, 1);
}
uint32_t ffta_art_live_fade_white(unsigned first, unsigned count, unsigned duration) {
    return fade(first, count, duration, (const uint16_t *)0, 2);
}
uint32_t ffta_art_live_fade_table(unsigned first, unsigned count, unsigned duration, const uint16_t *table) {
    return fade(first, count, duration, table, 3);
}

static uint32_t transform(unsigned first, unsigned count, unsigned duration,
        unsigned red, unsigned green, unsigned blue, unsigned kind) {
    uint32_t task, previous;
    unsigned last, before;
    if (live->magic != MAGIC) ffta_art_heap_reset();
    last=((first&65535)+(count&65535)-1)&65535;
    if(last>511)last=511;
    ffta_art_variants_track(&live->variants,&live->bindings,
        (const uint16_t *)0x03003a60u,ffta_art_native_reference,ffta_art_custom_colors,
        first&65535,last,ffta_art_custom_mask,live->visible_colors);
    previous = live->fade_command;
    live->fade_command = kind;
    if (kind == 4) task = ffta_art_original_fade_gray(first, count, duration);
    else if (kind == 5) task = ffta_art_original_fade_tint(first, count, duration);
    else if (kind == 6) task = ffta_art_original_fade_rgb(first, count, duration, red, green, blue);
    else if(kind==7) task = ffta_art_original_fade_solid(first, count, duration, red, green, blue);
    else if(kind==8) task = ffta_art_original_fade_blend(first,count,duration,red,green,blue);
    else if(kind==9) task = ffta_art_original_fade_brighten(first,count,duration,red);
    else if(kind==10) task = ffta_art_original_fade_darken(first,count,duration,red);
    else if(kind==11) task = ffta_art_original_fade_exposure(first,count,duration,red);
    else task = ffta_art_original_fade_exposure_rgb(first,count,duration,red,green,blue);
    live->fade_command = previous;
    first &= 65535;
    last = (first + (count & 65535) - 1) & 65535;
    if (last > 511) last = 511;
    before = live->bindings.unsupported;
    ffta_art_binding_transform(&live->bindings, first, last, duration & 65535,
        task, kind, red, green, blue);
    live->target_refusals += live->bindings.unsupported - before;
    return task;
}
uint32_t ffta_art_live_fade_gray(unsigned first, unsigned count, unsigned duration) {
    return transform(first, count, duration, 0, 0, 0, 4);
}
uint32_t ffta_art_live_fade_tint(unsigned first, unsigned count, unsigned duration) {
    return transform(first, count, duration, 294, 273, 204, 5);
}
uint32_t ffta_art_live_fade_rgb(unsigned first, unsigned count, unsigned duration,
        unsigned red, unsigned green, unsigned blue) {
    return transform(first, count, duration, red, green, blue, 6);
}
uint32_t ffta_art_live_fade_solid(unsigned first, unsigned count, unsigned duration,
        unsigned red, unsigned green, unsigned blue) {
    return transform(first, count, duration, red, green, blue, 7);
}

uint32_t ffta_art_live_fade_blend(unsigned first,unsigned count,unsigned duration,
        unsigned color,unsigned weight,unsigned original) {
    return transform(first,count,duration,color,weight,original,8);
}
uint32_t ffta_art_live_fade_brighten(unsigned first,unsigned count,unsigned duration,unsigned amount) {
    return transform(first,count,duration,amount,0,0,9);
}
uint32_t ffta_art_live_fade_darken(unsigned first,unsigned count,unsigned duration,unsigned amount) {
    return transform(first,count,duration,amount,0,0,10);
}
uint32_t ffta_art_live_fade_exposure(unsigned first,unsigned count,unsigned duration,unsigned amount) {
    return transform(first,count,duration,amount,amount,amount,11);
}
uint32_t ffta_art_live_fade_exposure_rgb(unsigned first,unsigned count,unsigned duration,
        unsigned red,unsigned green,unsigned blue) {
    return transform(first,count,duration,red,green,blue,12);
}

static uint32_t table_transform(unsigned first,unsigned count,unsigned duration,
        const uint16_t *table,unsigned red,unsigned green,unsigned blue,unsigned kind) {
    unsigned last,previous,before;uint32_t task;
    if(live->magic!=MAGIC)ffta_art_heap_reset();
    last=((first&65535)+(count&65535)-1)&65535;if(last>511)last=511;
    ffta_art_variants_track(&live->variants,&live->bindings,
        (const uint16_t *)0x03003a60u,ffta_art_native_reference,ffta_art_custom_colors,
        first&65535,last,ffta_art_custom_mask,live->visible_colors);
    previous=live->fade_command;live->fade_command=kind;
    if(kind==13)task=ffta_art_original_fade_table_exposure(first,count,duration,table,red,green,blue);
    else task=ffta_art_original_fade_table_blend(first,count,duration,table,red,green,blue);
    live->fade_command=previous;
    before=live->bindings.unsupported;
#ifdef FFTA_ART_PROVISIONAL_HISTORY
    if((duration&65535)<=255 && task)
        ffta_art_provisional_reconcile(&live->variants,&live->bindings,
            live->confirmed_keys,first&65535,last,table);
#endif
    ffta_art_binding_table_transform(&live->bindings,first&65535,last,duration&65535,
        task,kind,table,red,green,blue,ffta_art_custom_colors,live->variants.key);
    live->target_refusals+=live->bindings.unsupported-before;
    return task;
}
uint32_t ffta_art_live_fade_table_exposure(unsigned first,unsigned count,unsigned duration,
        const uint16_t *table,unsigned red,unsigned green,unsigned blue) {
    return table_transform(first,count,duration,table,red,green,blue,13);
}
uint32_t ffta_art_live_fade_table_blend(unsigned first,unsigned count,unsigned duration,
        const uint16_t *table,unsigned color,unsigned weight,unsigned original) {
    return table_transform(first,count,duration,table,color,weight,original,14);
}

static void retire_task(uint32_t task) {
    unsigned i;
    if(live->magic!=MAGIC)return;
    for(i=0;i<FFTA_ART_HISTORY_SLOTS;++i)if(live->bindings.entry[i].task==task)
        live->bindings.entry[i].task=0;
}
uint32_t ffta_art_live_fade_delete(uint32_t task) {
    uint32_t result=(uint32_t)__builtin_return_address(0);
    ffta_art_original_fade_delete(task);
    retire_task(task);
    return result;
}
uint32_t ffta_art_live_fade_collect(uint32_t task) {
    uint32_t result=ffta_art_original_fade_collect(task);
    if(!result)retire_task(task);
    return result;
}
uint32_t ffta_art_live_fade_delete_all(void) {
    unsigned i;uint32_t result=(uint32_t)__builtin_return_address(0);
    ffta_art_original_fade_delete_all();
    if(live->magic==MAGIC)for(i=0;i<FFTA_ART_HISTORY_SLOTS;++i)live->bindings.entry[i].task=0;
    return result;
}
uint32_t ffta_art_live_fade_cancel(unsigned first,unsigned last,unsigned types) {
    unsigned i;uint32_t result=(uint32_t)__builtin_return_address(0);
    ffta_art_original_fade_cancel(first,last,types);
    /* Full deletion already retired its handle through the delete hook. For
     * surviving tasks, only bindings wholly removed from the new range stop. */
    if(live->magic==MAGIC)for(i=0;i<FFTA_ART_HISTORY_SLOTS;++i) {
        FFTA_ArtBinding *entry=&live->bindings.entry[i];
        if(entry->task) {
            const uint16_t *task=(const uint16_t *)entry->task;
            unsigned index=256+entry->bank*16;
            if(task[3]>index+15 || task[4]<index)entry->task=0;
        }
    }
    return result;
}

void ffta_art_live_fade_tick(uint16_t *task) {
    unsigned before = task[6], flags = task[1],first=task[3],last=task[4];
    ffta_art_original_fade_tick(task);
    if (live->magic == MAGIC) {
        unsigned unsupported = live->bindings.unsupported;
        ffta_art_binding_tick_range(&live->bindings, (uint32_t)task, before, task[6], task[0], flags,first,last);
        live->tick_refusals += live->bindings.unsupported - unsupported;
    }
}

static void track_rotation(uint16_t *task) {
    if(live->magic!=MAGIC)ffta_art_heap_reset();
    ffta_art_variants_track(&live->variants,&live->bindings,
        (const uint16_t *)0x03003a60u,ffta_art_native_reference,ffta_art_custom_colors,
        task[3]&~15u,task[4]|15u,ffta_art_custom_mask,live->visible_colors);
}
uint32_t ffta_art_live_fade_rotate(uint16_t *task) {
    uint32_t result=(uint32_t)__builtin_return_address(0);
    unsigned first=task[3],last=task[4],right=task[1]&2,steps=0;
    track_rotation(task);
    if(task[9]==1)steps=((const uint8_t *)task)[28];
    ffta_art_original_fade_rotate(task);
    if(steps)ffta_art_binding_rotate(&live->bindings,first,last,right,steps,0,0);
    return result;
}
uint32_t ffta_art_live_fade_cycle(uint16_t *task) {
    uint32_t result=(uint32_t)__builtin_return_address(0);
    unsigned first=task[3],last=task[4],right=task[1]&2,step=task[13]==1;
    const uint8_t *table=*(const uint8_t **)((uint8_t *)task+28);
    unsigned value=*(const uint16_t *)(table+task[16]);
    track_rotation(task);
    ffta_art_original_fade_cycle(task);
    if(step)ffta_art_binding_rotate(&live->bindings,first,last,right,1,1,value);
    return result;
}
