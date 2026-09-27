#ifndef FFTA_CHEMIST_PROGRESSION_H
#define FFTA_CHEMIST_PROGRESSION_H
#include <stdint.h>
#ifndef FFTA_CHEMIST_PROGRESSION
#define FFTA_CHEMIST_PROGRESSION 0
#endif
#define FFTA_PHY_FIRST 446u
#define FFTA_PHY_LAST 452u
#define FFTA_SAP_FIRST 453u
#define FFTA_SAP_LAST 459u
#define FFTA_PHY_SUPPORT 146u
#define FFTA_SAP_SUPPORT 147u
#define FFTA_PHY_REACTION 146u
#define FFTA_SAP_REACTION 147u
/* Schema 3 appends five bytes in RAM; flash uses a validated packed envelope.
 * Timers are 2 remaining bits plus an application-turn skip bit. The fuse
 * retains an exact cohort origin, never a pointer or guessed character ID.
 * Tile coordinates use nibbles only after a legal 0..15 map check. */
#define FFTA_CP_MEDIC 22u /* Triage0..2, Ward3..5, Dressing lock6 */
#define FFTA_CP_TIMERS 23u /* Smoke0..2, Tripwire3..5, Fuse6..7 */
#define FFTA_CP_FUSE_OWNER 24u
#define FFTA_CP_TRAP_TILE 25u
#define FFTA_CP_FUSE_TILE 26u
/* One additional snapshot word: lower 22 bits freeze action-start data;
 * upper ten are exact-action claims. No query may write claims. */
#define FFTA_CP_AILMENTS 8191u
#define FFTA_CP_TRIAGE (1u<<13)
#define FFTA_CP_WARD (1u<<14)
#define FFTA_CP_SMOKE (1u<<15)
#define FFTA_CP_FOLLOWUP (1u<<16)
#define FFTA_CP_SPOTTER (1u<<17)
#define FFTA_CP_DRESSING (1u<<18)
#define FFTA_CP_DUCK (1u<<19)
#define FFTA_CP_FORCED (1u<<20)
#define FFTA_CP_ADJACENT (1u<<21)
#define FFTA_CP_CURED (1u<<22)
#define FFTA_CP_WARD_USED (1u<<23)
#define FFTA_CP_DAMAGED (1u<<24)
#define FFTA_CP_DRESSING_QUEUED (1u<<25)
#define FFTA_CP_FOLLOWUP_QUEUED (1u<<26)
#define FFTA_CP_TRIAGE_QUEUED (1u<<27)
#define FFTA_CP_DRESSING_ADMITTED (1u<<28)
#define FFTA_CP_WARD_CANDIDATE (1u<<29)
#define FFTA_CP_TRIAGE_ACTION 460u
#define FFTA_CP_FOLLOWUP_ACTION 461u
#define FFTA_CP_DRESSING_ACTION 462u
unsigned ffta_cp_flags(const uint8_t *);
unsigned ffta_cp_combat_flags(const uint8_t *);
unsigned ffta_action_cp_combat_flags(const uint8_t *);
unsigned ffta_cp_spotter_adjacency(const uint8_t *,const uint8_t *);
unsigned ffta_action_cp_flags(const uint8_t *);
unsigned ffta_action_cp_claim(uint8_t *,unsigned);
void ffta_action_cp_candidate(const uint8_t *,unsigned);
void ffta_cp_candidate(const uint8_t *,const uint8_t *,unsigned,unsigned);
unsigned ffta_cp_ailments(const uint8_t *);
unsigned ffta_cp_eligibility(const uint8_t *);
int ffta_cp_healing(const uint8_t *);
int ffta_cp_revive(const uint8_t *);
uint8_t *ffta_cp_apply(uint8_t *);
void ffta_cp_event(uint8_t *,unsigned);
void ffta_cp_turn_end(uint8_t *);
void ffta_cp_action_event(const uint8_t *,unsigned,unsigned);
void ffta_cp_hp_loss(uint8_t *,unsigned,unsigned);
void ffta_cp_direct_hit(uint8_t *,unsigned);
void ffta_cp_queue(unsigned *);
unsigned ffta_cp_damage_factor(const uint8_t *,const uint8_t *,unsigned);
unsigned ffta_cp_status_icon(const uint8_t *,unsigned);
unsigned ffta_cp_ai_buff(unsigned);
int ffta_cp_ai_value(int,const uint8_t *,const uint8_t *,unsigned);
void ffta_cp_ai_row(uint8_t *,const uint8_t *,const uint8_t *,unsigned);
uint8_t *ffta_cp_application_observer(uint8_t *);
unsigned ffta_cp_record_pack(uint8_t *,const uint8_t *);
unsigned ffta_cp_record_unpack(uint8_t *,const uint8_t *);
unsigned ffta_cp_rider(const uint8_t *);
int ffta_cp_magnitude(const uint8_t *);
unsigned ffta_cp_accuracy(const uint8_t *,unsigned);
unsigned ffta_cp_empty_tile(const uint8_t *,unsigned,unsigned);
unsigned ffta_cp_trap_at(const uint8_t *,unsigned,unsigned);
void ffta_cp_position_changed(uint8_t *,unsigned,unsigned);
int ffta_cp_fuse_damage(const uint8_t *,const uint8_t *);
void ffta_cp_fuse_prepare(uint8_t *,uint8_t *);
unsigned ffta_cp_fuse_next(uint8_t *);
unsigned ffta_cp_battle_tick(uint8_t *,unsigned,unsigned);
void ffta_cp_trap_slow(uint8_t *,uint8_t *);
unsigned ffta_cp_ai_trap_search(uint8_t *,unsigned);
#endif
