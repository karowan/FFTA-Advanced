#ifndef FFTA_JOB_STATE_H
#define FFTA_JOB_STATE_H
#include <stdint.h>
/* Shared API contract for independent job implementation. Integration and
 * native persistence acceptance are owned by the primary checkout. */
#define FFTA_JOB_RECORD_BYTES 22u
#define FFTA_JOB_UNIT_COUNT 36u
#define FFTA_JOB_BANK_BYTES (16u+FFTA_JOB_UNIT_COUNT*FFTA_JOB_RECORD_BYTES)
#define FFTA_JOB_FOOTER_BYTES (32u+FFTA_JOB_UNIT_COUNT*FFTA_JOB_RECORD_BYTES)
/* Remaining-job reservation; allocation does not implement the effects.
 * Preserve full native coordinate bytes, not a guessed smaller map domain.
 * Byte3 was unused in schema1; all established effect offsets stay fixed. */
#define FFTA_JOB_DNC_FLAGS 3u /* Polka T2 bits0..2, Frolic T2 bits3..5, Fury6..7 */
#define FFTA_JOB_GEO_FIELD_X 15u
#define FFTA_JOB_GEO_FIELD_Y 16u
#define FFTA_JOB_GEO_FIELD_FLAGS 17u /* kind0..1, T2 bits2..4, Wisp T2 bits5..7 */
#define FFTA_JOB_GEO_TRAVERSAL 18u /* Wisp strength0, Move T2 bits1..3, Jump T2 bits4..6 */
#define FFTA_JOB_GEO_STEADY 19u /* displacement immunity T2 bits0..2 ONLY */
/* Shared byte19: turn allowance high2 bits3..4, capped step remainder5..6,
 * authenticated allowance bit7. Byte14 high5 holds allowance low5.
 * Geomancer readers/writers must preserve this movement ledger. */
#define FFTA_JOB_MYK_BLADE 20u /* 16-bit: enchant0..3, primary item4..12, sequence13..14 */
#define FFTA_JOB_DRK_OFFSET 0u
#define FFTA_JOB_VIK_OFFSET 4u
#define FFTA_JOB_CHM_OFFSET 8u
/* NULL for foreign/retired units. Exact copies have independent records.
 * Origin is0 for unknown,1..24 party,25..36 enemy. It is propagated only
 * through explicit owned copies, never recovered by character identity. */
uint8_t *ffta_job_state(uint8_t *unit);
unsigned ffta_job_origin(const uint8_t *unit);
/* Exact same-owner cohort only; no copied-to-live fallback. Enumeration writes
 * the complete group only if output/capacity suffice, otherwise returns0.
 * Single lookup returns NULL for unrepresented or ambiguous duplicate origins.
 * Missing representation is not evidence that the source has died. */
unsigned ffta_job_peers(uint8_t *unit,uint8_t **output,unsigned capacity);
uint8_t *ffta_job_peer(uint8_t *unit,unsigned origin);
/* Existing saved preference, including explicit owned/evaluated copies. */
uint8_t *ffta_job_potion(uint8_t *unit);
void ffta_job_reset(void);
/* Native persistent roster operations only, never simulated KO/status events.
 * Exchange a/b tokens; b=0 forgets a without assigning unknown links. */
void ffta_job_record_reindex(uint8_t *record,unsigned a,unsigned b);
void ffta_job_swap(unsigned a,unsigned b);
void ffta_job_forget_origin(unsigned token);
void ffta_job_footer_encode(uint8_t *output,unsigned generation);
unsigned ffta_job_footer_decode(uint8_t *input,unsigned generation);
#endif
