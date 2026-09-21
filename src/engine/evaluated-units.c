#include "evaluated-units.h"
#include "battle-state.h"
#include "blade-wound.h"
#include "job-state.h"

#define EVALUATED_MAGIC 0x31564546u
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
static int ram_container(uintptr_t p) {
    return !(p&3) && p>=0x02000000u && p<=0x0203f400u-sizeof(FFTA_EvaluatedUnit);
}
static int stack_container(uintptr_t p) {
    uintptr_t stack;
    __asm__ volatile ("mov %0, sp" : "=r" (stack));
    return !(p&3) && p>=0x03000000u && p>=stack &&
        p<=0x03008000u-sizeof(FFTA_EvaluatedUnit);
}
/* The native heap is a physical chain beginning at its first block, +8.
 * Only an exact live allocated payload start can own a law-copy container.
 * No guessed header immediately before an arbitrary pointer is accepted. */
static int heap_container(uintptr_t p) {
    if (!ram_container(p)) return 0;
    uintptr_t base=*(const uintptr_t *)0x0200f434u;
    if ((base&3) || base<0x02000000u || base>0x0203f3f8u) return 0;
    uintptr_t end=base+8u+4u*half((const uint8_t *)base+6);
    if (end<=base+8 || end>0x0203f400u || p<base+20 || p+sizeof(FFTA_EvaluatedUnit)>end) return 0;
    uintptr_t block=base+8;
    for (unsigned n=0;n<16384;++n) {
        if (block<base+8 || block>end-12) return 0;
        const uint8_t *header=(const uint8_t *)block;
        unsigned marker=half(header+4),bytes=4u*half(header+6);
        if (marker!=0x616c && marker!=0x7370) return 0;
        if (block+12==p)
            return marker==0x616c && bytes>=12+sizeof(FFTA_EvaluatedUnit) && bytes<=end-block;
        unsigned next=half(header+2);
        if (!next) return 0;
        uintptr_t following=base+4u*next;
        if (following<=block) return 0;
        block=following;
    }
    return 0;
}
static FFTA_EvaluatedUnit *tagged(uint8_t *unit) {
    uintptr_t p=(uintptr_t)unit;
    if (!ram_container(p) && !stack_container(p)) return 0;
    FFTA_EvaluatedUnit *scope=(FFTA_EvaluatedUnit *)unit;
    return scope->magic==EVALUATED_MAGIC && scope->self==p ? scope : 0;
}
uint8_t *ffta_evaluated_exposed(uint8_t *unit) {
    FFTA_EvaluatedUnit *scope=tagged(unit);
    if (!scope) return 0; /* Common unregistered copies never walk the heap. */
    return stack_container((uintptr_t)unit) || heap_container((uintptr_t)unit) ? &scope->exposed : 0;
}
unsigned ffta_evaluated_init(FFTA_EvaluatedUnit *scope,const uint8_t *source) {
    if (!scope || !source || !stack_container((uintptr_t)scope)) return 0;
    uint8_t *owned=ffta_owned_exposed((uint8_t *)source);
    uint8_t exposed=owned ? *owned : 0;
    uint8_t *wound=ffta_owned_wound((uint8_t *)source);
    uint8_t saved_wound[2]={wound ? wound[0] : 0,wound ? wound[1] : 0};
    uint8_t saved_job[FFTA_JOB_RECORD_BYTES],*job=ffta_job_state((uint8_t *)source);
    for(unsigned i=0;i<FFTA_JOB_RECORD_BYTES;i++)saved_job[i]=job ? job[i] : 0;
    unsigned origin=ffta_job_origin(source);
    uint8_t *potion=ffta_job_potion((uint8_t *)source);
    unsigned preference=potion ? *potion : 0;
    for (unsigned i=0;i<264;++i) scope->unit[i]=source[i];
    scope->exposed=exposed;
    scope->wound[0]=saved_wound[0];scope->wound[1]=saved_wound[1];scope->reserved=0;
    scope->self=(uintptr_t)scope;scope->magic=EVALUATED_MAGIC;
    for(unsigned i=0;i<FFTA_JOB_RECORD_BYTES;i++)scope->job[i]=saved_job[i];
    scope->origin=(uint8_t)origin;scope->potion=(uint8_t)preference;
    scope->job_reserved[0]=scope->job_reserved[1]=0;
    return 1;
}
void ffta_evaluated_close(FFTA_EvaluatedUnit *scope) {
    if (!tagged((uint8_t *)scope)) return;
    scope->magic=0;scope->self=0;scope->exposed=0;
    scope->wound[0]=0;scope->wound[1]=0;scope->reserved=0;
    for(unsigned i=0;i<FFTA_JOB_RECORD_BYTES;i++)scope->job[i]=0;
    scope->origin=scope->potion=scope->job_reserved[0]=scope->job_reserved[1]=0;
}
void *ffta_evaluated_allocate(unsigned requested) {
    unsigned size=requested==264 ? sizeof(FFTA_EvaluatedUnit) : requested;
    FFTA_EvaluatedUnit *scope=((void *(*)(unsigned))0x08022841u)(size);
    if (!scope || requested!=264) return scope;
    /* Native allocation failure is returned unchanged; no tag or state write. */
    if (!heap_container((uintptr_t)scope)) return scope;
    scope->exposed=0;
    scope->wound[0]=0;scope->wound[1]=0;scope->reserved=0;
    scope->self=(uintptr_t)scope;scope->magic=EVALUATED_MAGIC;
    for(unsigned i=0;i<FFTA_JOB_RECORD_BYTES;i++)scope->job[i]=0;
    scope->origin=scope->potion=scope->job_reserved[0]=scope->job_reserved[1]=0;
    return scope;
}
void ffta_evaluated_retire_heap(void *allocation) {
    if (!tagged(allocation) || !heap_container((uintptr_t)allocation)) return;
    ffta_evaluated_close(allocation);
}
uint8_t *ffta_evaluated_wound(uint8_t *unit) {
    uint8_t *packed=ffta_evaluated_exposed(unit);
    return packed ? packed+1 : 0;
}
uint8_t *ffta_evaluated_job(uint8_t *unit) {
    return ffta_evaluated_exposed(unit) ? ((FFTA_EvaluatedUnit *)unit)->job : 0;
}
unsigned ffta_evaluated_origin(const uint8_t *unit) {
    return ffta_evaluated_job((uint8_t *)unit) ? ((const FFTA_EvaluatedUnit *)unit)->origin : 0;
}
uint8_t *ffta_evaluated_potion(uint8_t *unit) {
    return ffta_evaluated_job(unit) ? &((FFTA_EvaluatedUnit *)unit)->potion : 0;
}
void ffta_evaluated_reindex_heap(unsigned a,unsigned b) {
    uintptr_t base=*(const uintptr_t *)0x0200f434u;
    if((base&3) || base<0x02000000u || base>0x0203f3f8u)return;
    uintptr_t end=base+8u+4u*half((const uint8_t *)base+6),block=base+8;
    if(end<=block || end>0x0203f400u)return;
    for(unsigned n=0;n<16384;n++) {
        if(block>end-12)return;
        const uint8_t *header=(const uint8_t *)block;
        unsigned marker=half(header+4),bytes=4u*half(header+6);
        if((marker!=0x616c && marker!=0x7370) || bytes<12 || bytes>end-block)return;
        if(marker==0x616c && bytes>=12+sizeof(FFTA_EvaluatedUnit)) {
            FFTA_EvaluatedUnit *scope=(FFTA_EvaluatedUnit *)(block+12);
            if(scope->magic==EVALUATED_MAGIC && scope->self==(uintptr_t)scope) {
                ffta_job_record_reindex(scope->job,a,b);
                if(scope->origin==a)scope->origin=(uint8_t)b;
                else if(b && scope->origin==b)scope->origin=(uint8_t)a;
            }
        }
        unsigned next=half(header+2);
        if(!next)return;
        uintptr_t following=base+4u*next;
        if(following<=block)return;
        block=following;
    }
}
