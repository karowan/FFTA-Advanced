#include "mission-recovery.h"
#include "mission-recovery-data.h"

/* All earned/consumed edges are nonrepeatable original missions. Completion flags
 * count original earned copies and legitimate expenditure, not recovery claims.
 * No additional persistent state or gear-inventory namespace is involved. */
static unsigned completed(unsigned mission) {
    const volatile uint8_t *flags=(const volatile uint8_t *)0x02001f70u;
    unsigned index=mission+0x2ffu;
    return (flags[index>>3]>>(index&7u))&1u;
}

static unsigned is_recovery(unsigned mission) {
    return mission>=FFTA_RECOVERY_FIRST &&
        mission<FFTA_GEAR_RECOVERY_FIRST+FFTA_GEAR_RECOVERY_COUNT;
}

static unsigned gear_needed(unsigned mission) {
    const FFTA_GearRecoveryRule *rule=&ffta_gear_recovery_rules[mission-FFTA_GEAR_RECOVERY_FIRST];
    const volatile uint8_t *state=(const volatile uint8_t *)0x02000000u;
    /* Original cleared-game flag plus original mission completion or clan-gift
     * receipt, not a new recovery completion flag. Merely reaching a gift's
     * skill threshold is insufficient: its original consumer must claim it.
     * Native owned totals include equipped copies.
     * The expansion's migrated inventory is a count table at1940, not the
     * original four-byte equipment records or the separate quest-item bag. */
    unsigned bit=ffta_gear_recovery_required_flag;
    unsigned original=rule->original_mission!=0xffffu ? completed(rule->original_mission) :
        ((state[0x2c08u+(rule->original_gift>>3)]>>(rule->original_gift&7u))&1u);
    return ((state[0x1f70u+(bit>>3)]>>(bit&7u))&1u) &&
        original && !state[0x1940u+rule->item];
}

unsigned ffta_recovery_needed(unsigned mission) {
    if(mission>=FFTA_GEAR_RECOVERY_FIRST && mission<FFTA_GEAR_RECOVERY_FIRST+FFTA_GEAR_RECOVERY_COUNT)
        return gear_needed(mission);
    if(mission<FFTA_RECOVERY_FIRST || mission>=FFTA_RECOVERY_FIRST+FFTA_RECOVERY_COUNT)
        return 0;
    const FFTA_RecoveryRule *rule=&ffta_recovery_rules[mission-FFTA_RECOVERY_FIRST];
    unsigned earned=0,spent=0,needed=0,held=0;
    for(unsigned i=0;i<rule->source_count;i++)
        if(completed(rule->sources[i].mission))earned+=rule->sources[i].copies;
    for(unsigned i=0;i<rule->use_count;i++) {
        const FFTA_RecoveryUse *use=&rule->uses[i];
        unsigned done=completed(use->mission);
        if(done)spent+=use->consumed;
        if((!done || use->repeatable) && use->required>needed)needed=use->required;
    }
    if(!needed || earned<=spent)return 0;
    unsigned entitlement=earned-spent;
    if(entitlement<needed)needed=entitlement;
    const volatile uint8_t *inventory=(const volatile uint8_t *)0x02002b08u;
    for(unsigned i=0;i<64;i++)if(inventory[i*4]==rule->item)held++;
    return held<needed;
}

unsigned ffta_recovery_pub_mask(unsigned mission,unsigned native_mask) {
    /* Free obsolete unaccepted offers before the512-slot generator searches
     * for empty cache records. Index1 is its single first iteration. */
    if(mission==1u)ffta_recovery_prune_offers();
    if(is_recovery(mission)) {
        if(!native_mask || !ffta_recovery_needed(mission))return 0;
        /* Native insertion evicts an ordinary posting when all64 slots are
         * occupied. Optional recovery must wait for space, never replace it. */
        const volatile uint8_t *cache=(const volatile uint8_t *)0x020021c8u;
        for(unsigned i=0;i<64;i++)
            if(!cache[i*16] && !(cache[i*16+1]&3u))return native_mask;
        return 0;
    }
    return native_mask;
}

unsigned ffta_recovery_cached_allowed(const uint8_t *cached) {
    if(!cached)return 0;
    unsigned mission=cached[0]|((cached[1]&3u)<<8);
    if(!is_recovery(mission))
        return 1;
    return ffta_recovery_needed(mission);
}

/* Recovery routes are services, outside the original mission-completion
 * ledger. Do not claim formerly unused flags which event scripts may read. */
void ffta_recovery_complete_original(unsigned mission,unsigned result) {
    if((result&0xfeu)!=0xc8u)return;
    if(is_recovery(mission))return;
    ((void (*)(unsigned,unsigned))0x080c9575u)(mission+0x2ffu,1);
}

/* Native linked posting nodes: {cached record, previous, next}. Prune only
 * unaccepted offers (state1 displayed or state2 undisplayed); active/cooling missions
 * retain native ownership. This runs before native list construction, never
 * while a list is being enumerated or a selected dispatch is committed. */
typedef struct RecoveryPosting RecoveryPosting;
struct RecoveryPosting {
    uint8_t *record;
    RecoveryPosting *previous, *next;
};

static unsigned valid_node(const RecoveryPosting *node) {
    uintptr_t at=(uintptr_t)node;
    return !at || (at>=0x020025c8u && at<0x020028c8u && (at-0x020025c8u)%12u==0);
}

void ffta_recovery_prune_offers(void) {
    RecoveryPosting *nodes=(RecoveryPosting *)0x020025c8u;
    RecoveryPosting **head=(RecoveryPosting **)0x020028c8u;
    for(unsigned i=0;i<64;i++) {
        RecoveryPosting *node=&nodes[i];
        uint8_t *record=node->record;
        uintptr_t at=(uintptr_t)record;
        if(at<0x020021c8u || at>=0x020025c8u || (at-0x020021c8u)%16u)continue;
        unsigned state=record[2]&0x1cu;
        if((state!=4u && state!=8u) || ffta_recovery_cached_allowed(record))continue;
        RecoveryPosting *previous=node->previous,*next=node->next;
        if(!valid_node(previous) || !valid_node(next) || previous==node || next==node)continue;
        if(previous ? previous->next!=node : *head!=node)continue;
        if(next && next->previous!=node)continue;
        if(previous)previous->next=next;else *head=next;
        if(next)next->previous=previous;
        for(unsigned byte=0;byte<16;byte++)record[byte]=0;
        node->record=0;
        /* Native removal leaves the detached links; no fixture or observer
         * should confuse a null record with a live posting. */
    }
}
