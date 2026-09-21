#ifndef FFTA_AI_CHOICE_H
#define FFTA_AI_CHOICE_H
#include <stdint.h>
typedef struct FFTA_AIChoiceScope {
 volatile unsigned magic;
 const void *self;
 const uint8_t *actor;
 unsigned action,choice,position;
 struct FFTA_AIChoiceScope *previous;
} FFTA_AIChoiceScope;
void ffta_ai_choice_begin(FFTA_AIChoiceScope *,const uint8_t *,unsigned,unsigned,unsigned);
void ffta_ai_choice_end(FFTA_AIChoiceScope *);
unsigned ffta_ai_preview_choice(const uint8_t *,unsigned);
unsigned ffta_ai_position(const uint8_t *,int *,int *);
unsigned ffta_geo_ai_row_options(FFTA_AIChoiceScope *,uint8_t *,unsigned *);
unsigned ffta_geo_ai_utility(unsigned);
int ffta_geo_ai_utility_value(int,const uint8_t *,const uint8_t *,unsigned);
void ffta_geo_ai_utility_row(uint8_t *,const uint8_t *,const uint8_t *,unsigned);
unsigned ffta_geo_ai_recipients(const uint8_t *,const uint8_t **);
unsigned ffta_geo_ai_utility_search(uint8_t *,unsigned);
#endif
