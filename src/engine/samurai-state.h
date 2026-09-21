#ifndef FFTA_SAMURAI_STATE_H
#define FFTA_SAMURAI_STATE_H
#include <stdint.h>
#define FFTA_CENTERED_MASK 0x0eu
/* Bits1..2 hold remaining subsequent turns; bit3 skips the application
 * turn. Encoded7 is reserved for a consumed, current-execution snapshot.
 * It is never a beneficial status and must retire at the executor return. */
unsigned ffta_centered_active(const uint8_t *unit);
unsigned ffta_centered_factor(const uint8_t *unit,unsigned action);
void ffta_centered_grant(uint8_t *unit,unsigned application_is_own_turn);
void ffta_centered_clear(uint8_t *unit);
void ffta_centered_turn_end(uint8_t *unit);
unsigned ffta_centered_paid(uint8_t *unit,unsigned action);
void ffta_centered_retire(uint8_t *unit);
void ffta_centered_event(uint8_t *unit,unsigned event);
unsigned ffta_samurai_direct_action(unsigned action);
unsigned ffta_centered_consuming_action(unsigned action);
#endif
