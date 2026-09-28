#ifndef FFTA_ALIGNED_MEMORY_H
#define FFTA_ALIGNED_MEMORY_H
#include <stdint.h>
/* GCC's explicit alias type permits word access to our owned structs. ARM7
 * word transfers require aligned addresses: uncertain/unaligned copies keep
 * their byte path. Length is an exact multiple of four at each caller. These
 * forward copies preserve the former forward-byte overlap behavior. */
typedef uint32_t FFTA_AliasWord __attribute__((may_alias));
static inline void ffta_zero_aligned(void *destination,unsigned bytes) {
    FFTA_AliasWord *d=destination;
    for(unsigned i=0;i<bytes/4u;i++)d[i]=0;
}
static inline void ffta_copy_aligned_or_bytes(void *destination,const void *source,unsigned bytes) {
    if(!(((uintptr_t)destination|(uintptr_t)source|bytes)&3u)) {
        FFTA_AliasWord *d=destination;const FFTA_AliasWord *s=source;
        for(unsigned i=0;i<bytes/4u;i++)d[i]=s[i];
    } else {
        uint8_t *d=destination;const uint8_t *s=source;
        for(unsigned i=0;i<bytes;i++)d[i]=s[i];
    }
}
#endif
