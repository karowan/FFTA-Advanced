#ifndef FFTA_MEDICINE_AI_H
#define FFTA_MEDICINE_AI_H
#include <stdint.h>
unsigned ffta_medicine_available(const uint8_t *,unsigned);
unsigned ffta_medicine_choice_valid(unsigned,unsigned);
void ffta_medicine_ai_row(uint8_t *,const uint8_t *,const uint8_t *,unsigned,unsigned);
int ffta_medicine_ai_value(const uint8_t *,const uint8_t *,unsigned,unsigned);
unsigned ffta_medicine_ai_search(uint8_t *,unsigned);
#endif
