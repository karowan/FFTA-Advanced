#ifndef FFTA_CHEMIST_STATE_H
#define FFTA_CHEMIST_STATE_H
#include <stdint.h>
#define FFTA_CHM_INOCULATED_MASK 7u
#define FFTA_CHM_POTION_LOCK 8u
unsigned ffta_inoculated_active(const uint8_t *unit);
unsigned ffta_inoculated_grant(uint8_t *unit,unsigned own_turn);
void ffta_chemist_turn_end(uint8_t *unit);
void ffta_chemist_event(uint8_t *unit,unsigned event);
unsigned ffta_chemist_native_curable(unsigned status);
unsigned ffta_chemist_prevent_native(const uint8_t *context,unsigned status);
uint8_t *ffta_chemist_inoculation(uint8_t *context);
#endif
