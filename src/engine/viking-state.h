#ifndef FFTA_VIKING_STATE_H
#define FFTA_VIKING_STATE_H
#include <stdint.h>

/* Root owns the sixteen-byte record and copy/save bridge. These declarations
 * match its published job-state.h contract; no raw RAM address is assumed. */
uint8_t *ffta_job_state(uint8_t *unit);
unsigned ffta_job_origin(const uint8_t *unit);

#define FFTA_VIK_FLAG_ABSORB_READY (1u << 25)
#define FFTA_VIK_FLAG_GIL_READY (1u << 26)
#define FFTA_VIK_CLAIM_ABSORB 8u
#define FFTA_VIK_CLAIM_GIL 16u
unsigned ffta_viking_reaction_ready(const uint8_t *unit);

#define FFTA_VIK_CHALLENGER_SHIFT 16u
#define FFTA_VIK_CHALLENGER_MASK (63u << FFTA_VIK_CHALLENGER_SHIFT)

#define FFTA_VIK_WAR_CRY_APPLICATION 93u
#define FFTA_VIK_CHALLENGED_APPLICATION 94u
#define FFTA_VIK_WAR_CRY_DESCRIPTOR 211u
#define FFTA_VIK_CHALLENGED_DESCRIPTOR 212u
#define FFTA_VIK_WAR_CRY_ICON 31u
#define FFTA_VIK_CHALLENGED_ICON 32u

unsigned ffta_viking_war_cry(const uint8_t *unit);
unsigned ffta_viking_challenger(const uint8_t *unit);
void ffta_viking_grant_war_cry(uint8_t *unit,unsigned own_turn);
unsigned ffta_viking_grant_challenge(uint8_t *unit,const uint8_t *challenger);
void ffta_viking_turn_end(uint8_t *unit);
void ffta_viking_event(uint8_t *unit,unsigned event);
unsigned ffta_viking_snapshot_flags(const uint8_t *unit);
unsigned ffta_viking_gil_award(uint8_t *unit,unsigned actual_hp_lost);
uint8_t *ffta_viking_war_cry_apply(uint8_t *context);
uint8_t *ffta_viking_challenged_apply(uint8_t *context);
#endif
