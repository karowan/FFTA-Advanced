#include <stdint.h>
/* The 66-byte owned copy tail ends at +7282. Move the full item-list start
 * to +7290 and enlarge both constructors by 16 bytes. Compact Status keeps
 * its earlier read-only list at +4340, but still needs the larger copy tail.
 * The existing party heap's authenticated lifecycle owns this decision. */
static unsigned readonly(void *heap){
 const volatile uint32_t *s=(const volatile uint32_t *)0x0203f200u;
 return s[0]==0x50485232u && s[1]==(uint32_t)heap &&
  s[1]==*(volatile uint32_t *)0x0200f434u && s[2]==1 && !s[3];
}
void *ffta_art_party_context_allocate(void *heap,unsigned bytes){
 if(bytes==0x9990 && readonly(heap))bytes=0x7290;
 return ((void *(*)(void *,unsigned))0x08007139u)(heap,bytes);
}
unsigned ffta_art_party_list_offset(uint32_t *context){
 return context && readonly((void *)context[0])?0x4340u:0x7290u;
}
