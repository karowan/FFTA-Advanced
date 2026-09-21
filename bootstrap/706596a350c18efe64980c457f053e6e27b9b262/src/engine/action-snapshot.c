#include "action-snapshot.h"
#include "samurai-state.h"
#include "registry.h"
#define MAGIC 0x31534e41u
/* Four private bytes after the Higan execution root; no saved-state alias. */
#define ACTIVE ((FFTA_ActionSnapshot *volatile *)0x0203ff48u)
static unsigned stack_frame(const FFTA_ActionSnapshot *s) {
    uintptr_t p=(uintptr_t)s,sp;
    __asm__ volatile("mov %0, sp":"=r"(sp));
    return !(p&3u) && p>=sp && p>=0x03000000u && p<=0x03008000u-sizeof(*s);
}
static FFTA_ActionSnapshot *current(void) {
    FFTA_ActionSnapshot *s=*ACTIVE;
    return stack_frame(s) && s->magic==MAGIC && s->self==(uintptr_t)s && s->count<=64?s:0;
}
/* These are native status bits, established by their actual application
 * callbacks: Regen31->3, Conceal60->12, Haste52->21, Shell83->24,
 * Protect82->25. Float/Last Resort/enchantments need their own future tagged
 * state providers; do not mistake equipment movement modes for a status. */
extern unsigned ffta_additional_beneficial(const uint8_t *) __attribute__((weak));
unsigned ffta_poise_beneficial(const uint8_t *unit) {
    if(!unit)return 0;
    return (unit[0xe8]&8u) || (unit[0xe9]&16u) || (unit[0xea]&32u) ||
        (unit[0xeb]&3u) || ffta_centered_active(unit) ||
        (ffta_additional_beneficial && ffta_additional_beneficial(unit));
}
static unsigned flags(const uint8_t *unit) {
    if(!unit)return 0;
    unsigned value=((unsigned)unit[0x29]>>7)*128u;
    if(unit[0xeb]&0x20u)value|=256u;
    if(((unsigned (*)(const uint8_t *))0x080cd50du)(unit)==FFTA_SAM_S2)
        value|=2u|ffta_poise_beneficial(unit);
    if(((unsigned (*)(const uint8_t *))0x080cd4d5u)(unit)==FFTA_SAM_R1)
        value|=32u|(ffta_blade_ward_ready(unit)?64u:0);
    return value;
}
static int find(const FFTA_ActionSnapshot *s,const uint8_t *unit) {
    if(s)for(unsigned i=0;i<s->count;++i)if(s->units[i].unit==unit)return (int)i;
    return -1;
}
static void record(FFTA_ActionSnapshot *s,const uint8_t *unit,unsigned value) {
    if(!unit)return;
    int i=find(s,unit);
    if(i<0) { if(s->count==64)return;i=(int)s->count++; }
    s->units[i].unit=unit;s->units[i].flags=value;
}
static unsigned continues(const uint8_t *actor) {
    FFTA_ActionSnapshot *s=current();int i=find(s,actor);
    return i>=0 && (s->units[i].flags&4u);
}
unsigned ffta_snapshot_begin(FFTA_ActionSnapshot *s,const uint8_t *actor,const uint8_t *target,unsigned battle) {
    if(!actor || !stack_frame(s))return 0;
    FFTA_ActionSnapshot *previous=current();
    if(s==previous)return 0;
    int actor_index=find(previous,actor);
    /* A native Counter uses the same outer executor but reverses actor and
     * recipient. Its preview is a new incoming action, not a continuation of
     * the attack it answers. Explicit copies retain the actor-role bit. */
    unsigned same_action=!battle && actor_index>=0 &&
        (previous->units[actor_index].flags&4u);
    s->magic=0;s->self=(uintptr_t)s;s->previous=previous;s->count=0;
    s->reactions_enabled=same_action?previous->reactions_enabled:1;
    const uint8_t *units[36];unsigned count=0,enabled=previous!=0;
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
        unsigned value=inherited>=0?previous->units[inherited].flags:flags(unit);
        if(unit==actor)value|=4u;
        record(s,unit,value);enabled|=value&34u;
    }
    if(!enabled) { s->self=0;s->previous=0;s->count=0;return 0; }
    s->magic=MAGIC;*ACTIVE=s;return 1;
}
void ffta_snapshot_end(FFTA_ActionSnapshot *s) {
    if(!s || current()!=s)return;
    *ACTIVE=s->previous;
    for(unsigned i=0;i<sizeof(*s);++i)((uint8_t *)s)[i]=0;
}
void ffta_snapshot_copy(uint8_t *destination,const uint8_t *source) {
    FFTA_ActionSnapshot *s=current();
    if(!s || !destination || !source)return;
    int i=find(s,source);
    record(s,destination,i>=0?s->units[i].flags:flags(source));
}
unsigned ffta_poise_factor(const uint8_t *unit) {
    FFTA_ActionSnapshot *s=current();
    int i=find(s,unit);
    /* An active action never substitutes live identity for a copied recipient.
     * Copy observers explicitly propagate the original snapshot instead. */
    unsigned active=s?(i>=0?s->units[i].flags:0):flags(unit);
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
    if(!unit || ((unsigned (*)(const uint8_t *))0x080cd4d5u)(unit)!=FFTA_SAM_R1)return 0;
    unsigned weapon=ffta_primary_weapon(unit);
    if(!weapon || ((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(weapon,3)!=9)return 0;
    /* Native Reflex availability: incapacity C8280, then its status mask5.
     * Never index native reaction/status tables with the custom ID128. */
    return !((unsigned (*)(const uint8_t *))0x080c8281u)(unit) &&
        ((unsigned (*)(const uint8_t *,unsigned))0x08133addu)(unit+0xe8,5);
}
unsigned ffta_blade_ward_factor(const uint8_t *actor,const uint8_t *target) {
    if(!actor || !target || actor==target)return 20;
    FFTA_ActionSnapshot *s=current();
    int a=find(s,actor),t=find(s,target);
    if(s && (!s->reactions_enabled || a<0 || t<0))return 20;
    unsigned av=s?s->units[a].flags:flags(actor);
    unsigned tv=s?s->units[t].flags:flags(target);
    /* Exact copied-actor provenance also rejects a copied self-target.
     * Charm reverses only the acting side, matching native action hostility. */
    if(!(tv&64u) || (s && (tv&4u)) || (((av>>7)^(av>>8))&1u)==((tv>>7)&1u))return 20;
    return 13;
}
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
    record(s,unit,(value&~24u)|8u|(reaction==13?16u:0));
}
extern void ffta_on_unit_copy(uint8_t *,uint8_t *,unsigned);
void ffta_snapshotted_unit_copy(uint8_t *destination,uint8_t *source,unsigned length) {
    ffta_on_unit_copy(destination,source,length);
    if(length==264)ffta_snapshot_copy(destination,source);
}
extern unsigned ffta_evaluated_init(void *,const uint8_t *);
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
                s->units[s->count].unit=0;s->units[s->count].flags=0;
            } else ++i;
        }
        s=s->previous;
    }
}
extern void ffta_evaluated_close(void *);
void ffta_snapshotted_evaluated_close(void *unit) {
    ffta_evaluated_close(unit);
    forget((uintptr_t)unit,(uintptr_t)unit+1);
}
extern void ffta_copy_owner_free(void *);
void ffta_snapshotted_owner_free(void *allocation) {
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
unsigned ffta_snapshot_result(uint8_t *object,uint8_t *wrapper,uint8_t *manager,unsigned flags_value,
    unsigned mode,void *scratch,unsigned secondary,unsigned last) {
    uint8_t *actor=object && *(uint8_t **)object?**(uint8_t ***)object:0;
    FFTA_ActionSnapshot snapshot;
    /* The native executor processes Counter/Return Magic result objects in
     * its own loop. Keep one fresh snapshot for the entire new actor's result,
     * including repeated preview/critical calculations and all its recipients. */
    unsigned opened=!continues(actor) && ffta_snapshot_begin(&snapshot,actor,0,1);
    FFTA_ActionSnapshot *active=current();
    unsigned previous_reactions=active?active->reactions_enabled:0;
    if(active)active->reactions_enabled=(uint8_t)flags_value!=0;
    unsigned result=ffta_original_snapshot_result(object,wrapper,manager,flags_value,mode,scratch,secondary,last);
    if(active)active->reactions_enabled=previous_reactions;
    if(opened)ffta_snapshot_end(&snapshot);
    return result;
}
