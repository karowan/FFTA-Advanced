#include "job-state.h"
_Static_assert(FFTA_JOB_UNIT_COUNT==36u && FFTA_JOB_RECORD_BYTES==22u,
               "Authenticated canonical cohort layout");

/* Current-query canonical cohort traversal. No cached fields, ownership or
 * map state survives this call. The original query handles every other owner.
 * The installer authenticates the canonical record/peer accessor contract. */
unsigned ffta_geo_field_canonical(const uint8_t *u) {
    uintptr_t d=(uintptr_t)u-0x02000080u;
    if(d<24u*264u && d%264u==0)return 1;
    d=(uintptr_t)u-0x02002fc4u;
    return d<12u*264u && d%264u==0;
}
static unsigned tile(int x,int y) {
    return x>=0 && x<16 && y>=0 && y<16 &&
        ((unsigned (*)(unsigned,unsigned))0x0801cc7du)(x,y);
}
static unsigned absolute(int v) {return (unsigned)(v<0?-v:v);}

unsigned ffta_geo_field_fast(const uint8_t *u,int x,int y,unsigned kind) {
    /* Only the authenticated dispatcher calls this canonical-only entry.
     * Its other branch restores the original stack before the old query. */
    if(!tile(x,y) || (kind!=1 && kind!=2))return 0;
    /* Canonical state validity is shared by the complete live bank. Resolve
     * its first record through the existing accessor, including format checks. */
    const uint8_t *s=ffta_job_state((uint8_t *)0x02000080u);
    if(!s)return 0;
    for(unsigned i=0;i<FFTA_JOB_UNIT_COUNT;i++,s+=FFTA_JOB_RECORD_BYTES) {
        unsigned flags=s[FFTA_JOB_GEO_FIELD_FLAGS],timer=(flags>>2)&3u;
        if((flags&3u)!=kind || !timer || timer>2)continue;
        /* Most queries have no matching field. Do not construct a peer array
         * or read unit metadata until its record is a possible match. */
        const uint8_t *c=(const uint8_t *)(i<24 ? 0x02000080u+i*264u :
                                                        0x02002fc4u+(i-24)*264u);
        if(!(c[0x18]|c[0x19]) || (c[0xe8]&64u))continue;
        if(kind==2 && ((c[0x29]>>7)^((c[0xeb]>>5)&1u))!=(u[0x29]>>7))continue;
        int cx=s[FFTA_JOB_GEO_FIELD_X],cy=s[FFTA_JOB_GEO_FIELD_Y];
        if(absolute(x-cx)+absolute(y-cy)>1 || !tile(cx,cy))continue;
        int h=((int (*)(unsigned,unsigned))0x0801cc19u)(x,y);
        int ch=((int (*)(unsigned,unsigned))0x0801cc19u)(cx,cy);
        if(absolute(h-ch)<=2)return 1;
    }
    return 0;
}
