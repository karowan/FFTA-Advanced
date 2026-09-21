#ifndef FFTA_PASSING_STEP_H
#define FFTA_PASSING_STEP_H
#include <stdint.h>
void ffta_passing_begin(uint8_t *);
int ffta_passing_poll(uint8_t *,unsigned,unsigned);
unsigned ffta_passing_after_action(void);
unsigned ffta_passing_ai_prepare(void);
void ffta_passing_action_event(const uint8_t *,unsigned,unsigned);
void ffta_passing_lifecycle(uint8_t *,unsigned);
void ffta_passing_turn_end(uint8_t *);
#endif
