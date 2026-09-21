#include "art-palette-plan.h"
#ifdef FFTA_ART_DMA_TILE_CACHE
#include "art-palette-dirty.h"
#endif
extern const uint16_t ffta_art_pixel_banks[65536];
extern void ffta_art_copy_words(void *,const void *,unsigned);
_Static_assert(sizeof(FFTA_ArtPaletteCache)==2124,"cache reservation");

#ifndef FFTA_ART_FAST_BANK_SCAN
static unsigned same_tile(const uint32_t *a, const uint32_t *b) {
 unsigned k;
 for(k=0;k<16;k+=4)
  if((a[k]^b[k]) | (a[k+1]^b[k+1]) | (a[k+2]^b[k+2]) | (a[k+3]^b[k+3]))return 0;
 return 1;
}

static unsigned tile_mask(const uint32_t *block, FFTA_ArtPaletteCache *cache, unsigned tile) {
 unsigned k,used=0;
 uint32_t *saved=0;
#ifdef FFTA_ART_DMA_TILE_CACHE
 /* Only a cache explicitly initialized by the tracked live path has this
  * ABI. Generic primitive callers still validate every byte as before. */
 if(cache && FFTA_ART_DIRTY_CACHE(cache))
  return ffta_art_dirty_mask(cache,block,((unsigned)block-0x06010000u)/64);
#endif
 if(cache && tile<32) {
  saved=cache->pixels+tile*16;
  if(cache->valid&(1u<<tile)) {
   if(same_tile(saved,block))return cache->masks[tile];
  }
 }
 for(k=0;k<16;k+=4) {
  const uint16_t *pixels=(const uint16_t *)(block+k);
  if(!(block[k]|block[k+1]|block[k+2]|block[k+3]))continue;
  used|=ffta_art_pixel_banks[pixels[0]];
  used|=ffta_art_pixel_banks[pixels[1]];
  used|=ffta_art_pixel_banks[pixels[2]];
  used|=ffta_art_pixel_banks[pixels[3]];
  used|=ffta_art_pixel_banks[pixels[4]];
  used|=ffta_art_pixel_banks[pixels[5]];
  used|=ffta_art_pixel_banks[pixels[6]];
  used|=ffta_art_pixel_banks[pixels[7]];
 }
 if(saved) {
  for(k=0;k<16;++k)saved[k]=block[k];
  cache->masks[tile]=used;
  cache->valid|=1u<<tile;
 }
 return used;
}
#endif

/* The native compositor also hides unused entries at (248,-88) as an ordinary
 * 8x8 object. Validate its exact three attributes and absent owner tag before
 * trimming. Keep every interior hole and later enabled entry in the prefix. */
static unsigned object_count(const FFTA_ArtPaletteFrame *f) {
 unsigned count=128;
 while(count) {
  unsigned i=count-1,a=f->oam[i*4];
  if((a&0x300)!=0x200 &&
     !(((const uint32_t *)f->oam)[i*2]==0x00f800a8u &&
       f->oam[i*4+2]==0 && f->owner[i]==255))break;
  --count;
 }
 return count;
}

#ifdef FFTA_ART_FUSED_COMPOSE
static unsigned plan_inputs(const FFTA_ArtPaletteFrame *f,FFTA_ArtPaletteCache *cache,
                            unsigned count,const FFTA_ArtOamDemands *prepared) {
#else
static unsigned plan(const FFTA_ArtPaletteFrame *f, FFTA_ArtPaletteCache *cache, unsigned count) {
#endif
 static const uint8_t widths[12]={8,16,32,64,16,32,32,64,8,8,16,32};
 static const uint8_t heights[12]={8,16,32,64,8,8,16,32,16,32,32,64};
 FFTA_ArtPalettePlan p;
 unsigned i,used=0,wanted=0;
#if defined(FFTA_ART_GROUPED_PALETTES) && defined(FFTA_ART_FAST_BANK_SCAN)
 /* The same relocation-free ARM scanner handles every 8bpp object in this
  * invocation. Copy its authenticated 512 bytes once, instead of once per
  * object. This is stack-local code, never a cross-frame pixel/code cache.
  * Retain the original scoped wrapper when the caller lacks IWRAM room. */
 unsigned (*scoped_scan)(const unsigned *)=0;
#endif
#ifdef FFTA_ART_NATIVE_OAM_PREFIX
 /* Authenticated native12BC leaves the omitted tail at00f800a8/0000.
  * Those ordinary offscreen sentinels still reserve palette bank0. */
 if(count<128)used=1;
#endif
 if(!f->one_dimensional || !f->custom_count || f->custom_count>FFTA_ART_HISTORY_SLOTS)return 0;
 for(i=0;i<FFTA_ART_HISTORY_SLOTS;i++)p.bank[i]=255;
#ifdef FFTA_ART_ARM_OAM_SCAN
 FFTA_ArtOamDemands scratch;
 const FFTA_ArtOamDemands *demands=&scratch;
 extern unsigned ffta_art_oam_demands(const FFTA_ArtPaletteFrame *,void *,unsigned);
#ifdef FFTA_ART_FUSED_COMPOSE
 if(prepared) {
  if(prepared->count>128 || (prepared->requested>>f->custom_count))return 0;
  for(i=0;i<prepared->count;++i)if(prepared->indices[i]>=count)return 0;
  demands=prepared;
 } else
#endif
 if(!ffta_art_oam_demands(f,&scratch,count))return 0;
 used|=demands->occupied;wanted=demands->requested;count=demands->count;
 for(i=0;i<count;i++) {
  unsigned object=demands->indices[i];
  unsigned a=f->oam[object*4],b=f->oam[object*4+1],c=f->oam[object*4+2];
  unsigned shape=a>>14,size=b>>14;
  {
#else
 for(i=0;i<count;i++) {
#ifdef FFTA_ART_FAST_OAM_PLAN
  /* Native unused slots still reserve bank0 in the full planner. Fold only
   * four exact sentinel entries, ignoring their unrelated affine words.
   * Re-read current OAM/tags every call: this is not a lifetime cache. */
  if(i+4<=count && !((uintptr_t)(f->owner+i)&3u)) {
   typedef uint32_t OamWord __attribute__((may_alias));
   const OamWord *q=(const OamWord *)(f->oam+i*4);
   if(*(const OamWord *)(f->owner+i)==0xffffffffu &&
      q[0]==0x00f800a8u && q[2]==0x00f800a8u &&
      q[4]==0x00f800a8u && q[6]==0x00f800a8u &&
      !((q[1]|q[3]|q[5]|q[7])&65535u)) {
    used|=1;i+=3;continue;
   }
  }
#endif
  unsigned a=f->oam[i*4],b=f->oam[i*4+1],c=f->oam[i*4+2];
  unsigned id=f->owner[i],shape=a>>14,size=b>>14;
  if((a&0x300)==0x200)continue;
  if(shape==3)return 0;
  if(id!=255) {
   /* Current imported bodies are one non-affine32x32 4bpp object. */
   if(id>=f->custom_count || (a&0x2100) || shape || size!=2)return 0;
   wanted|=1u<<id;
  } else if(a&0x2000) {
#endif
   unsigned n=widths[shape*4+size]*heights[shape*4+size];
   unsigned start=(c&1022)*32;
#ifndef FFTA_ART_FAST_BANK_SCAN
   unsigned j,tile=0;
#endif
   if(start+n>32768)return 0;
   /*8bpp ignores attr2's palette nibble. Reserve the actual nonzero
    * color indices in every potentially displayed source tile. */
   {
    unsigned width=widths[shape*4+size],height=heights[shape*4+size];
    unsigned row,col;
    int x=(int)(b&511),y=(int)(a&255);
    if(x>=256)x-=512;
    if(y>=160)y-=256;
#ifdef FFTA_ART_FAST_BANK_SCAN
    /* Visible whole source tiles form a rectangular range, including flips.
     * Scan that range once with exact current bytes. Affine/mosaic keep the
     * full source footprint, as in the original conservative planner. */
    {
     extern unsigned ffta_art_bank_span_fast(const unsigned *);
     unsigned left=width,right=0,top=height,bottom=0;
     for(col=0;col<width;col+=8) {
      int px=x+(int)((b&0x1000)?width-8-col:col);
      if(!(a&0x1100) && (px>=240 || px+8<=0))continue;
      if(left==width)left=col;
      right=col+8;
     }
     for(row=0;row<height;row+=8) {
      int py=y+(int)((b&0x2000)?height-8-row:row);
      if(!(a&0x1100) && (py>=160 || py+8<=0))continue;
      if(top==height)top=row;
      bottom=row+8;
     }
     if(left<right && top<bottom) {
      const unsigned span[5]={(unsigned)(f->obj+start+top*width+left*8),
                       (right-left)*2,(bottom-top)/8,width*8,(unsigned)cache};
#if defined(FFTA_ART_GROUPED_PALETTES) && defined(FFTA_ART_FAST_BANK_SCAN)
      if(!scoped_scan) {
       unsigned current_sp;
       __asm__ volatile("mov %0,sp":"=r"(current_sp));
       scoped_scan=ffta_art_bank_span_fast;
       /* Native resident code ends at 6d68. Leave 512 interrupt bytes and
        * 64 bytes for the scanner's 48-byte frame and call interworking. */
       if(current_sp>=0x030071b0u && current_sp<=0x03008000u) {
        extern unsigned ffta_art_bank_span(const unsigned *);
        /* Allocate only after the room check; even the fallback must not
         * push a fixed 512-byte C frame into native resident code. */
        uint32_t *scanner_words=__builtin_alloca(512);
        ffta_art_copy_words(scanner_words,(const void *)ffta_art_bank_span,128);
        scoped_scan=(unsigned (*)(const unsigned *))scanner_words;
       }
      }
      used|=scoped_scan(span);
#else
      used|=ffta_art_bank_span_fast(span);
#endif
     }
    }
#else
    for(row=0;row<height;row+=8)for(col=0;col<width;col+=8) {
     /* Normal OBJ is tiled, with optional flips. Entirely off-screen tiles
      * cannot consume a displayed color. Keep partially clipped tiles whole
      * (conservative); affine/mosaic OBJ retain the complete footprint. */
     if(!(a&0x1100)) {
      int px=x+(int)((b&0x1000)?width-8-col:col);
      int py=y+(int)((b&0x2000)?height-8-row:row);
      if(px>=240 || px+8<=0 || py>=160 || py+8<=0)continue;
     }
     j=start+row*width+col*8;
     used|=tile_mask((const uint32_t *)(f->obj+j),cache,tile++);
    }
#endif
   }
  }
#ifndef FFTA_ART_ARM_OAM_SCAN
  else used|=1u<<(c>>12);
#endif
 }
 p.occupied=used;p.requested=wanted;p.reserved=0;
 for(i=0;i<f->custom_count;i++)if(wanted&(1u<<i)) {
  unsigned slot;
  for(slot=0;slot<16;slot++)if(!(used&(1u<<slot)))break;
  if(slot==16)return 0;
  p.bank[i]=slot;used|=1u<<slot;
 }
 /* Keep the freestanding ROM module independent of a C-library memcpy. */
 {
  volatile FFTA_ArtPalettePlan *target=f->plan;
  target->occupied=p.occupied;target->requested=p.requested;
  for(i=0;i<FFTA_ART_HISTORY_SLOTS;i++)target->bank[i]=p.bank[i];
  target->reserved=0;
 }
 return 1;
}

#ifdef FFTA_ART_FUSED_COMPOSE
static unsigned plan(const FFTA_ArtPaletteFrame *f,FFTA_ArtPaletteCache *cache,unsigned count) {
 return plan_inputs(f,cache,count,0);
}
#endif
unsigned ffta_art_palette_plan(const FFTA_ArtPaletteFrame *f) {return plan(f,0,128);}

static void apply(FFTA_ArtPaletteFrame *f, unsigned count) {
 typedef uint32_t TagWord __attribute__((may_alias));
 unsigned i;
 for(i=0;i<f->custom_count;i++)if(f->plan->requested&(1u<<i)) {
  unsigned slot=f->plan->bank[i];
  ffta_art_copy_words(f->palette+slot*16,f->custom+i*16,8);
 }
 for(i=0;i<count;i++) {
  unsigned id,a;
  /* A validated unowned group needs no OAM read or write. Keep arbitrary
   * tag alignment and trailing entries on the scalar path. This does not
   * change the preceding full-frame palette conflict validation. */
  if(i+4<=count && !((uintptr_t)(f->owner+i)&3u) &&
     *(const TagWord *)(f->owner+i)==0xffffffffu) {i+=3;continue;}
  id=f->owner[i];
  if(id==255)continue;
  a=f->oam[i*4];
  if((a&0x300)==0x200)continue;
  f->oam[i*4+2]=(f->oam[i*4+2]&0xfff)|(f->plan->bank[id]<<12);
 }
}

unsigned ffta_art_palette_apply_cached(FFTA_ArtPaletteFrame *f, FFTA_ArtPaletteCache *cache) {
#ifdef FFTA_ART_FAST_OAM_PLAN
 unsigned count=128;
#else
 unsigned count=object_count(f);
#endif
 if(!plan(f,cache,128))return 0;
 apply(f,count);
 return 1;
}

unsigned ffta_art_palette_apply(FFTA_ArtPaletteFrame *f) {return ffta_art_palette_apply_cached(f,0);}

#ifdef FFTA_ART_REPEAT_FRAME
/* Private caller has freshly proved ownership, unchanged palette demands,
 * history mapping and every consumed pixel byte.
 * Hardware native colors and displayed custom phase are always fresh inputs. */
void ffta_art_palette_apply_validated(FFTA_ArtPaletteFrame *f,uint16_t *backup) {
 for(unsigned i=0;i<f->custom_count;++i)if(f->plan->requested&(1u<<i)) {
  unsigned slot=f->plan->bank[i];
  ffta_art_copy_words(backup+slot*16,f->palette+slot*16,8);
 }
 apply(f,128);
}
#endif

/* Separate the rare8bpp path so the common disabled/4bpp OAM loop keeps
 * its pointers/counters in registers rather than the tile loop's stack. */
static __attribute__((noinline)) unsigned conflict8(const uint8_t *obj,
        unsigned a, unsigned b, unsigned c, unsigned bank
#ifdef FFTA_ART_DMA_TILE_CACHE
        , FFTA_ArtPaletteCache *cache
#endif
        ) {
 static const uint8_t widths[12]={8,16,32,64,16,32,32,64,8,8,16,32};
 static const uint8_t heights[12]={8,16,32,64,8,8,16,32,16,32,32,64};
 unsigned index=(a>>14)*4+(b>>14),width=widths[index],height=heights[index];
 unsigned start=(c&1022)*32,row,col,first=width,last=0;
 int x=(int)(b&511),y=(int)(a&255);
 extern unsigned ffta_art_span_has_bank_fast(const uint32_t *, unsigned, unsigned);
 if(!bank || start+width*height>32768)return 1;
 if(x>=256)x-=512;
 if(y>=160)y-=256;
 /* Visible source tiles in each normal row form one contiguous span, even
  * under horizontal flip. Partial tiles remain included in full. */
 for(col=0;col<width;col+=8) {
  int px=x+(int)((b&0x1000)?width-8-col:col);
  if(!(a&0x1100) && (px>=240 || px+8<=0))continue;
  if(first==width)first=col;
  last=col+8;
 }
 if(first==width)return 0;
#if defined(FFTA_ART_JOINED_ROWS) || defined(FFTA_ART_RECT_CONFLICT)
 /* Compute the same conservative visible row range once. Full-width rows can
  * join into one linear scan; the rectangle variant also handles clipped rows
  * with their original stride, copying the exact leaf once. No pixel or
  * lifetime cache is added. */
#ifdef FFTA_ART_RECT_CONFLICT
 {
#else
 if(first==0 && last==width) {
#endif
  unsigned top=height,bottom=0;
  for(row=0;row<height;row+=8) {
   int py=y+(int)((b&0x2000)?height-8-row:row);
   if(!(a&0x1100) && (py>=160 || py+8<=0))continue;
   if(top==height)top=row;
   bottom=row+8;
  }
  if(top==height)return 0;
#ifdef FFTA_ART_RECT_CONFLICT
  extern unsigned ffta_art_rect_has_bank_fast(const unsigned *);
  const unsigned span[5]={(unsigned)(obj+start+top*width+first*8),
       (last-first)*2,(bottom-top)/8,width*8,bank*0x10101010u};
  return ffta_art_rect_has_bank_fast(span);
#else
  return ffta_art_span_has_bank_fast((const uint32_t *)(obj+start+top*width),
                                    bank*0x10101010u,(bottom-top)*width/4);
#endif
 }
#endif
 for(row=0;row<height;row+=8) {
  int py=y+(int)((b&0x2000)?height-8-row:row);
  if(!(a&0x1100) && (py>=160 || py+8<=0))continue;
#ifdef FFTA_ART_DMA_TILE_CACHE
  if(cache && FFTA_ART_DIRTY_CACHE(cache)) {
   for(col=first;col<last;col+=8) {
    const uint32_t *block=(const uint32_t *)(obj+start+row*width+col*8);
    if(ffta_art_dirty_mask(cache,block,((unsigned)block-0x06010000u)/64)&(1u<<bank))return 1;
   }
   continue;
  }
#endif
  if(ffta_art_span_has_bank_fast((const uint32_t *)(obj+start+row*width+first*8),
                            bank*0x10101010u,(last-first)*2))return 1;
 }
 return 0;
}

static unsigned preferred(FFTA_ArtPaletteFrame *f, unsigned count
#ifdef FFTA_ART_DMA_TILE_CACHE
                          , FFTA_ArtPaletteCache *cache
#endif
                          ) {
 unsigned wanted,owner=0,bank,i,found=0;
 const volatile uint16_t *objects=f->oam;
 if(!f->one_dimensional || !f->custom_count || f->custom_count>FFTA_ART_HISTORY_SLOTS)return 0;
 wanted=f->plan->requested;
 if(!wanted || (wanted&(wanted-1)) || wanted>=(1u<<f->custom_count))return 0;
 while(!(wanted&(1u<<owner)))++owner;
 bank=f->plan->bank[owner];
 /* Full planning still accounts for the native bank0 offscreen sentinels.
  * Its diagnostics/allocation remain byte-compatible with the baseline. */
 if(!bank || bank>=16)return 0;
 for(i=0;i<count;++i) {
  unsigned a=objects[i*4],b,c,id;
  if((a&0x300)==0x200)continue;
  if((a>>14)==3)return 0;
  id=f->owner[i];b=objects[i*4+1];c=objects[i*4+2];
  if(id!=255) {
   if(id!=owner || (a&0xe100) || (b>>14)!=2)return 0;
   found=1;
  } else if(a&0x2000) {
   if(conflict8(f->obj,a,b,c,bank
#ifdef FFTA_ART_DMA_TILE_CACHE
                ,cache
#endif
                ))return 0;
  } else if((c>>12)==bank)return 0;
 }
 return found;
}

unsigned ffta_art_palette_reapply(FFTA_ArtPaletteFrame *f) {
 unsigned count=object_count(f);
 if(!preferred(f,count
#ifdef FFTA_ART_DMA_TILE_CACHE
               ,0
#endif
               ))return 0;
 apply(f,count);return 1;
}

#ifdef FFTA_ART_NATIVE_OAM_PREFIX
unsigned ffta_art_palette_live_apply_prefix(FFTA_ArtPaletteFrame *f,
        FFTA_ArtPaletteCache *cache,uint16_t *backup,unsigned count) {
 unsigned i;
 if(count>128)return 0;
#else
unsigned ffta_art_palette_live_apply(FFTA_ArtPaletteFrame *f,
                                    FFTA_ArtPaletteCache *cache, uint16_t *backup) {
#ifdef FFTA_ART_FAST_OAM_PLAN
 /* The preferred path only supports one history. Full planning already
  * visits every slot, and apply skips four unowned tags at a time; paying a
  * separate scalar tail scan in that case adds no information. */
 unsigned wanted=f->plan->requested;
 unsigned i,count=(!wanted || (wanted&(wanted-1)))?128:object_count(f);
#else
 unsigned i,count=object_count(f);
#endif
#endif
 if(!preferred(f,count
#ifdef FFTA_ART_DMA_TILE_CACHE
               ,cache
#endif
               ) && !plan(f,cache,
#ifdef FFTA_ART_NATIVE_OAM_PREFIX
                           count
#else
                           128
#endif
                           ))return 0;
#ifdef FFTA_ART_SCOPED_FRAME
 if(!(((uintptr_t)f->palette|(uintptr_t)f->custom|(uintptr_t)backup)&3u)) {
  extern void ffta_art_frame_publish(FFTA_ArtPaletteFrame *,uint16_t *,unsigned);
  ffta_art_frame_publish(f,backup,count);return 1;
 }
#endif
 for(i=0;i<f->custom_count;++i)if(f->plan->requested&(1u<<i)) {
  unsigned slot=f->plan->bank[i];
  ffta_art_copy_words(backup+slot*16,f->palette+slot*16,8);
 }
 apply(f,count);return 1;
}
#ifdef FFTA_ART_NATIVE_OAM_PREFIX
unsigned ffta_art_palette_live_apply(FFTA_ArtPaletteFrame *f,
        FFTA_ArtPaletteCache *cache,uint16_t *backup) {
 return ffta_art_palette_live_apply_prefix(f,cache,backup,128);
}
#endif

#ifdef FFTA_ART_FUSED_COMPOSE
#ifdef FFTA_ART_PREPARED_PREFERENCE
/* Ownership classification and variant remapping just authenticated these
 * demands in this invocation. Retain the old preferred bank and diagnostics,
 * but do not reclassify every4bpp object. Every8bpp pixel conflict remains an
 * exact current-byte scan. No classification survives a composition call. */
static unsigned preferred_inputs(const FFTA_ArtPaletteFrame *f,
                                  const FFTA_ArtOamDemands *d,unsigned count) {
 unsigned wanted=f->plan->requested,owner=0,bank;
 if(!f->one_dimensional || !f->custom_count ||
    f->custom_count>FFTA_ART_HISTORY_SLOTS || !wanted ||
    (wanted&(wanted-1)) || wanted>=(1u<<f->custom_count) ||
    wanted!=d->requested)return 0;
 while(!(wanted&(1u<<owner)))++owner;
 bank=f->plan->bank[owner];
 if(!bank || bank>=16 || (d->occupied&(1u<<bank)))return 0;
 for(unsigned i=0;i<d->count;++i) {
  unsigned object=d->indices[i];
  if(object>=count)return 0;
  unsigned a=f->oam[object*4],b=f->oam[object*4+1],c=f->oam[object*4+2];
  if((a>>14)==3 || conflict8(f->obj,a,b,c,bank))return 0;
 }
 return 1;
}
#endif
#ifdef FFTA_ART_PACKED_PLAN
/* Same-invocation classification already proved there are no 8bpp consumers.
 * Build the complete original plan locally, preserving failure atomicity and
 * its diagnostic fields. No previous-frame or graphics-lifetime assumption. */
static unsigned plan_four(const FFTA_ArtPaletteFrame *f,
                          const FFTA_ArtOamDemands *d,unsigned count) {
 typedef uint32_t PlanWord __attribute__((may_alias));
 union {uint32_t words[5];uint8_t bytes[20];} banks;
 unsigned i,slot=0,used=d->occupied|(count<128),wanted=d->requested;
 _Static_assert(FFTA_ART_HISTORY_SLOTS==20,"packed twenty-history plan");
 if(!f->one_dimensional || !f->custom_count || f->custom_count>20 ||
    (wanted>>f->custom_count))return 0;
 for(i=0;i<5;++i)banks.words[i]=0xffffffffu;
 for(i=0;i<f->custom_count;++i)if(wanted&(1u<<i)) {
  /* Allocations are monotonically increasing: every lower available slot
   * was consumed by an earlier history in this same plan. */
  while(slot<16 && (used&(1u<<slot)))++slot;
  if(slot==16)return 0;
  banks.bytes[i]=(uint8_t)slot;used|=1u<<slot;
 }
 f->plan->occupied=(uint16_t)(d->occupied|(count<128));
 f->plan->requested=wanted;
 for(i=0;i<5;++i)((PlanWord *)f->plan->bank)[i]=banks.words[i];
 f->plan->reserved=0;
 return 1;
}
#endif
unsigned ffta_art_palette_live_apply_fused(FFTA_ArtPaletteFrame *f,
        FFTA_ArtPaletteCache *cache,uint16_t *backup,const FFTA_ArtOamDemands *demands,
        unsigned count) {
 extern void ffta_art_frame_publish(FFTA_ArtPaletteFrame *,uint16_t *,unsigned);
 /* This caller owns same-invocation demands and uses native aligned palette
  * storage. Retain preferred-bank behavior, including its full validation. */
 if(count>128 || demands->count>128)return 0;
#ifdef FFTA_ART_PREPARED_PREFERENCE
 if(!preferred_inputs(f,demands,count)) {
#else
 if(!preferred(f,count)) {
#endif
#ifdef FFTA_ART_PACKED_PLAN
  if(!demands->count) {if(!plan_four(f,demands,count))return 0;}
  else
#endif
  if(!plan_inputs(f,cache,count,demands))return 0;
 }
 ffta_art_frame_publish(f,backup,count);return 1;
}
#endif
