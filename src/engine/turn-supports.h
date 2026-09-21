#ifndef FFTA_TURN_SUPPORTS_H
#define FFTA_TURN_SUPPORTS_H
#include <stdint.h>
#define FFTA_COMPOSURE_READY (1u<<15)
#define FFTA_FOLLOW_THROUGH_READY (1u<<7) /* extra snapshot bank */
void ffta_turn_event(uint8_t *,unsigned);
void ffta_turn_end(uint8_t *);
unsigned ffta_turn_flag(unsigned,unsigned,unsigned);
unsigned ffta_turn_snapshot_flags(const uint8_t *);
unsigned ffta_turn_extra_flags(const uint8_t *);
unsigned ffta_turn_original_allowance(const uint8_t *);
unsigned ffta_turn_step_remaining(const uint8_t *);
void ffta_turn_close_movement(uint8_t *);
unsigned ffta_turn_damage_numerator(const uint8_t *,const uint8_t *,unsigned,unsigned);
unsigned ffta_turn_healing_numerator(const uint8_t *);
#endif
