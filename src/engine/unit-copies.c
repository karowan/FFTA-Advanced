#include <stdint.h>
#include "persistent.h"
#include "battle-state.h"
#include "evaluated-units.h"
#include "blade-wound.h"
#include "job-state.h"

/* These tails belong to enlarged native allocations, not to guessed character
 * identities. The small root lives beyond the inventory compatibility view. */
#define ROOT_MAGIC 0x31525041u
#define NODE_MAGIC 0x31535041u
typedef struct { uint8_t ap[34], potion, exposed, wound[2], job[FFTA_JOB_RECORD_BYTES], origin; } Extra;
typedef struct Snapshot Snapshot;
struct Snapshot { uint8_t native[0xe1c]; Snapshot *next; uint32_t magic; Extra units[13]; };
typedef struct { uint32_t magic; Snapshot *snapshots; uint8_t *manager,*selection,*party; } Owners;
#define OWNERS ((Owners *)0x0203ff30u)
_Static_assert(sizeof(Snapshot)==0x1140,"snapshot allocation");
_Static_assert(sizeof(Extra)==61,"unit copy stride");
/* Execution-scope and snapshot chain pointers follow at 0x0203FF44/48. */
_Static_assert(0x0203ff30u+sizeof(Owners)<=0x0203ff44u,"copy-owner root below the scope pointers");

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
    OWNERS->magic=0;OWNERS->snapshots=0;OWNERS->manager=0;OWNERS->selection=0;OWNERS->party=0;
}
static Extra *copy_extra(uint8_t *unit) {
    Owners *r=owners(0);
    if (!r) return 0;
    if (r->manager && r->manager==*(uint8_t **)0x0200f4b0u) {
        uintptr_t delta=(uintptr_t)unit-(uintptr_t)(r->manager+0x40);
        if (delta==0 || delta==264) return (Extra *)(r->manager+0x3b4)+delta/264;
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
        if (delta<13*264 && delta%264==0) return &s->units[delta/264];
        s=s->next;
    }
    return 0;
}
static int roster_slot(uint8_t *unit) {
    uintptr_t delta=(uintptr_t)unit-0x02000080u;
    return delta<24*264 && delta%264==0 ? (int)(delta/264) : -1;
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
void ffta_on_unit_copy(uint8_t *destination,uint8_t *source,unsigned length) {
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
    if (!in_ram(manager,0x430)) return;
    Owners *r=owners(1);r->manager=manager;
    for (unsigned i=0;i<2*sizeof(Extra);++i) manager[0x3b4+i]=0;
}
uint8_t *ffta_owned_battle_manager(void) {
    Owners *r=owners(0);
    return r && r->manager && r->manager==*(uint8_t **)0x0200f4b0u &&
        in_ram(r->manager,0x430) ? r->manager : 0;
}
void ffta_selection_register(uint8_t *selection) {
    if (!in_ram(selection,0x3840)) return;
    Owners *r=owners(1);r->selection=selection;
    for (unsigned i=0;i<sizeof(Extra);++i) selection[0x3800+i]=0;
}
void ffta_party_copy_register(void) {
    uint8_t *party=*(uint8_t **)0x03002818u;
    if (!in_ram(party,0x7280)) return;
    Owners *r=owners(1);r->party=party;
    for (unsigned i=0;i<sizeof(Extra);++i) party[0x7240+i]=0;
}
void ffta_copy_owner_free(void *allocation) {
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
        if(delta<13*264 && delta%264==0) {
            if(capacity<13)return 0;
            for(unsigned i=0;i<13;i++)output[i]=s->native+4+i*264;
            return 13;
        }
        s=s->next;
    }
    return 0;
}
