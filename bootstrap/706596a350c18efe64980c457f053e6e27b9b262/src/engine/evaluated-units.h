#ifndef FFTA_EVALUATED_UNITS_H
#define FFTA_EVALUATED_UNITS_H
#include <stdint.h>
typedef struct {
    uint8_t unit[264];
    uint32_t magic;
    uintptr_t self;
    uint8_t exposed, wound[2], reserved;
} FFTA_EvaluatedUnit;
_Static_assert(sizeof(FFTA_EvaluatedUnit)==276,"evaluated unit container");
unsigned ffta_evaluated_init(FFTA_EvaluatedUnit *scope,const uint8_t *source);
void ffta_evaluated_close(FFTA_EvaluatedUnit *scope);
void *ffta_evaluated_allocate(unsigned requested);
uint8_t *ffta_evaluated_exposed(uint8_t *unit);
uint8_t *ffta_evaluated_wound(uint8_t *unit);
void ffta_evaluated_retire_heap(void *allocation);
#endif
