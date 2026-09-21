#include <stdint.h>

/* This selector is used only by the expansion's persistent battle workspace.
 * The native best-fit policy otherwise places it in a high temporary-work gap,
 * preventing that gap from coalescing for the next 39944-byte native request.
 * Native unlink/split/free still own all heap mutation. */
void ffta_art_workspace_find(uint16_t *heap, unsigned words,
                            void **previous, void **selected) {
    *previous=0;*selected=0;
    uintptr_t base=(uintptr_t)heap;
    if((base&3u) || base<0x0200000cu || base>0x0203bff0u || words!=0x998u)return;
    uintptr_t end=base+8u+4u*heap[3];
    if(end<=base+20u || end>0x0203c000u)return;
    unsigned previous_index=0;
    for(uintptr_t at=base+8u;at && at<=end-12u;) {
        const uint16_t *h=(const uint16_t *)at;
        unsigned free=h[2]==0x7370u;
        if((!free && h[2]!=0x616cu) || h[0]!=previous_index)return;
        unsigned bytes=4u*h[3];
        if(bytes>(end-at)-(free?12u:0u))return;
        uintptr_t next=h[1]?base+4u*h[1]:0;
        if(next && (next<=at || next>end-12u))return;
        if(at+bytes+(free?12u:0u)!=(next?next:end))return;
        if(free && h[3]>=words) {
            /* Verify the chosen free-list neighbors before native unlink. */
            for(unsigned side=0;side<2;side++) {
                unsigned index=h[4+side];
                if(!index) {
                    if(!side && heap[0]!=(at-base)/4u)return;
                    continue;
                }
                uintptr_t n=base+4u*index;
                if(n<base+8u || n>end-12u)return;
                const uint16_t *neighbor=(const uint16_t *)n;
                if(neighbor[2]!=0x7370u || neighbor[5-side]!=(at-base)/4u)return;
            }
            *selected=(void *)at;return;
        }
        previous_index=(at-base)/4u;
        at=next;
    }
}
