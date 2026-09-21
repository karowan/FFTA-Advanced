#include <stdint.h>
#include "persistent.h"
#include "battle-state.h"
#include "evaluated-units.h"
#include "blade-wound.h"

/* These tails belong to enlarged native allocations, not to guessed character
 * identities. The small root lives beyond the inventory compatibility view. */
#define ROOT_MAGIC 0x31525041u
#define NODE_MAGIC 0x31535041u
typedef struct { uint8_t ap[34], potion, exposed, wound[2]; } Extra;
typedef struct Snapshot Snapshot;
struct Snapshot { uint8_t native[0xe1c]; Snapshot *next; uint32_t magic; Extra units[13]; };
typedef struct { uint32_t magic; Snapshot *snapshots; uint8_t *manager,*selection,*party; } Owners;
#define OWNERS ((Owners *)0x0203ff30u)
_Static_assert(sizeof(Snapshot)==0x1014,"snapshot allocation");
_Static_assert(sizeof(Extra)==38,"unit copy stride");

static int in_ram(const void *p,unsigned size) {
    uintptr_t address=(uintptr_t)p;
    return !(address&3) && address>=0x02000000u && address<=0x0203f800u-size;
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
    saved.potion=0;
    uint8_t *pref=potion_address(source);
    if (pref) saved.potion=*pref;
    for (unsigned i=0;i<34;++i) to[i]=saved.ap[i];
    *potion_address(destination)=saved.potion;
}
void ffta_clear_copy_extra(uint8_t *unit) {
    uint8_t *evaluated=ffta_evaluated_exposed(unit);
    if (evaluated) *evaluated=0;
    ffta_wound_record_clear(ffta_evaluated_wound(unit));
    Extra *e=copy_extra(unit);
    if (e) { for (unsigned i=0;i<34;++i) e->ap[i]=0;e->potion=0;e->exposed=0;e->wound[0]=0;e->wound[1]=0; }
}
void ffta_snapshot_register(Snapshot *snapshot) {
    if (!in_ram(snapshot,sizeof(*snapshot))) return;
    Owners *r=owners(1);
    snapshot->next=r->snapshots;snapshot->magic=NODE_MAGIC;
    for (unsigned j=0;j<13;++j) {
        for (unsigned i=0;i<34;++i) snapshot->units[j].ap[i]=0;
        snapshot->units[j].potion=0;snapshot->units[j].exposed=0;
        snapshot->units[j].wound[0]=0;snapshot->units[j].wound[1]=0;
    }
    r->snapshots=snapshot;
}
void ffta_manager_register(uint8_t *manager) {
    if (!in_ram(manager,0x400)) return;
    Owners *r=owners(1);r->manager=manager;
    for (unsigned i=0;i<76;++i) manager[0x3b4+i]=0;
}
void ffta_selection_register(uint8_t *selection) {
    if (!in_ram(selection,0x3828)) return;
    Owners *r=owners(1);r->selection=selection;
    for (unsigned i=0;i<38;++i) selection[0x3800+i]=0;
}
void ffta_party_copy_register(void) {
    uint8_t *party=*(uint8_t **)0x03002818u;
    if (!in_ram(party,0x7268)) return;
    Owners *r=owners(1);r->party=party;
    for (unsigned i=0;i<38;++i) party[0x7240+i]=0;
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
