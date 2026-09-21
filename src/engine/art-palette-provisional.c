#include "art-palette-provisional.h"

void ffta_art_provisional_confirm(const FFTA_ArtVariants *v,uint8_t *confirmed,
                                 unsigned requested) {
#ifdef FFTA_ART_FAST_CONFIRM
    /* Equal current keys are already exactly the required output, including
     * absent and previously confirmed histories. Re-read every key; never
     * retain a validity bit or assume identities survived another frame. */
    if(!(((uintptr_t)v->key|(uintptr_t)confirmed)&3u)) {
        typedef uint32_t KeyWord __attribute__((may_alias));
        unsigned i;
        _Static_assert(FFTA_ART_HISTORY_SLOTS==20,"twenty current history keys");
        for(i=0;i<5;++i)
            if(((const KeyWord *)v->key)[i]!=((const KeyWord *)confirmed)[i])break;
        if(i==5)return;
    }
#endif
    for(unsigned slot=0;slot<FFTA_ART_HISTORY_SLOTS;slot++) {
        unsigned key=v->key[slot];
        if(key==255)confirmed[slot]=255;
        else if(requested&(1u<<slot))confirmed[slot]=(uint8_t)key;
        else if(confirmed[slot]!=key)confirmed[slot]=255;
    }
}

void ffta_art_provisional_reconcile(FFTA_ArtVariants *v,FFTA_ArtBindings *b,
    uint8_t *confirmed,unsigned first,unsigned last,const uint16_t *table) {
    if(!table)return;
    for(unsigned slot=0;slot<FFTA_ART_HISTORY_SLOTS;slot++) {
        unsigned key=v->key[slot];
        FFTA_ArtBinding *entry=&b->entry[slot];
        if(key==255 || (key>>4)>=FFTA_ART_CLASS_COUNT || confirmed[slot]==key ||
           entry->bank!=(key&15))continue;
        unsigned index=256u+entry->bank*16u;
        if(first>index+1u || last<index+15u)continue;
        unsigned lo=first>index?1:0;
        const uint16_t *values=table+index+lo-first;
        unsigned uniform=1,original=1;
        for(unsigned i=lo;i<16;i++) {
            if(values[i-lo]!=values[0])uniform=0;
            if(values[i-lo]!=entry->native_base[i])original=0;
        }
        if(uniform || original)continue;
        /* A shared native palette is only a possible future class identity.
         * An unrelated table replaces that unconfirmed identity. Do not invent
         * a generated target. A later actor must authenticate a fresh baseline.
         * Confirmed actors, including currently absent ones, still go through
         * the strict mapper and its explicit unsupported-effect reporting. */
        v->key[slot]=255;v->scale[slot]=0;confirmed[slot]=255;
        entry->bank=255;entry->task=0;
    }
}
