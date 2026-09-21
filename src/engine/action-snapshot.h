#ifndef FFTA_ACTION_SNAPSHOT_H
#define FFTA_ACTION_SNAPSHOT_H
#include <stdint.h>
typedef struct FFTA_ActionSnapshot FFTA_ActionSnapshot;
/* Existing bits0..8 retain Poise/Ward/actor/native-reaction/side semantics.
 * Additional providers own only their declared bits; claims are separate. */
#define FFTA_ACTION_FLAG_HARMFUL (1u<<9)
#define FFTA_ACTION_FLAG_OPPORTUNIST (1u<<10)
#define FFTA_ACTION_FLAG_AUTO_CUREALL (1u<<11)
#define FFTA_ACTION_FLAG_AUTO_POTION (1u<<12)
#define FFTA_ACTION_FLAG_DESPERATION (1u<<13)
#define FFTA_ACTION_FLAG_DESPERATION_ACTIVE (1u<<14)
#define FFTA_ACTION_CLAIM_AUTO_CUREALL 1u
#define FFTA_ACTION_CLAIM_AUTO_POTION 2u
#define FFTA_ACTION_FLAG_JOB_MASK 0xfffffe00u
enum { FFTA_ACTION_UNKNOWN=0, FFTA_ACTION_NATIVE_PRIMARY=1,
       FFTA_ACTION_NATIVE_REACTION=2, FFTA_ACTION_EXPLICIT_COMBO=3 };
enum { FFTA_ACTION_QUERY=0, FFTA_ACTION_EXECUTING=1,
       FFTA_ACTION_RESULT=2, FFTA_ACTION_COMPLETING=3 };
enum { FFTA_ACTION_UNCLASSIFIED=0, FFTA_ACTION_PHYSICAL=1,
       FFTA_ACTION_MAGICAL=2, FFTA_ACTION_ITEM=4, FFTA_ACTION_COMBO=8 };
typedef struct {
    const uint8_t *unit;
    unsigned flags;
    uint16_t hp_lost,claims;
} FFTA_SnapshotUnit;
struct FFTA_ActionSnapshot {
    uint32_t magic;
    uintptr_t self;
    FFTA_ActionSnapshot *previous;
    unsigned count;
    unsigned reactions_enabled; /* low8 native permission, upper24 exact queued kind/value */
    FFTA_SnapshotUnit units[64];
    unsigned action_id,origin,category,phase;
    /* Keep the820-byte ABI: payment count and actual MP debit share the
     * former32-bit count word. Both are independently bounded quantities. */
    uint16_t paid_count,mp_spent;
    /* MP holds the pre-payment baseline until the first paid callback. The
     * public post-cost getter intentionally returns zero while unpaid. */
    uint16_t post_cost_hp,post_cost_mp;
    const uint8_t *actor;
    const uint8_t *result_object; /* RESULT object; hidden bound native frame while EXECUTING */
};
_Static_assert(sizeof(FFTA_ActionSnapshot)==820,"action snapshot ABI");
/* The820-byte payload is unchanged. Root may lend a reserved fresh-result
 * frame authenticated by a live stack token; ordinary scopes stay on stack.
 * A native primary executor is not proof of a player-voluntary action or
 * own-turn eligibility. Native reaction origin is independently established
 * from authenticated result caller and exact primary/acting wrappers.
 * Incoming reactions_enabled remains an independent native engine flag. */
void ffta_action_started(const uint8_t *,unsigned,unsigned,unsigned);
void ffta_action_paid(const uint8_t *,unsigned);
unsigned ffta_action_id(void);
unsigned ffta_action_origin(void);
unsigned ffta_action_category(void);
unsigned ffta_action_phase(void);
/* Native permission only during authenticated RESULT; COMPLETING is not evidence. */
unsigned ffta_action_reactions_enabled(void);
/* Read-only permission for damage forecasts, including nested query scopes. */
unsigned ffta_action_reaction_forecast_enabled(void);
unsigned ffta_action_paid_count(void);
unsigned ffta_action_mp_spent(void);
unsigned ffta_action_post_cost_hp(void);
unsigned ffta_action_post_cost_mp(void);
const uint8_t *ffta_action_actor(void);
/* Exact native object only while its authenticated RESULT scope is active. */
const uint8_t *ffta_action_result_object(void);
/* Read-only nested forecasts may retain an exact live result owner. This
 * grants no RESULT phase or permission to mutate/claim from a query. */
unsigned ffta_action_in_result(const uint8_t *object,const uint8_t *actor);
unsigned ffta_action_unit_flags(const uint8_t *);
unsigned ffta_action_unit_extra_flags(const uint8_t *);
unsigned ffta_action_claim_extra(uint8_t *,unsigned);
/* Compressed extension: public bits0..9 are frozen data,16..21 are claims.
 * Other bits are rejected. Eight arrays of64 halfwords share the exact owner
 * of the first external word, preserving its copy/retirement ownership.
 * No save or stack bytes are added; both banks are separately reserved. */
unsigned ffta_action_unit_extension_flags(const uint8_t *);
unsigned ffta_action_unit_extension_support_flags(const uint8_t *);
unsigned ffta_action_unit_extension_reaction_flags(const uint8_t *);
unsigned ffta_action_claim_extension(uint8_t *,unsigned);
/* Controller-owned continuation may restore this bank only at native action
 * start; it never writes claims from a query/result or invents a new unit. */
void ffta_action_restore_extension(const uint8_t *,unsigned);
typedef struct { FFTA_SnapshotUnit unit;unsigned extra,extension; } FFTA_ActionCarry;
_Static_assert(sizeof(FFTA_ActionCarry)==20,"action continuation unit");
unsigned ffta_action_export_unit(const uint8_t *,FFTA_ActionCarry *);
void ffta_action_restore_unit(const FFTA_ActionCarry *);
/* Called only by the installed queue-entry assembly with its actual native
 * body SP. Empty actions have no result callback to bind this frame. */
void ffta_action_bind_queue_frame(const unsigned *);
const uint8_t *ffta_action_unit_at(unsigned);
unsigned ffta_action_reaction_kind(void);
unsigned ffta_action_reaction_value(void);
void ffta_action_queue_complete(unsigned *native_frame);
unsigned ffta_action_claim(uint8_t *,unsigned);
unsigned ffta_action_claimed(const uint8_t *,unsigned);
void ffta_action_set_actor_flags(unsigned,unsigned);
/* Transient pre-barrier HP eligibility for the exact current recipient.
 * Does not alter frozen status/equipment tags or acquire a reaction claim. */
void ffta_action_barrier_candidate(const uint8_t *,unsigned);
void ffta_action_completed(const uint8_t *);
unsigned ffta_action_hp_lost(const uint8_t *);
void ffta_action_note_hp_loss(uint8_t *,unsigned,unsigned);
unsigned ffta_snapshot_begin(FFTA_ActionSnapshot *,const uint8_t *,const uint8_t *,unsigned);
void ffta_snapshot_end(FFTA_ActionSnapshot *);
void ffta_snapshot_copy(uint8_t *,const uint8_t *);
unsigned ffta_poise_factor(const uint8_t *);
unsigned ffta_poise_hp_factor(const uint8_t *,const uint8_t *,unsigned);
unsigned ffta_poise_beneficial(const uint8_t *);
unsigned ffta_blade_ward_ready(const uint8_t *);
unsigned ffta_blade_ward_factor(const uint8_t *,const uint8_t *);
#endif
