#ifndef FFTA_ABILITIES_H
#define FFTA_ABILITIES_H
#include <stdint.h>
unsigned ffta_job_lesson_count(unsigned job);
unsigned ffta_job_lesson_at(unsigned job, unsigned position);
uint8_t *ffta_ap_address(uint8_t *unit, unsigned index);
unsigned ffta_ability_available(uint8_t *unit, unsigned index);
void ffta_ability_grant(uint8_t *unit, unsigned index);
unsigned ffta_job_mastered(uint8_t *unit, unsigned job);
unsigned ffta_job_action_count(uint8_t *unit, unsigned job, unsigned include_equipped);
unsigned ffta_new_job_eligible(uint8_t *unit, unsigned job);
#endif
