#include <stdint.h>
/* Historical art-stage source: scripts/build-palette-removal.py patches the
 * installed binary to heap limits 0x0203EFF0/0x0203F000 and moves the party
 * record to 0x0203F200. Keep these values so the parent stage reproduces. */

/* The native Status destructor individually releases its context, glyph
 * backing, text heap and secondary buffer. Its outer parent is not needed
 * when those allocations belong directly to the live battle heap. */
typedef struct { uint32_t magic,heap,opened,closed; } PartyHeap;
static volatile PartyHeap *const state=(PartyHeap *)FFTA_ART_PARTY_ROOT;
#define MAGIC 0x50485231u
#ifdef FFTA_ART_COMPACT_STATUS
#define READONLY_MAGIC 0x50485232u
static unsigned owned(void){return state->magic==MAGIC || state->magic==READONLY_MAGIC;}
#else
static unsigned owned(void){return state->magic==MAGIC;}
#endif
static uint32_t battle_heap(void){return *(volatile uint32_t *)0x0200f434u;}

void ffta_art_party_heap_reset(void){
 state->magic=state->heap=state->opened=state->closed=0;
}

void *ffta_art_party_parent_allocate(void){
 uint32_t heap=battle_heap();
 if(owned() || (heap&3u) || heap<0x02000000u || heap>0x0203bff0u)return 0;
 const uint16_t *h=(const uint16_t *)heap;
 uint32_t end=heap+8u+4u*h[3];
 /* Header+4 counts free blocks; it is not a constant heap-kind tag. */
 if(end<=heap+20u || end>0x0203c000u || h[2]>(end-heap)/12u)return 0;
 state->heap=heap;state->opened=state->closed=0;state->magic=MAGIC;
 return (void *)heap;
}

/* Only the two native party constructors and destructors may borrow/close
 * this heap. An unrelated heap reset with the same address must stay native. */
unsigned ffta_art_party_heap_bypass(void *heap,uint32_t caller){
 if(!owned() || (uint32_t)heap!=state->heap || state->heap!=battle_heap())return 0;
 if(caller==0x080710b3u || caller==0x08071131u){state->opened++;return 1;}
 if(caller==0x08071275u || caller==0x080712bfu){state->closed++;return 1;}
 return 0;
}

void ffta_art_party_parent_free(void *heap){
 if(owned() && (uint32_t)heap==state->heap && state->heap==battle_heap()){
  state->magic=0;return;
 }
 ((void (*)(void *))0x08022855u)(heap);
}

#ifdef FFTA_ART_COMPACT_STATUS
/* Only the native read-only battle Status entry at 08070688 calls this.
 * Other constructors, including world mode1, retain the full item list. */
void ffta_art_party_mark_readonly(void){
 if(state->magic==MAGIC && state->heap==battle_heap() && !state->opened && !state->closed)
  state->magic=READONLY_MAGIC;
}
static unsigned readonly(void *heap){
 return state->magic==READONLY_MAGIC && (uint32_t)heap==state->heap &&
  state->heap==battle_heap() && state->opened==1 && !state->closed;
}
void *ffta_art_party_context_allocate(void *heap,unsigned bytes){
 if(bytes==0x9980 && readonly(heap))bytes=0x7280;
 return ((void *(*)(void *,unsigned))0x08007139u)(heap,bytes);
}
unsigned ffta_art_party_list_offset(uint32_t *context){
 return context && readonly((void *)context[0]) ? 0x4340u : 0x7280u;
}
#endif
