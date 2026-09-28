#include "expansion-memory.h"
#include <stdint.h>
#include "persistent.h"
#include "battle-state.h"
#include "evaluated-units.h"
#include "blade-wound.h"
#include "job-state.h"
#include "unit-slot.h"
#include <stddef.h>

/* These tails belong to enlarged native allocations, not to guessed character
 * identities. The small root lives beyond the inventory compatibility view. */
#define ROOT_MAGIC 0x31525041u
#define NODE_MAGIC 0x31535041u
typedef struct { uint8_t ap[34], potion, exposed, wound[2], job[FFTA_JOB_RECORD_BYTES], origin; } Extra;
typedef struct Snapshot Snapshot;
struct Snapshot { uint8_t native[0xe1c]; Snapshot *next; uint32_t magic; Extra units[13]; };
typedef struct { uint32_t magic; Snapshot *snapshots; uint8_t *manager,*selection,*party; } Owners;
#define OWNERS ((Owners *)FFTA_COPY_ROOT)
_Static_assert(sizeof(Snapshot)==(FFTA_CHEMIST_PROGRESSION?0x1180u:0x1140u),"snapshot allocation");
_Static_assert(sizeof(Extra)==(FFTA_CHEMIST_PROGRESSION?66u:61u),"unit copy stride");
/* Execution-scope and snapshot chain pointers follow at 0x0203FF44/48. */
_Static_assert(FFTA_COPY_ROOT+sizeof(Owners)<=FFTA_EXECUTION_ROOT,"copy-owner root below the scope pointers");

static int in_ram(const void *p,unsigned size) {
    uintptr_t address=(uintptr_t)p;
    return !(address&3) && address>=0x02000000u && address<=0x0203f400u-size;
}
static Owners *owners(int initialize) {
    Owners *r=OWNERS;
    if (r->magic!=ROOT_MAGIC) {
        if (!initialize) return 0;
        r->snapshots=0;r->manager=0;r->selection=0;r->party=0;r->magic=ROOT_MAGIC;
    }
    return r;
}
void ffta_copy_owners_reset(void) {
#if FFTA_CHEMIST_PROGRESSION
    ffta_unit_read_invalidate();
#endif
    OWNERS->magic=0;OWNERS->snapshots=0;OWNERS->manager=0;OWNERS->selection=0;OWNERS->party=0;
}
static Extra *copy_extra(uint8_t *unit) {
    Owners *r=owners(0);
    if (!r) return 0;
    if (r->manager && r->manager==*(uint8_t **)0x0200f4b0u) {
        uintptr_t delta=(uintptr_t)unit-(uintptr_t)(r->manager+0x40);
        if (delta==0 || delta==264) return (Extra *)(r->manager+0x3b4)+(delta!=0);
    }
    if (r->selection && r->selection==*(uint8_t **)0x0200f454u && unit==r->selection+0xa4c)
        return (Extra *)(r->selection+0x3800);
    if (r->party && r->party==*(uint8_t **)0x03002818u && unit==r->party+0x1be4)
        return (Extra *)(r->party+0x7240);
    Snapshot *s=r->snapshots;
    /* Every node consumes at least1014 bytes; a longer chain cannot fit RAM. */
    for (unsigned n=0;s && n<64;++n) {
        if (!in_ram(s,sizeof(*s)) || s->magic!=NODE_MAGIC) return 0;
        uintptr_t delta=(uintptr_t)unit-(uintptr_t)(s->native+4);
        int slot=ffta_unit_slot(delta,13);
        if (slot>=0) return &s->units[slot];
        s=s->next;
    }
    return 0;
}
static int roster_slot(uint8_t *unit) {
    uintptr_t delta=(uintptr_t)unit-0x02000080u;
    return ffta_unit_slot(delta,24);
}
uint8_t *ffta_owned_extra_ap(uint8_t *unit,unsigned index) {
    if (index<144 || index>=178) return 0;
    int slot=roster_slot(unit);
    if (slot>=0) return (uint8_t *)0x02001b40u+34*slot+index-144;
    Extra *e=copy_extra(unit);
    return e ? e->ap+index-144 : 0;
}
static uint8_t *potion_address(uint8_t *unit) {
    int slot=roster_slot(unit);
    if (slot>=0) return (uint8_t *)0x02001e80u+slot;
    Extra *e=copy_extra(unit);
    return e ? &e->potion : 0;
}
uint8_t *ffta_owned_exposed(uint8_t *unit) {
    uint8_t *saved=ffta_state_exposed((uint8_t *)0x02000000u,unit);
    if (saved) return saved;
    if (ffta_storage_format((uint8_t *)0x02000000u)!=1) return 0;
    uint8_t *evaluated=ffta_evaluated_exposed(unit);
    if (evaluated) return evaluated;
    Extra *e=copy_extra(unit);
    return e ? &e->exposed : 0;
}
#if FFTA_CHEMIST_PROGRESSION
typedef struct {
    uint8_t *job,*exposed,*wound,*ap,*potion,*origin_address;
    unsigned origin;
} CopyView;
/* A successful ffta_job_state call has already authenticated the exact owner
 * and the storage/bank signatures. Derive its sibling fields synchronously:
 * there is no allocation, native call or persistent pointer cache in this
 * operation. Canonical records and the two copied layouts stay distinct. */
static CopyView copy_view(uint8_t *unit,uint8_t *job) {
    CopyView v={job,0,0,0,0,0,0};
    int slot=ffta_unit_slot((uintptr_t)unit-0x02000080u,24);
    if(slot>=0) {
        v.origin=1u+(unsigned)slot;
        v.ap=(uint8_t *)0x02001b40u+34u*(unsigned)slot;
        v.potion=(uint8_t *)0x02001e80u+(unsigned)slot;
    } else {
        slot=ffta_unit_slot((uintptr_t)unit-0x02002fc4u,12);
        if(slot>=0) {slot+=24;v.origin=1u+(unsigned)slot;}
    }
    if(slot>=0) {
        v.exposed=(uint8_t *)0x02000000u+FFTA_EXPOSED_OFFSET+(unsigned)slot;
        v.wound=(uint8_t *)0x02000000u+FFTA_WOUND_OFFSET+2u*(unsigned)slot;
    } else if(job==unit+offsetof(FFTA_EvaluatedUnit,job)) {
        FFTA_EvaluatedUnit *e=(FFTA_EvaluatedUnit *)unit;
        v.exposed=&e->exposed;v.wound=e->wound;v.potion=&e->potion;
        v.origin_address=&e->origin;v.origin=e->origin;
    } else {
        Extra *e=(Extra *)(job - offsetof(Extra,job));
        v.exposed=&e->exposed;v.wound=e->wound;v.ap=e->ap;v.potion=&e->potion;
        v.origin_address=&e->origin;v.origin=e->origin;
    }
    return v;
}
static unsigned copy_complete_state(uint8_t *destination,uint8_t *source) {
    uint8_t *from=ffta_job_state(source),*to=ffta_job_state(destination);
    if(!from || !to)return 0; /* Unknown sources must still clear known targets. */
    CopyView s=copy_view(source,from),d=copy_view(destination,to);
    /* Capture all values before writing, including self-copy and aliasing. */
    Extra saved;
    for(unsigned i=0;i<FFTA_JOB_RECORD_BYTES;i++)saved.job[i]=s.job[i];
    saved.exposed=*s.exposed;saved.wound[0]=s.wound[0];saved.wound[1]=s.wound[1];
    saved.potion=s.potion?*s.potion:0;saved.origin=(uint8_t)s.origin;
    if(d.ap)for(unsigned i=0;i<34;i++)saved.ap[i]=s.ap?s.ap[i]:0;
    for(unsigned i=0;i<FFTA_JOB_RECORD_BYTES;i++)d.job[i]=saved.job[i];
    *d.exposed=saved.exposed;d.wound[0]=saved.wound[0];d.wound[1]=saved.wound[1];
    if(d.origin_address)*d.origin_address=saved.origin;
    if(d.potion)*d.potion=saved.potion;
    if(d.ap)for(unsigned i=0;i<34;i++)d.ap[i]=saved.ap[i];
    return 1;
}
#endif
static void copy_unit_state(uint8_t *destination,uint8_t *source,unsigned length) {
    if (length!=264 || ffta_storage_format((uint8_t *)0x02000000u)!=1) return;
    uint8_t job[FFTA_JOB_RECORD_BYTES],*job_from=ffta_job_state(source);
    unsigned origin=ffta_job_origin(source);
    uint8_t *preference=ffta_job_potion(source);
    unsigned potion=preference ? *preference : 0;
    for(unsigned i=0;i<FFTA_JOB_RECORD_BYTES;i++)job[i]=job_from ? job_from[i] : 0;
    uint8_t *job_to=ffta_job_state(destination);
    if(job_to)for(unsigned i=0;i<FFTA_JOB_RECORD_BYTES;i++)job_to[i]=job[i];
    Extra *job_extra=copy_extra(destination);
    if(job_extra) { job_extra->origin=(uint8_t)origin;job_extra->potion=(uint8_t)potion; }
    else if(ffta_evaluated_job(destination)) {
        FFTA_EvaluatedUnit *view=(FFTA_EvaluatedUnit *)destination;
        view->origin=(uint8_t)origin;view->potion=(uint8_t)potion;
    }
    /* State ownership is independent of Human AP. Enemies own Exposed but
     * have no Human AP sidecar; unknown sources clear a known destination. */
    uint8_t *state_to=ffta_owned_exposed(destination);
    uint8_t *state_from=ffta_owned_exposed(source);
    uint8_t exposed=state_from ? *state_from : 0;
    if (state_to) *state_to=exposed;
    uint8_t *wound_from=ffta_owned_wound(source),*wound_to=ffta_owned_wound(destination);
    uint8_t wound[2]={wound_from ? wound_from[0] : 0,wound_from ? wound_from[1] : 0};
    if(wound_to) { wound_to[0]=wound[0];wound_to[1]=wound[1]; }
    uint8_t *to=ffta_owned_extra_ap(destination,144);
    if (!to) return;
    uint8_t *from=ffta_owned_extra_ap(source,144);
    /* Snapshot before any writes, including self-copy and roster replacement. */
    Extra saved;
    for (unsigned i=0;i<34;++i) saved.ap[i]=from ? from[i] : 0;
    saved.potion=(uint8_t)potion;
    for (unsigned i=0;i<34;++i) to[i]=saved.ap[i];
    *potion_address(destination)=saved.potion;
}
void ffta_on_unit_copy(uint8_t *destination,uint8_t *source,unsigned length) {
#if FFTA_CHEMIST_PROGRESSION
    ffta_unit_read_invalidate();
    /* The native transfer hook also handles arbitrary non-unit buffers. They
     * cannot acquire unit state; reject before authenticating either address. */
    if(length!=264 || ffta_storage_format((uint8_t *)0x02000000u)!=1)return;
    if(copy_complete_state(destination,source))return;
    FFTA_UnitReadScope from,to;
    ffta_unit_read_begin(&from,source);ffta_unit_read_begin(&to,destination);
#endif
    /* Writes affect values in already-owned records, never their container
     * identity or allocation. No native allocator is called by this body. */
    copy_unit_state(destination,source,length);
#if FFTA_CHEMIST_PROGRESSION
    ffta_unit_read_end(&to);ffta_unit_read_end(&from);
#endif
}
void ffta_clear_copy_extra(uint8_t *unit) {
    uint8_t *evaluated=ffta_evaluated_exposed(unit);
    if (evaluated) *evaluated=0;
    ffta_wound_record_clear(ffta_evaluated_wound(unit));
    uint8_t *job=ffta_evaluated_job(unit);
    if(job) {
        for(unsigned i=0;i<FFTA_JOB_RECORD_BYTES;i++)job[i]=0;
        ((FFTA_EvaluatedUnit *)unit)->origin=0;((FFTA_EvaluatedUnit *)unit)->potion=0;
    }
    Extra *e=copy_extra(unit);
    if (e) { for (unsigned i=0;i<34;++i) e->ap[i]=0;e->potion=0;e->exposed=0;e->wound[0]=0;e->wound[1]=0;
        for(unsigned i=0;i<FFTA_JOB_RECORD_BYTES;i++)e->job[i]=0;
        e->origin=0; }
}
void ffta_snapshot_register(Snapshot *snapshot) {
    if (!in_ram(snapshot,sizeof(*snapshot))) return;
    Owners *r=owners(1);
    snapshot->next=r->snapshots;snapshot->magic=NODE_MAGIC;
    for (unsigned j=0;j<13;++j) {
        for (unsigned i=0;i<34;++i) snapshot->units[j].ap[i]=0;
        snapshot->units[j].potion=0;snapshot->units[j].exposed=0;
        snapshot->units[j].wound[0]=0;snapshot->units[j].wound[1]=0;
        for(unsigned i=0;i<FFTA_JOB_RECORD_BYTES;i++)snapshot->units[j].job[i]=0;
        snapshot->units[j].origin=0;
    }
    r->snapshots=snapshot;
}
void ffta_manager_register(uint8_t *manager) {
    if (!in_ram(manager,FFTA_CHEMIST_PROGRESSION?0x440:0x430)) return;
    Owners *r=owners(1);r->manager=manager;
    for (unsigned i=0;i<2*sizeof(Extra);++i) manager[0x3b4+i]=0;
}
uint8_t *ffta_owned_battle_manager(void) {
    Owners *r=owners(0);
    return r && r->manager && r->manager==*(uint8_t **)0x0200f4b0u &&
        in_ram(r->manager,FFTA_CHEMIST_PROGRESSION?0x440:0x430) ? r->manager : 0;
}
void ffta_selection_register(uint8_t *selection) {
    if (!in_ram(selection,FFTA_CHEMIST_PROGRESSION?0x3850:0x3840)) return;
    Owners *r=owners(1);r->selection=selection;
    for (unsigned i=0;i<sizeof(Extra);++i) selection[0x3800+i]=0;
}
void ffta_party_copy_register(void) {
    uint8_t *party=*(uint8_t **)0x03002818u;
    if (!in_ram(party,FFTA_CHEMIST_PROGRESSION?0x7290:0x7280)) return;
    Owners *r=owners(1);r->party=party;
    for (unsigned i=0;i<sizeof(Extra);++i) party[0x7240+i]=0;
}
void ffta_copy_owner_free(void *allocation) {
#if FFTA_CHEMIST_PROGRESSION
    ffta_unit_read_invalidate();
#endif
    ffta_evaluated_retire_heap(allocation);
    Owners *r=owners(0);
    if (!r) return;
    if (r->manager==allocation) r->manager=0;
    if (r->selection==allocation) r->selection=0;
    if (r->party==allocation) r->party=0;
    Snapshot **link=&r->snapshots;
    for (unsigned n=0;*link && n<64;++n) {
        Snapshot *s=*link;
        if (!in_ram(s,sizeof(*s)) || s->magic!=NODE_MAGIC) { r->snapshots=0;break; }
        if (s==allocation) { *link=s->next;s->magic=0;s->next=0;break; }
        link=&s->next;
    }
}
uint8_t *ffta_owned_wound(uint8_t *unit) {
    uint8_t *saved=ffta_state_wound((uint8_t *)0x02000000u,unit);
    if(saved)return saved;
    if(ffta_storage_format((uint8_t *)0x02000000u)!=1)return 0;
    uint8_t *evaluated=ffta_evaluated_wound(unit);
    if(evaluated)return evaluated;
    Extra *extra=copy_extra(unit);
    return extra ? extra->wound : 0;
}
uint8_t *ffta_copied_job_state(uint8_t *unit) {
    uint8_t *evaluated=ffta_evaluated_job(unit);
    if(evaluated)return evaluated;
    Extra *extra=copy_extra(unit);
    return extra ? extra->job : 0;
}
unsigned ffta_copied_job_origin(const uint8_t *unit) {
    if(ffta_evaluated_job((uint8_t *)unit))return ffta_evaluated_origin(unit);
    Extra *extra=copy_extra((uint8_t *)unit);
    return extra ? extra->origin : 0;
}
uint8_t *ffta_copied_job_potion(uint8_t *unit) {
    uint8_t *evaluated=ffta_evaluated_potion(unit);
    if(evaluated)return evaluated;
    Extra *extra=copy_extra(unit);
    return extra ? &extra->potion : 0;
}
static void reindex_extra(Extra *extra,unsigned a,unsigned b) {
    ffta_job_record_reindex(extra->job,a,b);
    if(extra->origin==a)extra->origin=(uint8_t)b;
    else if(b && extra->origin==b)extra->origin=(uint8_t)a;
}
void ffta_copied_job_reindex(unsigned a,unsigned b) {
    Owners *r=owners(0);
    if(r) {
        if(r->manager && r->manager==*(uint8_t **)0x0200f4b0u)
            for(unsigned i=0;i<2;i++)reindex_extra((Extra *)(r->manager+0x3b4)+i,a,b);
        if(r->selection && r->selection==*(uint8_t **)0x0200f454u)
            reindex_extra((Extra *)(r->selection+0x3800),a,b);
        if(r->party && r->party==*(uint8_t **)0x03002818u)
            reindex_extra((Extra *)(r->party+0x7240),a,b);
        Snapshot *s=r->snapshots;
        for(unsigned n=0;s && n<64;n++) {
            if(!in_ram(s,sizeof(*s)) || s->magic!=NODE_MAGIC)break;
            for(unsigned i=0;i<13;i++)reindex_extra(&s->units[i],a,b);
            s=s->next;
        }
    }
    /* Transient stack evaluations end before the native roster UI can reorder
     * or replace a unit. Heap-backed previews remain owned across UI events. */
    ffta_evaluated_reindex_heap(a,b);
}
unsigned ffta_copied_job_peers(uint8_t *unit,uint8_t **output,unsigned capacity) {
    if(!output)return 0;
    if(ffta_evaluated_job(unit)) {
        if(!capacity)return 0;
        output[0]=unit;return 1;
    }
    if(!copy_extra(unit))return 0;
    Owners *r=owners(0);
    if(r->manager && r->manager==*(uint8_t **)0x0200f4b0u &&
       (unit==r->manager+0x40 || unit==r->manager+0x148)) {
        if(capacity<2)return 0;
        output[0]=r->manager+0x40;output[1]=r->manager+0x148;return 2;
    }
    if((r->selection && r->selection==*(uint8_t **)0x0200f454u && unit==r->selection+0xa4c) ||
       (r->party && r->party==*(uint8_t **)0x03002818u && unit==r->party+0x1be4)) {
        if(!capacity)return 0;
        output[0]=unit;return 1;
    }
    Snapshot *s=r->snapshots;
    for(unsigned n=0;s && n<64;n++) {
        if(!in_ram(s,sizeof(*s)) || s->magic!=NODE_MAGIC)return 0;
        uintptr_t delta=(uintptr_t)unit-(uintptr_t)(s->native+4);
        if(ffta_unit_slot(delta,13)>=0) {
            if(capacity<13)return 0;
            for(unsigned i=0;i<13;i++)output[i]=s->native+4+i*264;
            return 13;
        }
        s=s->next;
    }
    return 0;
}
#if FFTA_CHEMIST_PROGRESSION
unsigned ffta_job_copied_cohort(uint8_t *unit,FFTA_JobCohort *view) {
    if(!view || !ffta_job_state(unit))return 0;
    uint8_t *evaluated=ffta_evaluated_job(unit);
    if(evaluated){*view=(FFTA_JobCohort){unit,evaluated,1,0};return 1;}
    Extra *own=copy_extra(unit);Owners *r=owners(0);
    if(!own || !r)return 0;
    if(r->manager && r->manager==*(uint8_t **)0x0200f4b0u &&
       (unit==r->manager+0x40 || unit==r->manager+0x148)) {
        *view=(FFTA_JobCohort){r->manager+0x40,((Extra *)(r->manager+0x3b4))->job,2,sizeof(Extra)};
        return 1;
    }
    if((r->selection && r->selection==*(uint8_t **)0x0200f454u && unit==r->selection+0xa4c) ||
       (r->party && r->party==*(uint8_t **)0x03002818u && unit==r->party+0x1be4)) {
        *view=(FFTA_JobCohort){unit,own->job,1,0};return 1;
    }
    Snapshot *s=r->snapshots;
    for(unsigned n=0;s && n<64;n++,s=s->next) {
        if(!in_ram(s,sizeof(*s)) || s->magic!=NODE_MAGIC)return 0;
        if(ffta_unit_slot((uintptr_t)unit-(uintptr_t)(s->native+4),13)>=0) {
            *view=(FFTA_JobCohort){s->native+4,s->units[0].job,13,sizeof(Extra)};return 1;
        }
    }
    return 0;
}
#endif
