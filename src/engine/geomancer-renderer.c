#include "geomancer-renderer.h"
#include "geomancer-compositor.h"
#include "geomancer-animation.h"
#include "geomancer-assets.h"
#include "battle-workspace.h"
#include "job-state.h"

#define MAGIC 0x31524746u
#define MAP ((uint8_t *)0x02007f40u)
#define LOCK (*(volatile uint8_t *)0x02009198u)
#define SHADOW ((volatile uint16_t *)0x03000940u)
typedef struct {
 unsigned magic,self,manager,heap,map,published,retiring,dirty;
 int camera_x,camera_y;
 const FFTA_GeoAsset *asset;
 unsigned animation_stamp[4];
 uint32_t inherited_tail[8];
 uint32_t retained[8][8];
 uint8_t board[256];
 FFTA_GeoProjection projection[256];
 FFTA_GeoScene scene;
 FFTA_GeoAnimationSource animation;
 FFTA_GeoFrame frame;
 uint32_t field_inputs[36];
 unsigned board_valid;
} Renderer;
_Static_assert(sizeof(Renderer)==18332,"Renderer metadata ownership ABI");
#define CACHE_BYTES (FFTA_GEO_CACHE_TILES*32u)
static unsigned half(const void *p){return *(const uint16_t *)p;}
static unsigned word(const void *p){return *(const unsigned *)p;}
static unsigned valid(const void *p,unsigned size){
 uintptr_t a=(uintptr_t)p;return !(a&3u) && a>=0x0200000cu && a<=0x0203f000u-size;
}
static unsigned allocated(const void *p,unsigned size){
 if(!valid(p,size))return 0;
 const uint16_t *h=(const uint16_t *)((uintptr_t)p-12);
 unsigned n=4u*h[3];return h[2]==0x616c && n>=size+12 && n<=size+24 && valid(p,n-12);
}
static Renderer **slot(void){return ffta_battle_workspace(FFTA_WORKSPACE_GEOMANCER);}
static Renderer *owner(void){
 Renderer **s=slot();Renderer *r=s?*s:0;
 return allocated(r,sizeof(*r)) && r->magic==MAGIC && r->self==(unsigned)r &&
  r->manager==(unsigned)ffta_owned_battle_manager() && r->heap==word((void *)0x0200f434u) &&
  allocated(r->frame.graphics,CACHE_BYTES)?r:0;
}
static unsigned map_matches(const Renderer *r){
 return r->map==half((void *)0x02007f10u) && MAP[0]<4 && MAP[1]<4 && MAP[0]!=MAP[1] &&
  MAP[4]==1 && half(MAP+6)==4096 && half(MAP+8)==512 && half(MAP+10)==256 &&
  word(MAP+16)==0x06000000u && word(MAP+20)==0x06007000u && word(MAP+24)==0x06006000u;
}
static void transfer(const void *source,unsigned destination,unsigned bytes){
 if(!bytes)return;
 volatile unsigned *dma=(volatile unsigned *)0x040000d4u;
 dma[0]=(unsigned)source;dma[1]=destination;dma[2]=0x84000000u|(bytes>>2);
 while(dma[2]&0x80000000u){}
}
static void background_size(unsigned size){
 for(unsigned i=0;i<2;i++){
  unsigned bg=MAP[i];SHADOW[1+bg]=(uint16_t)((SHADOW[1+bg]&0x3fffu)|(size<<14));
 }
}
static void native_stream(void){
 ((void (*)(void *,unsigned,unsigned,unsigned,unsigned,unsigned))0x0801b7f9u)
  (MAP,word(MAP+20),word(MAP+24),0x020091a0u,0x0200b1a0u,1);
}
static void restore(Renderer *r){
 if(r->published && map_matches(r)){
  transfer(r->asset->graphics,0x06000000u,r->asset->tiles*32u);
  transfer(r->animation.graphics,0x06000000u,r->asset->prefix_tiles*32u);
  for(unsigned i=0;i<r->asset->retained_count;i++)
   transfer(r->retained[i],0x06000000u+r->asset->retained_ids[i]*32u,32);
  /* Across all native maps,576 is the only visible uninitialized atlas tile.
   * Preserve it even on maps where it is currently hidden: a later map67
   * load inherits it. Cache pixels must never become that inherited source. */
  if(r->asset->tiles<=576)transfer(r->inherited_tail,0x06004800u,32);
  /* The root is detached before entry, so the original native stream is used. */
  native_stream();background_size(MAP[4]);
  ((void (*)(void))0x08019b49u)();
 }
 ffta_geo_animation_end(&r->animation);
}
/* Release bits:1 metadata,2 cache. A native free observer omits the allocation
 * whose original free is already in progress; roots detach before recursion. */
static void retire(unsigned release){
 Renderer *r=owner();if(!r)return;
 unsigned prior=LOCK;LOCK=1;Renderer **s=slot();*s=0;
 restore(r);r->magic=0;
 if(release&2u)((void (*)(void *,void *))0x08007171u)((void *)r->heap,r->frame.graphics);
 if(release&1u)((void (*)(void *,void *))0x08007171u)((void *)r->heap,r);
 LOCK=(uint8_t)prior;
}
void ffta_geo_renderer_retire(void){retire(3);}
extern void *ffta_geo_native_allocate(void *,unsigned);
void *ffta_geo_allocate(void *heap,unsigned bytes){
 /* This optional display cache must never starve native battle work. Preserve
  * the original allocation first; only a real failure reclaims the cache and
  * retries. Field mechanics live in the job bank and are unaffected. The next
  * map update can reconstruct the display when memory is available again. */
 void *result=ffta_geo_native_allocate(heap,bytes);
 if(!result && bytes && heap==*(void **)0x0200f434u && !LOCK && owner()){
  retire(3);result=ffta_geo_native_allocate(heap,bytes);
 }
 return result;
}
void ffta_geo_renderer_free(void *allocation){
 Renderer *r=owner();if(!r || !valid(allocation,0))return;
 if(allocation==r){retire(2);return;}
 if(allocation==r->frame.graphics){retire(1);return;}
 const uint16_t *h=(const uint16_t *)((uintptr_t)allocation-12);
 unsigned size=4u*h[3],a=(unsigned)allocation;
 Renderer **s=slot();
 if(h[2]!=0x616c || size<12 || size-12>0x0203f000u-a)return;
 if(allocation==(void *)((uint8_t *)s-FFTA_WORKSPACE_GEOMANCER) ||
    (a<=r->manager && a+size-12>=r->manager+FFTA_WORKSPACE_MANAGER_BYTES))retire(3);
}
extern void ffta_copy_owners_reset(void);
void ffta_geo_reset_owners(void){retire(3);ffta_copy_owners_reset();}

static unsigned stamp(Renderer *r){
 unsigned changed=0;
 for(unsigned i=0;i<4;i++){
  const uint8_t *c=r->animation.bindings[i].controller;
  /* Tick changes frame before DMA. A zero progress frame has no new
   * source pixels yet, including pumps occupied by native map streaming. */
  if(c && i<r->animation.count && !half(c+12))continue;
  unsigned value=i<r->animation.count?c[4]|(half(c+12)<<8):0;
  if(r->animation_stamp[i]!=value && c){
   /* Native controllers can animate off-screen water throughout a battle.
    * Rebuild only if this stream contributes source pixels to the viewport.
    * Camera/board changes still rebuild unconditionally from current sources. */
   unsigned start=(r->animation.bindings[i].destination-0x06000000u)/32u;
   unsigned end=start+half(c+8)/32u;
   if(end>128)end=128;
   for(unsigned t=start;t<end;t++)if(r->frame.animated_used[t>>5]&(1u<<(t&31u)))changed=1;
  }
  r->animation_stamp[i]=value;
 }
 return changed;
}
static unsigned can_create(void){
 /* Let native scene/cold-load buffers take their stable positions first.
  * Recreate a reclaimed display only at a player command/facing boundary.
  * A queued action can keep its large temporary allocation through many map
  * updates. Retrying construction there rebuilds the board and allocates/frees
  * metadata every frame, despite there being no room for the graphics cache. */
 unsigned phase=half((void *)0x0200f5c4u);
 if(phase!=37 && phase!=47)return 0;
 const uint8_t *command=*(const uint8_t **)0x0200f438u;
 if(!valid(command,28) || command[4]<4 || command[4]>12 ||
    !ffta_job_origin(*(const uint8_t *const *)(command+24)))return 0;
 const uint8_t *wrapper=*(const uint8_t **)0x0200f4ecu;
 if(valid(wrapper,4)){
  const uint8_t *unit=*(const uint8_t *const *)wrapper;
  if(ffta_job_origin(unit) && (unit[0x29]&128u))return 0;
 }
 return 1;
}
static Renderer *create(void){
 unsigned map=half((void *)0x02007f10u);
 if(map>=162 || !ffta_additional_workspace_prepare())return 0;
 Renderer **s=slot();if(!s || *s)return 0;
 const FFTA_GeoAsset *asset=(const FFTA_GeoAsset *)FFTA_GEO_ASSET_BASE+map;
 if(!asset->tiles || asset->tiles>640 || asset->prefix_tiles>128 ||
    asset->prefix_tiles>asset->tiles || asset->retained_count>8)return 0;
 Renderer *r=((Renderer *(*)(unsigned))0x08022841u)(sizeof(Renderer));if(!r)return 0;
 /* Do not zero the entire frame; the compositor overwrites it before publishing. */
 for(unsigned i=0;i<(unsigned)((uint8_t *)&r->frame-(uint8_t *)r);i++)((uint8_t *)r)[i]=0;
 r->board_valid=0;
 for(unsigned i=0;i<36;i++)r->field_inputs[i]=0;
 r->self=(unsigned)r;r->manager=(unsigned)ffta_owned_battle_manager();
 r->heap=word((void *)0x0200f434u);r->map=map;r->asset=asset;
 r->frame.graphics=0;
 if(!map_matches(r))goto fail;
 r->frame.graphics=((void *(*)(unsigned))0x08022841u)(CACHE_BYTES);
 if(!r->frame.graphics)goto fail;
 if(asset->prefix_tiles && !ffta_geo_animation_begin(&r->animation,
     *(uint8_t **)0x0200f1d4u,asset->prefix_tiles))goto fail;
 for(unsigned j=0;j<8;j++)r->inherited_tail[j]=((volatile uint32_t *)0x06004800u)[j];
 for(unsigned i=0;i<asset->retained_count;i++){
  const volatile uint32_t *v=(const volatile uint32_t *)(0x06000000u+asset->retained_ids[i]*32u);
  for(unsigned j=0;j<8;j++)r->retained[i][j]=v[j];
 }
 r->scene.arrangement[0]=(const uint16_t *)0x020091a0u;
 r->scene.arrangement[1]=(const uint16_t *)0x0200b1a0u;
 r->scene.graphics=asset->graphics;r->scene.palette=asset->palette;
 r->scene.projection=r->projection;r->scene.board=r->board;r->scene.tile_count=asset->tiles;
 r->scene.animated_graphics=(const uint32_t *)r->animation.graphics;
 r->scene.animated_tiles=asset->prefix_tiles;r->scene.retained_ids=asset->retained_ids;
 r->scene.retained_graphics=(const uint32_t *)r->retained;r->scene.retained_count=asset->retained_count;
 r->dirty=1;r->frame.ready=0;r->magic=MAGIC;*s=r;return r;
fail:
 if(r->frame.graphics)((void (*)(void *,void *))0x08007171u)((void *)r->heap,r->frame.graphics);
 ((void (*)(void *,void *))0x08007171u)((void *)r->heap,r);return 0;
}
void ffta_geo_renderer_update(unsigned map_state){
 if(map_state!=8){retire(3);return;}
 if(!ffta_owned_battle_manager() || LOCK)return;
 /* The canonical bank is contiguous. Ordinary play has no fields: avoid36
  * repeated ownership/format/division queries on every native map frame. */
 const uint8_t *bank=ffta_job_state((uint8_t *)0x02000080u);unsigned any=0;
 if(bank)for(unsigned i=0;i<FFTA_JOB_UNIT_COUNT;i++)
  any|=bank[i*FFTA_JOB_RECORD_BYTES+FFTA_JOB_GEO_FIELD_FLAGS]&31u;
 if(!any){Renderer *old=owner();if(old)old->retiring=1;return;}
 Renderer *r=owner();
 if(r && !map_matches(r)){retire(3);r=0;}
 /* Test admission before collecting/projecting an absent display's board. */
 if(!r && !can_create())return;
 unsigned terrain=half(MAP+44)&1u,board_changed=!r || !r->board_valid || terrain;
 /* Exact input comparison, not a hash: a stable field must not repeat36
  * ownership queries and native geometry scans on every ordinary frame. */
 uint32_t inputs[36];
 for(unsigned i=0;i<36;i++){
  const uint8_t *s=bank+i*FFTA_JOB_RECORD_BYTES;
  const uint8_t *u=(const uint8_t *)(i<24?0x02000080u+i*264u:0x02002fc4u+(i-24)*264u);
  inputs[i]=s[15]|((unsigned)s[16]<<8)|((s[17]&31u)<<16)|
   ((unsigned)(half(u+0x18)!=0 && !(u[0xe8]&64u))<<24);
  if(r && r->field_inputs[i]!=inputs[i])board_changed=1;
 }
 uint8_t board[256];
 if(board_changed && !ffta_geo_field_board((uint8_t *)0x02000080u,board)){
  if(r)r->retiring=1;
  return;
 }
 unsigned prior=LOCK;LOCK=1;
 if(!r)r=create();
 if(!r){LOCK=(uint8_t)prior;return;}
 r->retiring=0;
 int x=*(int16_t *)(MAP+36),y=*(int16_t *)(MAP+38);
 /* Include native shake in the composed viewport as well as its scroll. */
 if(half(MAP+44)&0x400u){
  if(MAP[0x218])x+=*(int16_t *)(MAP+0x224);
  if(MAP[0x21c])y+=*(int16_t *)(MAP+0x226);
 }
 unsigned window_changed=(x>>3)!=(r->camera_x>>3) || (y>>3)!=(r->camera_y>>3);
 unsigned changed=r->dirty || window_changed;
 changed|=board_changed;
 /* Native terrain edits mark this bit; projections must follow current heights. */
 changed|=terrain;
 if(board_changed){
  for(unsigned i=0;i<256;i++){
   r->board[i]=board[i];
   if(board[i] && !ffta_geo_project_tile((int)(i&15u),(int)(i>>4),&r->projection[i]))r->board[i]=0;
  }
  for(unsigned i=0;i<36;i++)r->field_inputs[i]=inputs[i];
  r->board_valid=1;
  /* Native quarter queries release their own map lock before returning. */
  LOCK=1;
 }
 if(changed){
  unsigned reused=0;
  if(!board_changed && !terrain){
   /* Refresh against the OLD viewport first: its maps/provenance still own
    * that intersection. Failed alias/opacity checks require a full rebuild. */
   unsigned current=!(r->dirty&2u) || ffta_geo_refresh_animation(&r->scene,&r->frame);
   if(current){
    r->scene.camera_x=x;r->scene.camera_y=y;
    if(window_changed)reused=ffta_geo_shift(&r->scene,&r->frame,r->asset->sources);
    else if(r->dirty&2u)reused=1;
   }
  }
  r->scene.camera_x=x;r->scene.camera_y=y;
  if(!reused && !ffta_geo_compose(&r->scene,&r->frame,r->asset->sources)){r->retiring=1;}
  else r->dirty=1;
 }
 r->camera_x=x;r->camera_y=y;LOCK=(uint8_t)prior;
}
/* Called only for the native terrain stream; overlay streams retain native ownership. */
unsigned ffta_geo_renderer_stream(void){
 Renderer *r=owner();if(!r || !map_matches(r) || (!r->published && !r->frame.ready))return 0;
 *(uint16_t *)(MAP+44)&=(uint16_t)~1u;return 1;
}
extern void ffta_geo_native_pump(void);
void ffta_geo_renderer_pump(void){
 unsigned skip=half((void *)0x03000e10u) || LOCK;
 ffta_geo_native_pump();if(skip)return;
 Renderer *r=owner();if(!r)return;
 unsigned prior=LOCK;LOCK=1;
 if(r->retiring || !map_matches(r)){retire(3);LOCK=(uint8_t)prior;return;}
 if(r->frame.ready){
  if((r->dirty&1u) || !r->published){
   unsigned n=r->frame.count,first=n<640?n:640;
   transfer(r->frame.graphics,0x06000000u,first*32u);
   if(n>640)transfer(r->frame.graphics[640],0x06006800u,(n-640)*32u);
   transfer(r->frame.map[0],0x06007000u,2048);
   transfer(r->frame.map[1],0x06006000u,2048);
   r->dirty=0;r->published=1;
  }
  background_size(0);
  ((void (*)(void))0x08019b49u)();
  /* Keep native camera-stream origins intact:1BC94 uses them to decide when
   * a new stream is needed. Only the hardware ring scroll uses global pixels.
   * Recompute native scroll first, preserving its exact shake/overlay rules. */
  for(unsigned i=0;i<2;i++){
   unsigned bg=MAP[i];
   SHADOW[5+2*bg]=(uint16_t)(SHADOW[5+2*bg]+half(MAP+40));
   SHADOW[6+2*bg]=(uint16_t)(SHADOW[6+2*bg]+half(MAP+42));
  }
 }
 /* Sample only after native DMA. Recompose in the next main update, never
  * in the VBlank pump: the cache deliberately displays the last completed
  * source snapshot. Bit1 requests composition; bit0 requests publication. */
 if(stamp(r))r->dirty|=2u;
 LOCK=(uint8_t)prior;
}
