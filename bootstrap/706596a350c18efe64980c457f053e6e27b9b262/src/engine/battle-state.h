#ifndef FFTA_BATTLE_STATE_H
#define FFTA_BATTLE_STATE_H
#include <stdint.h>
/* Saved-state-relative domains:24 party and12 enemy native108-byte records. */
#define FFTA_EXPOSED_OFFSET 0x1e98u
#define FFTA_EXPOSED_COUNT 36u
uint8_t *ffta_state_exposed(uint8_t *state,const uint8_t *unit);
void ffta_state_exposed_swap(uint8_t *state,unsigned a,unsigned b);
void ffta_state_exposed_clear(uint8_t *state,const uint8_t *unit);
uint8_t *ffta_owned_exposed(uint8_t *unit);
#endif
