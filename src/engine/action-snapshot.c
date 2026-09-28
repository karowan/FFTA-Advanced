#include "expansion-memory.h"
#include "action-snapshot.h"
#include "samurai-state.h"
#include "registry.h"
#include "reaction-queue.h"
#include "evaluated-units.h"
#include "battle-state.h"
#include "blade-wound.h"
#include "aligned-memory.h"
#if FFTA_CHEMIST_PROGRESSION
#include "dark-knight-state.h"
#include "viking-state.h"
#include "turn-supports.h"
extern unsigned ffta_drk_snapshot_flags(const uint8_t *);
#endif
#define MAGIC 0x31534e41u
/* Four private bytes after the Higan execution root; no saved-state alias. */
#define ACTIVE ((FFTA_ActionSnapshot *volatile *)FFTA_SNAPSHOT_ROOT)
typedef struct { uintptr_t *token; FFTA_ActionSnapshot frame; } ResultStorage;
_Static_assert(sizeof(ResultStorage)==824,"external result snapshot ABI");
extern ResultStorage *ffta_additional_result_storage(void) __attribute__((weak));
extern unsigned ffta_additional_workspace_prepare(void) __attribute__((weak));
extern void ffta_additional_workspace_retire(void *) __attribute__((weak));
static unsigned stack_frame(const FFTA_ActionSnapshot *s) {
    uintptr_t p=(uintptr_t)s,sp;
    __asm__ volatile("mov %0, sp":"=r"(sp));
    if(!(p&3u) && p>=sp && p>=0x03000000u && p<=0x03008000u-sizeof(*s))return 1;
    /* A null, unaligned or non-EWRAM pointer cannot be an external frame.
     * Ordinary forecasts have no current snapshot; avoid owner/heap lookups. */
    if((p&3u) || p<0x02000000u || p>0x02040000u-sizeof(*s))return 0;
    /* Root's external result frames still require an exact live stack owner.
     * A RAM pointer or a stale copied frame cannot authenticate itself. */
    ResultStorage *bank=ffta_additional_result_storage?ffta_additional_result_storage():0;
    if(bank)for(unsigned i=0;i<8;i++)if(s==&bank[i].frame){
        uintptr_t t=(uintptr_t)bank[i].token;
        return !(t&3u) && t>=sp && t>=0x03000000u && t<=0x03007ffcu && *(uintptr_t *)t==p;
    }
    return 0;
}
static FFTA_ActionSnapshot *current(void) {
    FFTA_ActionSnapshot *s=*ACTIVE;
    return stack_frame(s) && s->magic==MAGIC && s->self==(uintptr_t)s && s->count<=64?s:0;
}
/* Never grow the nested native stack into IWRAM executable code. Root
 * integration allocates eight external slots in a pool owned by its battle manager.
 * Standalone builds return no bank and never touch that allocation. Ownership is
 * the exact current snapshot, not unit identity; stale slots are reclaimable. */
typedef struct { FFTA_ActionSnapshot *owner;unsigned flags[64]; } ExtraSnapshot;
_Static_assert(sizeof(ExtraSnapshot)==260,"external snapshot bank ABI");
extern ExtraSnapshot *ffta_additional_snapshot_storage(void) __attribute__((weak));
extern uint16_t *ffta_additional_extension_snapshot_storage(void) __attribute__((weak));
#if !FFTA_CHEMIST_PROGRESSION
static uint16_t *extension_slot(ExtraSnapshot *slot) {
    uint16_t *bank=ffta_additional_extension_snapshot_storage?ffta_additional_extension_snapshot_storage():0;
    if(!slot || !bank)return 0;
    return bank+64u*(unsigned)(slot-ffta_additional_snapshot_storage());
}
#endif
#if FFTA_CHEMIST_PROGRESSION
#include "battle-workspace.h"
#endif
typedef struct { ExtraSnapshot *extra;uint16_t *extension;unsigned *medicine; } ExtraView;
/* One validated pool, one slot search. These pointers never escape this
 * synchronous accessor: no allocation, mutation callback or cached root can
 * carry them into another lifetime. All arrays belong to the same pool ABI. */
static ExtraView extra_view(ExtraSnapshot *bank,unsigned index) {
    ExtraView v={bank+index,0,0};
#if FFTA_CHEMIST_PROGRESSION
    v.extension=(uint16_t *)((uint8_t *)bank+FFTA_WORKSPACE_EXTENSION-FFTA_WORKSPACE_EXTRA)+64u*index;
    v.medicine=(unsigned *)((uint8_t *)bank+FFTA_WORKSPACE_CHEMIST-FFTA_WORKSPACE_EXTRA)+64u*index;
#else
    v.extension=extension_slot(bank+index);
#endif
    return v;
}
static unsigned extra_owner_active(const FFTA_ActionSnapshot *owner) {
    FFTA_ActionSnapshot *s=current();
    for(unsigned i=0;s && i<8;i++,s=s->previous) {
        if(!stack_frame(s)||s->magic!=MAGIC||s->self!=(uintptr_t)s)break;
        if(s==owner)return 1;
    }
    return 0;
}
static ExtraView extra_slot(FFTA_ActionSnapshot *owner,unsigned create) {
    ExtraView empty={0,0,0};unsigned free=8;
#if FFTA_CHEMIST_PROGRESSION
    ExtraSnapshot *bank=ffta_battle_workspace(FFTA_WORKSPACE_EXTRA);
#else
    ExtraSnapshot *bank=ffta_additional_snapshot_storage?ffta_additional_snapshot_storage():0;
#endif
    if(!bank)return empty;
    for(unsigned i=0;i<8;i++) {
        if(bank[i].owner==owner)return extra_view(bank,i);
        if(create && free==8 && (!bank[i].owner || !extra_owner_active(bank[i].owner)))free=i;
    }
    if(!create || free==8)return empty;
    ExtraView v=extra_view(bank,free);
    for(unsigned i=0;i<64;i++){
        v.extra->flags[i]=0;if(v.extension)v.extension[i]=0;
        if(v.medicine)v.medicine[i]=0;
    }
    v.extra->owner=owner;return v;
}
static unsigned extra_get(FFTA_ActionSnapshot *s,unsigned i) {
    ExtraView v=extra_slot(s,0);return v.extra?v.extra->flags[i]:0;
}
static void extra_set(FFTA_ActionSnapshot *s,unsigned i,unsigned value) {
    ExtraView v=extra_slot(s,value!=0);if(v.extra)v.extra->flags[i]=value;
}
static unsigned extension_get(FFTA_ActionSnapshot *s,unsigned i) {
    ExtraView view=extra_slot(s,0);unsigned v=view.extension?view.extension[i]:0;
    return (v&1023u)|((v&0xfc00u)<<6);
}
static void extension_set(FFTA_ActionSnapshot *s,unsigned i,unsigned value) {
    if(value&~0x003f03ffu)return;
    uint16_t *slot=extra_slot(s,value!=0).extension;
    if(slot)slot[i]=(uint16_t)((value&1023u)|((value>>6)&0xfc00u));
}
#if FFTA_CHEMIST_PROGRESSION
static unsigned cp_get(FFTA_ActionSnapshot *s,unsigned i) {
    unsigned *p=extra_slot(s,0).medicine;return p?p[i]:0;
}
static void cp_set(FFTA_ActionSnapshot *s,unsigned i,unsigned value) {
    unsigned *p=extra_slot(s,value!=0).medicine;if(p)p[i]=value;
}
#endif
static void inherit_flags(FFTA_ActionSnapshot *to,unsigned d,FFTA_ActionSnapshot *from,unsigned i) {
    /* Values are already frozen. Resolve the two owner slots once; never run
     * live providers for a destination whose values will be overwritten. */
    ExtraView source=extra_slot(from,0);
    unsigned extra=source.extra?source.extra->flags[i]:0;
    unsigned extension=source.extension?source.extension[i]:0;
    unsigned medicine=source.medicine?source.medicine[i]:0;
    ExtraView target=extra_slot(to,(extra|extension|medicine)!=0);
    if(target.extra)target.extra->flags[d]=extra;
    if(target.extension)target.extension[d]=(uint16_t)extension;
    if(target.medicine)target.medicine[d]=medicine;
}
static void extra_release(FFTA_ActionSnapshot *s) {
    ExtraView v=extra_slot(s,0);if(!v.extra)return;
    for(unsigned i=0;i<64;i++){
        v.extra->flags[i]=0;if(v.extension)v.extension[i]=0;
        if(v.medicine)v.medicine[i]=0;
    }
    v.extra->owner=0;
}
/* These are native status bits, established by their actual application
 * callbacks: Regen31->3, Conceal60->12, Haste52->21, Shell83->24,
 * Protect82->25. Float/Last Resort/enchantments need their own future tagged
 * state providers; do not mistake equipment movement modes for a status. */
extern unsigned ffta_additional_beneficial(const uint8_t *) __attribute__((weak));
extern unsigned ffta_additional_snapshot_flags(const uint8_t *) __attribute__((weak));
extern unsigned ffta_additional_extra_snapshot_flags(const uint8_t *) __attribute__((weak));
extern unsigned ffta_additional_extension_snapshot_flags(const uint8_t *) __attribute__((weak));
extern unsigned ffta_additional_extension_support_flags(const uint8_t *) __attribute__((weak));
extern unsigned ffta_additional_extension_reaction_flags(const uint8_t *) __attribute__((weak));
extern unsigned ffta_additional_action_category(const uint8_t *,unsigned) __attribute__((weak));
extern void ffta_additional_action_event(const uint8_t *,unsigned,unsigned) __attribute__((weak));
unsigned ffta_poise_beneficial(const uint8_t *unit) {
    if(!unit)return 0;
    return (unit[0xe8]&8u) || (unit[0xe9]&16u) || (unit[0xea]&32u) ||
        (unit[0xeb]&3u) || ffta_centered_active(unit) ||
        (ffta_additional_beneficial && ffta_additional_beneficial(unit));
}
extern void ffta_additional_reaction_queue(unsigned *) __attribute__((weak));
static unsigned flags(const uint8_t *unit) {
    if(!unit)return 0;
    unsigned value=((unsigned)unit[0x29]>>7)*128u;
    if(unit[0xeb]&0x20u)value|=256u;
    if(((unsigned (*)(const uint8_t *))0x080cd50du)(unit)==FFTA_SAM_S2)
        value|=2u|ffta_poise_beneficial(unit);
    unsigned reaction=((unsigned (*)(const uint8_t *))0x080cd4d5u)(unit);
    if(reaction==FFTA_SAM_R1 || reaction==FFTA_SLD_AX_R1)
        value|=32u|(ffta_blade_ward_ready(unit)?64u:0);
    if(reaction==FFTA_SLD_AX_R1)value|=1u<<30;
    if(ffta_additional_snapshot_flags)value|=ffta_additional_snapshot_flags(unit)&FFTA_ACTION_FLAG_JOB_MASK;
    return value;
}
static int find(const FFTA_ActionSnapshot *s,const uint8_t *unit) {
    if(s)for(unsigned i=0;i<s->count;++i)if(s->units[i].unit==unit)return (int)i;
    return -1;
}
/* Conservative zero-provider proof. Native statuses, any custom R/S, owned
 * effect bytes, Exposed/Wound or an allied Refuge field take the full path.
 * The only ignored record bytes are the documented movement ledger, whose
 * modifiers additionally require custom supports. No class-ID assumption. */
static unsigned plain_unit(const uint8_t *unit) {
#if FFTA_CHEMIST_PROGRESSION
    if(!((uintptr_t)unit&3u)) {
        const FFTA_AliasWord *status=(const FFTA_AliasWord *)(unit+0xe8);
        if(status[0]|status[1])return 0;
    } else for(unsigned i=0;i<8;i++)if(unit[0xe8+i])return 0;
    if(((unsigned (*)(const uint8_t *))0x080cd50du)(unit)>=128 ||
       ((unsigned (*)(const uint8_t *))0x080cd4d5u)(unit)>=128)return 0;
    const uint8_t *state=ffta_job_state((uint8_t *)unit);
    if(state) {
        unsigned bits=0;
        for(unsigned i=0;i<12;i++)bits|=state[i];
        bits|=state[15]|state[16]|state[17]|state[18]|(state[19]&7u);
        for(unsigned i=20;i<FFTA_JOB_RECORD_BYTES;i++)bits|=state[i];
        if(bits)return 0;
    }
    const uint8_t *exposed=ffta_owned_exposed((uint8_t *)unit);
    const uint8_t *wound=ffta_owned_wound((uint8_t *)unit);
    if((exposed && *exposed) || (wound && (wound[0]|wound[1])))return 0;
    extern unsigned ffta_geo_refuge(const uint8_t *);
    return !ffta_geo_refuge(unit);
#else
    (void)unit;return 0;
#endif
}
enum { CAPTURE_FULL, CAPTURE_PLAIN, CAPTURE_INHERITED };
static void record(FFTA_ActionSnapshot *s,const uint8_t *unit,unsigned value,unsigned plain) {
    if(!unit)return;
    int i=find(s,unit);
    if(i<0) {
        if(s->count==64)return;
        i=(int)s->count++;
        s->units[i].hp_lost=0;s->units[i].claims=0;
        if(plain!=CAPTURE_INHERITED) {
            unsigned extra=!plain && ffta_additional_extra_snapshot_flags?ffta_additional_extra_snapshot_flags(unit):0;
            unsigned extension=!plain && ffta_additional_extension_snapshot_flags?ffta_additional_extension_snapshot_flags(unit):0;
            unsigned medicine=0;
#if FFTA_CHEMIST_PROGRESSION
            medicine=(plain?0:ffta_cp_flags(unit))|ffta_cp_spotter_adjacency(s->actor,unit);
#endif
            /* Providers have finished before borrowing a pool view. Keep one
             * ownership check for this record's three disjoint flag arrays. */
            ExtraView v=extra_slot(s,(extra|extension|medicine)!=0);
            if(v.extra)v.extra->flags[i]=extra;
            if(v.extension && !(extension&~0x003f03ffu))
                v.extension[i]=(uint16_t)((extension&1023u)|((extension>>6)&0xfc00u));
            if(v.medicine)v.medicine[i]=medicine;
        }
    }
    s->units[i].unit=unit;s->units[i].flags=value;
}
static unsigned continues(const uint8_t *actor) {
    FFTA_ActionSnapshot *s=current();int i=find(s,actor);
    return i>=0 && (s->units[i].flags&4u);
}
unsigned ffta_snapshot_begin(FFTA_ActionSnapshot *s,const uint8_t *actor,const uint8_t *target,unsigned battle) {
    if(!actor || !stack_frame(s))return 0;
    if(ffta_additional_workspace_prepare)ffta_additional_workspace_prepare();
    FFTA_ActionSnapshot *previous=current();
    if(s==previous)return 0;
    extra_release(s);
    int actor_index=find(previous,actor);
    /* A native Counter uses the same outer executor but reverses actor and
     * recipient. Its preview is a new incoming action, not a continuation of
     * the attack it answers. Explicit copies retain the actor-role bit. */
    unsigned same_action=!battle && actor_index>=0 &&
        (previous->units[actor_index].flags&4u);
    s->magic=0;s->self=(uintptr_t)s;s->previous=previous;s->count=0;
    s->reactions_enabled=same_action?(previous->reactions_enabled&255u):1;
    s->action_id=same_action?previous->action_id:0;
    s->origin=same_action?previous->origin:FFTA_ACTION_UNKNOWN;
    s->category=same_action?previous->category:FFTA_ACTION_UNCLASSIFIED;
    s->phase=battle?FFTA_ACTION_EXECUTING:FFTA_ACTION_QUERY;
    s->paid_count=same_action?previous->paid_count:0;
    s->mp_spent=same_action?previous->mp_spent:0;
    s->post_cost_hp=same_action?previous->post_cost_hp:0;
    s->post_cost_mp=same_action?previous->post_cost_mp:0;
    s->actor=actor;s->result_object=0;
    /* A neutral query is still a valid frozen snapshot. Dropping it makes
     * each damage factor rediscover the same empty providers, including heap
     * ownership and terrain scans. Keep the already-captured values for the
     * query's exact lifetime; copies still inherit through snapshot_copy. */
    const uint8_t *units[36];unsigned count=0,enabled=battle || previous!=0 || FFTA_CHEMIST_PROGRESSION;
    if(battle) {
        uint8_t *manager=*(uint8_t **)0x0200f4b0u;
        if(manager) {
            count=((unsigned (*)(uint8_t *,const uint8_t **))0x08099cddu)(manager,units);
            if(count>36)return 0;
            for(unsigned i=0;i<count;++i)units[i]=*(const uint8_t *const *)units[i];
        }
    }
    for(unsigned i=0;i<count+2;++i) {
        const uint8_t *unit=i<count?units[i]:(i==count?actor:target);
        if(!unit)continue;
        int inherited=same_action?find(previous,unit):-1;
#if FFTA_CHEMIST_PROGRESSION
        FFTA_UnitReadScope read;
        if(inherited<0)ffta_unit_read_begin(&read,unit);
#endif
        unsigned plain=inherited<0 && plain_unit(unit);
        unsigned value=inherited>=0?previous->units[inherited].flags:plain?((unsigned)unit[0x29]>>7)*128u:flags(unit);
        if(unit==actor)value|=4u;
        record(s,unit,value,inherited>=0?CAPTURE_INHERITED:plain);enabled|=value&(34u|FFTA_ACTION_FLAG_JOB_MASK);
        unsigned at=(unsigned)find(s,unit);
        ExtraView view=extra_slot(s,0);
        if(view.extra)enabled|=view.extra->flags[at];
        if(view.extension)enabled|=view.extension[at];
        if(view.medicine)enabled|=view.medicine[at];
        if(inherited>=0) {
            int at=find(s,unit);
            s->units[at].hp_lost=previous->units[inherited].hp_lost;
            s->units[at].claims=previous->units[inherited].claims;
            inherit_flags(s,(unsigned)at,previous,(unsigned)inherited);
        }
#if FFTA_CHEMIST_PROGRESSION
        if(inherited<0)ffta_unit_read_end(&read);
#endif
    }
    if(!enabled) { s->self=0;s->previous=0;s->count=0;return 0; }
    s->magic=MAGIC;*ACTIVE=s;return 1;
}
void ffta_snapshot_end(FFTA_ActionSnapshot *s) {
    if(!s || current()!=s)return;
    extra_release(s);
    *ACTIVE=s->previous;
    _Static_assert(sizeof(*s)%4u==0,"aligned snapshot clearing");
    ffta_zero_aligned(s,sizeof(*s));
}
unsigned ffta_action_neutral_query(const uint8_t *actor,const uint8_t *target) {
#if FFTA_CHEMIST_PROGRESSION
    FFTA_ActionSnapshot *s=current();
    /* Native spell AI also calls its final damage stage without opening a
     * snapshot. Prove neutrality from current owned records in that case.
     * This is never a fallback for a missing unit in an active snapshot. */
    if(!s)return (!actor || plain_unit(actor)) && (!target || plain_unit(target)) &&
        (!actor || !target || !ffta_cp_spotter_adjacency(actor,target));
    if(!actor || !target)return 0;
    if(s->phase!=FFTA_ACTION_QUERY)return 0;
    int a=find(s,actor),t=find(s,target);
    if(a<0 || t<0 || ((s->units[a].flags|s->units[t].flags)&~0x184u))return 0;
    ExtraView v=extra_slot(s,0);
    return !v.extra || !(v.extra->flags[a]|v.extra->flags[t]|
        (v.extension?(v.extension[a]|v.extension[t]):0)|
        (v.medicine?(v.medicine[a]|v.medicine[t]):0));
#else
    (void)actor;(void)target;return 0;
#endif
}
void ffta_snapshot_copy(uint8_t *destination,const uint8_t *source) {
    FFTA_ActionSnapshot *s=current();
    if(!s || !destination || !source)return;
    int i=find(s,source);
    record(s,destination,i>=0?s->units[i].flags:flags(source),i>=0?CAPTURE_INHERITED:CAPTURE_FULL);
    int d=find(s,destination);
    if(d>=0) {
        s->units[d].hp_lost=i>=0?s->units[i].hp_lost:0;
        s->units[d].claims=i>=0?s->units[i].claims:0;
        if(i>=0) {inherit_flags(s,(unsigned)d,s,(unsigned)i);return;}
        extra_set(s,(unsigned)d,i>=0?extra_get(s,(unsigned)i):(ffta_additional_extra_snapshot_flags?ffta_additional_extra_snapshot_flags(source):0));
        extension_set(s,(unsigned)d,i>=0?extension_get(s,(unsigned)i):(ffta_additional_extension_snapshot_flags?ffta_additional_extension_snapshot_flags(source):0));
#if FFTA_CHEMIST_PROGRESSION
    cp_set(s,(unsigned)d,i>=0?cp_get(s,(unsigned)i):ffta_cp_flags(source));
#endif
    }
}
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
void ffta_action_started(const uint8_t *actor,unsigned action,unsigned origin,unsigned category) {
    FFTA_ActionSnapshot *s=current();
    if(!s || s->phase!=FFTA_ACTION_EXECUTING || s->actor!=actor)return;
    s->action_id=(uint16_t)action;s->origin=origin;s->category=category;
    s->post_cost_mp=(uint16_t)half(actor+0x1c);
    if(!category && ffta_additional_action_category)
        s->category=ffta_additional_action_category(actor,(uint16_t)action);
    if(ffta_additional_action_event)ffta_additional_action_event(actor,(uint16_t)action,0);
}
void ffta_action_paid(const uint8_t *actor,unsigned action) {
    FFTA_ActionSnapshot *s=current();int i=find(s,actor);
    if(!s || s->phase!=FFTA_ACTION_EXECUTING || i<0 || !(s->units[i].flags&4u))return;
    unsigned mp=half(actor+0x1c),spent=s->post_cost_mp>mp?s->post_cost_mp-mp:0;
    spent+=s->mp_spent;s->mp_spent=(uint16_t)(spent>65535u?65535u:spent);
    if(s->paid_count<65535u)s->paid_count++;
    s->post_cost_hp=(uint16_t)half(actor+0x18);
    s->post_cost_mp=(uint16_t)half(actor+0x1c);
    if(ffta_additional_action_event)ffta_additional_action_event(actor,(uint16_t)action,1);
}
unsigned ffta_action_id(void) { FFTA_ActionSnapshot *s=current();return s?s->action_id:0; }
unsigned ffta_action_origin(void) { FFTA_ActionSnapshot *s=current();return s?s->origin:FFTA_ACTION_UNKNOWN; }
unsigned ffta_action_category(void) { FFTA_ActionSnapshot *s=current();return s?s->category:FFTA_ACTION_UNCLASSIFIED; }
unsigned ffta_action_phase(void) { FFTA_ActionSnapshot *s=current();return s?s->phase:FFTA_ACTION_QUERY; }
unsigned ffta_action_reactions_enabled(void) {
    FFTA_ActionSnapshot *s=current();
    return s && s->phase==FFTA_ACTION_RESULT && s->origin!=FFTA_ACTION_UNKNOWN && (s->reactions_enabled&255u);
}
unsigned ffta_action_paid_count(void) { FFTA_ActionSnapshot *s=current();return s?s->paid_count:0; }
unsigned ffta_action_mp_spent(void) { FFTA_ActionSnapshot *s=current();return s?s->mp_spent:0; }
unsigned ffta_action_post_cost_hp(void) { FFTA_ActionSnapshot *s=current();return s?s->post_cost_hp:0; }
unsigned ffta_action_post_cost_mp(void) { FFTA_ActionSnapshot *s=current();return s&&s->paid_count?s->post_cost_mp:0; }
const uint8_t *ffta_action_actor(void) { FFTA_ActionSnapshot *s=current();return s?s->actor:0; }
const uint8_t *ffta_action_result_object(void) {
    FFTA_ActionSnapshot *s=current();
    return s && s->phase==FFTA_ACTION_RESULT?s->result_object:0;
}
unsigned ffta_action_in_result(const uint8_t *object,const uint8_t *actor) {
    if(!object || !actor)return 0;
    FFTA_ActionSnapshot *s=current();
    for(unsigned i=0;s && i<8;i++,s=s->previous){
        if(!stack_frame(s)||s->magic!=MAGIC||s->self!=(uintptr_t)s ||
           s->origin!=FFTA_ACTION_NATIVE_PRIMARY || s->action_id!=half(object+16) ||
           s->actor!=actor)return 0;
        if(s->phase==FFTA_ACTION_RESULT)return s->result_object==object;
        if(s->phase!=FFTA_ACTION_QUERY)return 0;
    }
    return 0;
}
unsigned ffta_action_unit_flags(const uint8_t *unit) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    return s?(i>=0?s->units[i].flags:0):flags(unit);
}
unsigned ffta_action_unit_extra_flags(const uint8_t *unit) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    return s?(i>=0?extra_get(s,(unsigned)i):0):(ffta_additional_extra_snapshot_flags?ffta_additional_extra_snapshot_flags(unit):0);
}
unsigned ffta_action_claim_extra(uint8_t *unit,unsigned mask) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    if(!s || i<0 || !mask || (mask&0x001fffffu) ||
       (s->phase!=FFTA_ACTION_RESULT && s->phase!=FFTA_ACTION_COMPLETING) ||
       s->origin!=FFTA_ACTION_NATIVE_PRIMARY)return 0;
    unsigned value=extra_get(s,(unsigned)i);if(value&mask)return 0;
    extra_set(s,(unsigned)i,value|mask);return extra_get(s,(unsigned)i)==(value|mask);
}
unsigned ffta_action_unit_extension_flags(const uint8_t *unit) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    return s?(i>=0?extension_get(s,(unsigned)i):0):
        (ffta_additional_extension_snapshot_flags?ffta_additional_extension_snapshot_flags(unit):0);
}
unsigned ffta_action_unit_extension_support_flags(const uint8_t *unit) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    return s?(i>=0?extension_get(s,(unsigned)i):0):
        (ffta_additional_extension_support_flags?ffta_additional_extension_support_flags(unit):0);
}
unsigned ffta_action_unit_extension_reaction_flags(const uint8_t *unit) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    return s?(i>=0?extension_get(s,(unsigned)i):0):
        (ffta_additional_extension_reaction_flags?ffta_additional_extension_reaction_flags(unit):0);
}
unsigned ffta_action_claim_extension(uint8_t *unit,unsigned mask) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    if(!s || i<0 || !mask || (mask&~0x003f0000u) ||
       (s->phase!=FFTA_ACTION_RESULT && s->phase!=FFTA_ACTION_COMPLETING) ||
       s->origin!=FFTA_ACTION_NATIVE_PRIMARY)return 0;
    unsigned value=extension_get(s,(unsigned)i);if(value&mask)return 0;
    extension_set(s,(unsigned)i,value|mask);return extension_get(s,(unsigned)i)==(value|mask);
}
#if FFTA_CHEMIST_PROGRESSION
unsigned ffta_action_cp_flags(const uint8_t *unit) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    return s?(i>=0?cp_get(s,(unsigned)i):0):ffta_cp_flags(unit);
}
unsigned ffta_action_cp_claim(uint8_t *unit,unsigned mask) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    if(!s || i<0 || !mask || (mask&0x003fffffu) ||
       (s->phase!=FFTA_ACTION_RESULT && s->phase!=FFTA_ACTION_COMPLETING) ||
       s->origin!=FFTA_ACTION_NATIVE_PRIMARY)return 0;
    unsigned value=cp_get(s,(unsigned)i);if(value&mask)return 0;
    cp_set(s,(unsigned)i,value|mask);return cp_get(s,(unsigned)i)==(value|mask);
}
/* These projections retain exact frozen data inside an action. Outside one,
 * allegiance/result-only consumers need no job-provider or ownership scan.
 * No memoized state survives a query, copy, mutation or allocation lifetime. */
unsigned ffta_action_unit_flags_masked(const uint8_t *unit,unsigned mask) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    if(s)return i>=0?s->units[i].flags&mask:0;
    if(!unit)return 0;
    unsigned value=(((unsigned)unit[0x29]>>7)*128u)|((unit[0xeb]&32u)?256u:0);
    unsigned jobs=mask&~0x19cu;
    if(!jobs)return value&mask;
    if(jobs==FFTA_COMPOSURE_READY)return (value|ffta_turn_snapshot_flags(unit))&mask;
    if(!(jobs&~(FFTA_ACTION_FLAG_DESPERATION|FFTA_ACTION_FLAG_DESPERATION_ACTIVE|FFTA_DRK_LAST_RESORT|FFTA_DRK_TBN|(3u<<27))))
        return (value|ffta_drk_snapshot_flags(unit))&mask;
    /* Harmful is composed across jobs; it must retain the complete provider. */
    if(!(jobs&~(FFTA_ACTION_FLAG_OPPORTUNIST|FFTA_VIK_CHALLENGER_MASK|FFTA_VIK_FLAG_ABSORB_READY|FFTA_VIK_FLAG_GIL_READY)))
        return (value|ffta_viking_snapshot_flags(unit))&mask;
    return flags(unit)&mask;
}
extern unsigned ffta_integrated_extra_flags_masked(const uint8_t *,unsigned);
unsigned ffta_action_unit_extra_flags_masked(const uint8_t *unit,unsigned mask) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    return s?(i>=0?extra_get(s,(unsigned)i)&mask:0):ffta_integrated_extra_flags_masked(unit,mask);
}
unsigned ffta_action_cp_combat_flags(const uint8_t *unit) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    /* Always honor the frozen action, including units absent from it. Only
     * the no-snapshot path may read current state through the narrower query. */
    return s?(i>=0?cp_get(s,(unsigned)i):0):ffta_cp_combat_flags(unit);
}
void ffta_action_cp_candidate(const uint8_t *unit,unsigned eligible) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    if(!s || i<0 || s->phase!=FFTA_ACTION_RESULT || s->origin!=FFTA_ACTION_NATIVE_PRIMARY)return;
    unsigned value=cp_get(s,(unsigned)i)&~FFTA_CP_WARD_CANDIDATE;
    cp_set(s,(unsigned)i,value|(eligible?FFTA_CP_WARD_CANDIDATE:0));
}
#endif
const uint8_t *ffta_action_unit_at(unsigned index) {
    FFTA_ActionSnapshot *s=current();return s && index<s->count?s->units[index].unit:0;
}
unsigned ffta_action_reaction_kind(void) {
    FFTA_ActionSnapshot *s=current();
    return s && s->phase==FFTA_ACTION_RESULT && s->origin==FFTA_ACTION_NATIVE_REACTION ?
        (s->reactions_enabled>>8)&255u:0;
}
unsigned ffta_action_reaction_value(void) {
    FFTA_ActionSnapshot *s=current();return ffta_action_reaction_kind()?s->reactions_enabled>>16:0;
}
unsigned ffta_action_owns_native_frame(const unsigned *frame) {
    FFTA_ActionSnapshot *s=current();
    if(s && s->origin==FFTA_ACTION_NATIVE_REACTION)s=s->previous;
    return s && stack_frame(s) && s->magic==MAGIC && s->self==(uintptr_t)s &&
      (s->phase==FFTA_ACTION_EXECUTING || s->phase==FFTA_ACTION_COMPLETING) &&
      s->origin==FFTA_ACTION_NATIVE_PRIMARY && s->result_object==(const uint8_t *)frame;
}
void ffta_action_queue_complete(unsigned *frame) {
    FFTA_ActionSnapshot *s=current();uintptr_t p=(uintptr_t)frame;
    if(!s || !ffta_action_owns_native_frame(frame) || s->phase!=FFTA_ACTION_EXECUTING || s->origin!=FFTA_ACTION_NATIVE_PRIMARY ||
       (p&3u) || p<0x03000000u || p>0x03008000u-0xb8)return;
    uintptr_t wrapper=frame[0x24/4];
    if((wrapper&3u) || wrapper<0x02000000u || wrapper>0x0203fffcu ||
       *(const uint8_t **)wrapper!=s->actor || frame[0x28/4]!=s->action_id)return;
    s->phase=FFTA_ACTION_COMPLETING;
    if(ffta_additional_reaction_queue)ffta_additional_reaction_queue(frame);
    s->phase=FFTA_ACTION_EXECUTING;
}
unsigned ffta_action_claim(uint8_t *unit,unsigned mask) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    if(!s || (s->phase!=FFTA_ACTION_RESULT && s->phase!=FFTA_ACTION_COMPLETING) || s->origin==FFTA_ACTION_UNKNOWN ||
       i<0 || !mask || mask>0xffff || (s->units[i].claims&mask))return 0;
    s->units[i].claims|=(uint16_t)mask;return 1;
}
unsigned ffta_action_claimed(const uint8_t *unit,unsigned mask) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    return i>=0 && mask && mask<=0xffff && (s->units[i].claims&mask)==mask;
}
void ffta_action_set_actor_flags(unsigned mask,unsigned value) {
    FFTA_ActionSnapshot *s=current();mask&=FFTA_ACTION_FLAG_JOB_MASK;
    if(!s || s->phase!=FFTA_ACTION_EXECUTING || !s->paid_count)return;
    for(unsigned i=0;i<s->count;++i)if(s->units[i].flags&4u)
        s->units[i].flags=(s->units[i].flags&~mask)|(value&mask);
}
void ffta_action_completed(const uint8_t *actor) {
    FFTA_ActionSnapshot *s=current();
    if(!s || s->actor!=actor || s->phase!=FFTA_ACTION_EXECUTING)return;
    s->result_object=0;
    s->phase=FFTA_ACTION_COMPLETING;
    if(ffta_additional_action_event)ffta_additional_action_event(actor,s->action_id,3);
    s->phase=FFTA_ACTION_EXECUTING;
}
void ffta_action_barrier_candidate(const uint8_t *unit,unsigned eligible) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    if(!s || s->phase!=FFTA_ACTION_RESULT || s->origin!=FFTA_ACTION_NATIVE_PRIMARY || i<0)return;
    const unsigned mask=1u<<24; /* centrally reserved TBN_CONSUMING */
    s->units[i].flags=(s->units[i].flags&~mask)|(eligible?mask:0);
}
unsigned ffta_action_hp_lost(const uint8_t *unit) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    return i>=0?s->units[i].hp_lost:0;
}
extern void ffta_additional_hp_loss(uint8_t *,unsigned,unsigned) __attribute__((weak));
void ffta_action_note_hp_loss(uint8_t *unit,unsigned before,unsigned after) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    if(!s || s->phase!=FFTA_ACTION_RESULT || s->origin==FFTA_ACTION_UNKNOWN ||
       i<0 || (s->units[i].flags&4u) || before<=after)return;
    unsigned loss=before-after;
    if(loss>0xffffu-s->units[i].hp_lost)loss=0xffffu-s->units[i].hp_lost;
    s->units[i].hp_lost=(uint16_t)(s->units[i].hp_lost+loss);
    if(ffta_additional_hp_loss)ffta_additional_hp_loss(unit,before,after);
}
/* Native HP application is shared by Fight and descriptor-driven actions.
 * A315A alone misses Fight's dedicated route. Read actual HP around the
 * original native writer; never derive committed loss from a magnitude. */
extern unsigned ffta_original_action_hp_apply(uint8_t *,int);
unsigned ffta_action_hp_apply(uint8_t *unit,int delta) {
    unsigned before=half(unit+0x18);
    unsigned result=ffta_original_action_hp_apply(unit,delta);
    ffta_action_note_hp_loss(unit,before,half(unit+0x18));
    return result;
}
unsigned ffta_poise_factor(const uint8_t *unit) {
    FFTA_ActionSnapshot *s=current();
    int i=find(s,unit);
    /* An active action never substitutes live identity for a copied recipient.
     * Copy observers explicitly propagate the original snapshot instead. */
    unsigned active=s?(i>=0?s->units[i].flags:0):0;
    if(!s && unit && ((unsigned (*)(const uint8_t *))0x080cd50du)(unit)==FFTA_SAM_S2)
        active=2u|ffta_poise_beneficial(unit);
    return (active&3u)==3?3:4;
}
unsigned ffta_poise_hp_factor(const uint8_t *actor,const uint8_t *target,unsigned action) {
    unsigned factor=ffta_poise_factor(target);
    FFTA_ActionSnapshot *s=current();int i=find(s,target);
    /* The actual executor has already resolved its reaction-enable flag,
     * recipient position and special-action gates. In particular Counter
     * passes reaction0 even when Damage-to-MP is equipped and MP remains. */
    if(i>=0 && (s->units[i].flags&8u) && !(s->units[i].flags&16u))return factor;
    /* Called only for a positive direct HP magnitude. Native reaction13 at
     * 12E986 requires MP, positive preview, then Fight OR (!flag17 && 1306E0).
     * Its common gates exclude self-targets and action265. Reuse all native
     * status/MP/action predicates. Both 12E6E0 and 1306E0 dispatch magnitude
     * again, so their positive-HP test is supplied by this caller's admitted
     * positive HP stage. Keeping that magnitude unscaled also prevents Poise
     * rounding it to zero before interception. Do not use for MP/cost stages. */
    action=(uint16_t)action;
    if(factor!=4 && actor && target && actor!=target && action!=265 &&
       ((unsigned (*)(const uint8_t *))0x0812e6a5u)(target)==13 &&
       ((unsigned (*)(const uint8_t *,unsigned))0x080c7ea5u)(target,0x15) &&
       (!action || !((unsigned (*)(unsigned,unsigned))0x080ccd51u)(action,17)))return 4;
    return factor;
}
extern unsigned ffta_primary_weapon(const uint8_t *);
unsigned ffta_blade_ward_ready(const uint8_t *unit) {
    if(!unit)return 0;
    unsigned reaction=((unsigned (*)(const uint8_t *))0x080cd4d5u)(unit);
    if(reaction!=FFTA_SAM_R1 && reaction!=FFTA_SLD_AX_R1)return 0;
    unsigned weapon=ffta_primary_weapon(unit);
    if(!weapon || ((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(weapon,3)!=(reaction==FFTA_SLD_AX_R1?31u:9u))return 0;
    /* Native Reflex availability: incapacity C8280, then its status mask5.
     * Never index native reaction/status tables with the custom ID128. */
    return !((unsigned (*)(const uint8_t *))0x080c8281u)(unit) &&
        ((unsigned (*)(const uint8_t *,unsigned))0x08133addu)(unit+0xe8,5);
}
unsigned ffta_blade_ward_factor(const uint8_t *actor,const uint8_t *target) {
    if(!actor || !target || actor==target)return 20;
    FFTA_ActionSnapshot *s=current();
    /* An unsnapshotted forecast only needs this recipient's Ward and native
     * allegiance. Avoid constructing every job's flags for both participants. */
    if(!s){
        if(!ffta_blade_ward_ready(target) ||
           (((actor[0x29]>>7)^((actor[0xeb]>>5)&1u))==(target[0x29]>>7)))return 20;
        return ((unsigned (*)(const uint8_t *))0x080cd4d5u)(target)==FFTA_SLD_AX_R1?15:13;
    }
    int a=find(s,actor),t=find(s,target);
    if(s && (!(s->reactions_enabled&255u) || a<0 || t<0))return 20;
    unsigned av=s->units[a].flags;
    unsigned tv=s->units[t].flags;
    /* Exact copied-actor provenance also rejects a copied self-target.
     * Charm reverses only the acting side, matching native action hostility. */
    if(!(tv&64u) || (s && (tv&4u)) || (((av>>7)^(av>>8))&1u)==((tv>>7)&1u))return 20;
    return tv&(1u<<30)?15:13;
}
unsigned ffta_action_reaction_forecast_enabled(void){
    FFTA_ActionSnapshot *s=current();return !s || (s->reactions_enabled&255u)!=0;
}
void ffta_action_restore_extension(const uint8_t *unit,unsigned value) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    if(s && i>=0 && s->phase==FFTA_ACTION_EXECUTING && s->origin==FFTA_ACTION_NATIVE_PRIMARY)
        extension_set(s,(unsigned)i,value);
}
unsigned ffta_action_export_unit(const uint8_t *unit,FFTA_ActionCarry *out) {
    FFTA_ActionSnapshot *s=current();int i=find(s,unit);
    if(!s || i<0 || !out || s->phase!=FFTA_ACTION_COMPLETING || s->origin!=FFTA_ACTION_NATIVE_PRIMARY)return 0;
    out->unit=s->units[i];out->extra=extra_get(s,(unsigned)i);out->extension=extension_get(s,(unsigned)i);
#if FFTA_CHEMIST_PROGRESSION
    out->medicine=cp_get(s,(unsigned)i);
#endif
    return 1;
}
void ffta_action_restore_unit(const FFTA_ActionCarry *in) {
    FFTA_ActionSnapshot *s=current();int i=in?find(s,in->unit.unit):-1;
    if(!s || i<0 || s->phase!=FFTA_ACTION_EXECUTING || s->origin!=FFTA_ACTION_NATIVE_PRIMARY || s->paid_count)return;
    s->units[i]=in->unit;extra_set(s,(unsigned)i,in->extra);extension_set(s,(unsigned)i,in->extension);
#if FFTA_CHEMIST_PROGRESSION
    cp_set(s,(unsigned)i,in->medicine);
#endif
}
void ffta_action_bind_queue_frame(const unsigned *frame) {
    FFTA_ActionSnapshot *s=current();uintptr_t p=(uintptr_t)frame,sp;
    __asm__ volatile("mov %0, sp":"=r"(sp));
    if(!s || s->result_object || s->phase!=FFTA_ACTION_EXECUTING || s->origin!=FFTA_ACTION_NATIVE_PRIMARY ||
       (p&3u) || p<sp || p<0x03000000u || p>0x03007f48u)return;
    uintptr_t w=frame[0x24/4];
    if((w&3u) || w<0x02000000u || w>0x0203fffcu ||
       *(const uint8_t **)w!=s->actor || frame[0x28/4]!=s->action_id)return;
    s->result_object=(const uint8_t *)frame;
}
extern void ffta_additional_before_fight(const uint8_t *,uint8_t *) __attribute__((weak));
void ffta_snapshot_native_reaction(const uint8_t *frame) {
    FFTA_ActionSnapshot *s=current();
    if(!s)return;
    unsigned row=*(const unsigned *)(frame+0x304);
    const uint8_t *rows=*(const uint8_t *const *)(frame+0x33c);
    const uint8_t *wrapper=*(const uint8_t *const *)(rows+44u*row);
    const uint8_t *unit=*(const uint8_t *const *)wrapper;
    int i=find(s,unit);
    unsigned value=i>=0?s->units[i].flags:flags(unit);
    unsigned reaction=*(const unsigned *)(frame+0x30c);
    record(s,unit,(value&~24u)|8u|(reaction==13?16u:0),0);
    if(ffta_additional_before_fight)ffta_additional_before_fight(s->actor,(uint8_t *)unit);
}
extern void ffta_on_unit_copy(uint8_t *,uint8_t *,unsigned);
void ffta_snapshotted_unit_copy(uint8_t *destination,uint8_t *source,unsigned length) {
    ffta_on_unit_copy(destination,source,length);
    if(length==264)ffta_snapshot_copy(destination,source);
}
unsigned ffta_snapshotted_evaluated_init(void *destination,const uint8_t *source) {
    unsigned result=ffta_evaluated_init(destination,source);
    if(result)ffta_snapshot_copy(destination,source);
    return result;
}
static void forget(uintptr_t first,uintptr_t last) {
    FFTA_ActionSnapshot *s=current();
    for(unsigned depth=0;s && depth<16;++depth) {
        if(!stack_frame(s) || s->magic!=MAGIC || s->self!=(uintptr_t)s || s->count>64)break;
        for(unsigned i=0;i<s->count;) {
            uintptr_t p=(uintptr_t)s->units[i].unit;
            if(p>=first && p<last) {
                s->units[i]=s->units[--s->count];
                extra_set(s,i,extra_get(s,s->count));extra_set(s,s->count,0);
                extension_set(s,i,extension_get(s,s->count));extension_set(s,s->count,0);
#if FFTA_CHEMIST_PROGRESSION
    cp_set(s,i,cp_get(s,s->count));cp_set(s,s->count,0);
#endif
                s->units[s->count].unit=0;s->units[s->count].flags=0;
                s->units[s->count].hp_lost=0;s->units[s->count].claims=0;
            } else ++i;
        }
        s=s->previous;
    }
}
void ffta_snapshotted_evaluated_close(void *unit) {
    ffta_evaluated_close(unit);
    forget((uintptr_t)unit,(uintptr_t)unit+1);
}
extern void ffta_copy_owner_free(void *);
void ffta_snapshotted_owner_free(void *allocation) {
    if(ffta_additional_workspace_retire)ffta_additional_workspace_retire(allocation);
    uintptr_t p=(uintptr_t)allocation;
    /* Called before the original native free changes the physical heap header.
     * Drop aliases to all copied units within the released payload. */
    if(!(p&3u) && p>=0x0200000cu && p<=0x0203f800u) {
        const uint16_t *header=(const uint16_t *)(p-12);
        unsigned size=4u*header[3];
        if(header[2]==0x616c && size>=12 && size-12<=0x0203f800u-p)
            forget(p,p+size-12);
    }
    ffta_copy_owner_free(allocation);
}
extern unsigned ffta_original_snapshot_result(uint8_t *,uint8_t *,uint8_t *,unsigned,unsigned,void *,unsigned,unsigned);
/* Integrated jobs may bind an exact, synchronous weapon component. The
 * original native frame is supplied only by its authenticated primary caller;
 * queued reactions and anonymous result calls never inherit that authority. */
extern unsigned ffta_additional_native_result(uint8_t *,uint8_t *,uint8_t *,unsigned,
    unsigned,void *,unsigned,unsigned,const unsigned *) __attribute__((weak));
static __attribute__((noinline)) unsigned run_result(uint8_t *object,uint8_t *wrapper,uint8_t *manager,unsigned flags_value,
    unsigned mode,void *scratch,unsigned secondary,unsigned last,unsigned caller,const unsigned *native_frame) {
    caller&=~1u;
    uint8_t *actor=object && *(uint8_t **)object?**(uint8_t ***)object:0;
    FFTA_ActionSnapshot *active=current();
    const uint8_t *previous_object=active?active->result_object:0;
    unsigned authenticated_frame=0;
    /* The exact native caller supplies its frame; never discover a frame by
     * scanning nearby stack words. Keep it in hidden EXECUTING metadata. */
    if(active && active->phase==FFTA_ACTION_EXECUTING &&
       active->origin==FFTA_ACTION_NATIVE_PRIMARY &&
       (caller==0x080a4856u || caller==0x080a4a9eu) && object && wrapper &&
       *(uint8_t **)object==wrapper && native_frame &&
       (uintptr_t)native_frame>=0x03000000u && (uintptr_t)native_frame<=0x03007f48u &&
       !( (uintptr_t)native_frame&3u ) && native_frame[0x24/4]==(uintptr_t)wrapper &&
       native_frame[0x28/4]==active->action_id){
       previous_object=(const uint8_t *)native_frame;
       authenticated_frame=1;
    }
    unsigned previous_reactions=active?active->reactions_enabled:0;
    unsigned previous_origin=active?active->origin:0,previous_phase=active?active->phase:0;
    unsigned previous_action=active?active->action_id:0,previous_category=active?active->category:0;
    if(active) {
        /* These two authenticated native callers retain the primary wrapper
         * in argument1 even while a queued Counter/Return Magic object uses
         * its different reacting wrapper. r3 is NOT an origin discriminator. */
        if((caller==0x080a4856u || caller==0x080a4a9eu) && object && wrapper) {
            active->origin=*(uint8_t **)object==wrapper?FFTA_ACTION_NATIVE_PRIMARY:FFTA_ACTION_NATIVE_REACTION;
            active->action_id=half(object+0x10);
            active->category=ffta_additional_action_category?ffta_additional_action_category(actor,active->action_id):0;
            active->phase=FFTA_ACTION_RESULT;active->result_object=object;
        } else { active->origin=FFTA_ACTION_UNKNOWN;active->phase=FFTA_ACTION_QUERY; }
    }
    if(active) {
        unsigned metadata=active->origin==FFTA_ACTION_NATIVE_REACTION ?
            ffta_reaction_request_metadata(native_frame,object,wrapper):0;
        active->reactions_enabled=((uint8_t)flags_value!=0)|metadata;
    }
    const unsigned *weapon_frame=active && active->phase==FFTA_ACTION_RESULT &&
        active->origin==FFTA_ACTION_NATIVE_PRIMARY && caller==0x080a4856u &&
        authenticated_frame?native_frame:0;
    unsigned result=ffta_additional_native_result?
        ffta_additional_native_result(object,wrapper,manager,flags_value,mode,scratch,secondary,last,weapon_frame):
        ffta_original_snapshot_result(object,wrapper,manager,flags_value,mode,scratch,secondary,last);
    if(active) {
        if(active->phase==FFTA_ACTION_RESULT && ffta_additional_action_event)
            ffta_additional_action_event(actor,active->action_id,2);
        active->result_object=previous_object;
        active->reactions_enabled=previous_reactions;active->origin=previous_origin;
        active->phase=previous_phase;active->action_id=previous_action;active->category=previous_category;
    }
    return result;
}
/* Put the large local in a separate, non-inlined function. Merely declaring it
 * in the public wrapper reserves820 bytes even for an ordinary continuation;
 * the nested native result calculators can then overwrite IWRAM code. */
static __attribute__((noinline)) unsigned stack_snapshot_result(uint8_t *object,uint8_t *wrapper,uint8_t *manager,unsigned flags_value,
    unsigned mode,void *scratch,unsigned secondary,unsigned last,unsigned caller,const unsigned *native_frame) {
    uint8_t *actor=object && *(uint8_t **)object?**(uint8_t ***)object:0;
    FFTA_ActionSnapshot snapshot;
    unsigned opened=ffta_snapshot_begin(&snapshot,actor,0,1);
    unsigned result=run_result(object,wrapper,manager,flags_value,mode,scratch,secondary,last,caller,native_frame);
    if(opened)ffta_snapshot_end(&snapshot);
    return result;
}
/* No bank frame (workspace allocation failed, or all eight slots busy): keep
 * the snapshot on the stack only with room for the deepest nested result
 * chain; otherwise resolve without one, like bank-less forecasts. */
static __attribute__((noinline)) unsigned stack_result(uint8_t *object,uint8_t *wrapper,uint8_t *manager,unsigned flags_value,
    unsigned mode,void *scratch,unsigned secondary,unsigned last,unsigned caller,const unsigned *native_frame) {
    if(ffta_stack_room(sizeof(FFTA_ActionSnapshot)+FFTA_RESULT_STACK_RESERVE))
        return stack_snapshot_result(object,wrapper,manager,flags_value,mode,scratch,secondary,last,caller,native_frame);
    return run_result(object,wrapper,manager,flags_value,mode,scratch,secondary,last,caller,native_frame);
}
static __attribute__((noinline)) unsigned fresh_result(uint8_t *object,uint8_t *wrapper,uint8_t *manager,unsigned flags_value,
    unsigned mode,void *scratch,unsigned secondary,unsigned last,unsigned caller,const unsigned *native_frame) {
    if(ffta_additional_workspace_prepare)ffta_additional_workspace_prepare();
    ResultStorage *bank=ffta_additional_result_storage?ffta_additional_result_storage():0;
    if(bank)for(unsigned i=0;i<8;i++)if(!extra_owner_active(&bank[i].frame)){
        FFTA_ActionSnapshot *snapshot=&bank[i].frame;
        uintptr_t token=(uintptr_t)snapshot;bank[i].token=&token;
        uint8_t *actor=object && *(uint8_t **)object?**(uint8_t ***)object:0;
        unsigned opened=ffta_snapshot_begin(snapshot,actor,0,1);
        unsigned result=run_result(object,wrapper,manager,flags_value,mode,scratch,secondary,last,caller,native_frame);
        if(opened)ffta_snapshot_end(snapshot);
        bank[i].token=0;return result;
    }
    /* Standalone overlays have no reserved bank. Their original stack path
     * remains available; native queued results are sequential, not recursive
     * reaction chains, so the eight root slots exceed their live requirement. */
    return stack_result(object,wrapper,manager,flags_value,mode,scratch,secondary,last,caller,native_frame);
}
unsigned ffta_snapshot_result(uint8_t *object,uint8_t *wrapper,uint8_t *manager,unsigned flags_value,
    unsigned mode,void *scratch,unsigned secondary,unsigned last,unsigned caller,const unsigned *native_frame) {
    uint8_t *actor=object && *(uint8_t **)object?**(uint8_t ***)object:0;
    if(continues(actor))return run_result(object,wrapper,manager,flags_value,mode,scratch,secondary,last,caller,native_frame);
    return fresh_result(object,wrapper,manager,flags_value,mode,scratch,secondary,last,caller,native_frame);
}
