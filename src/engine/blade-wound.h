#ifndef FFTA_BLADE_WOUND_H
#define FFTA_BLADE_WOUND_H
#include <stdint.h>
/* Reserved save tail. The native state block remains 0x3ca8 bytes. */
#define FFTA_WOUND_OFFSET 0x1ebcu
#define FFTA_WOUND_COUNT 36u
#define FFTA_WOUND_BYTES 2u
uint8_t *ffta_state_wound(uint8_t *state,const uint8_t *unit);
uint8_t *ffta_owned_wound(uint8_t *unit);
void ffta_state_wound_swap(uint8_t *state,unsigned a,unsigned b);
void ffta_state_wound_clear(uint8_t *state,const uint8_t *unit);
unsigned ffta_wound_record_remaining(const uint8_t *record);
unsigned ffta_wound_record_replace(uint8_t *record,int reference);
unsigned ffta_wound_record_tick(uint8_t *record);
void ffta_wound_record_clear(uint8_t *record);
#endif
