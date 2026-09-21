#ifndef FFTA_EVALUATED_UNITS_H
#define FFTA_EVALUATED_UNITS_H
#include <stdint.h>
#include "job-state.h"
typedef struct {
    uint8_t unit[264];
    uint32_t magic;
    uintptr_t self;
    uint8_t exposed, wound[2], reserved;
    uint8_t job[FFTA_JOB_RECORD_BYTES], origin, potion, job_reserved[2];
} FFTA_EvaluatedUnit;
_Static_assert(sizeof(FFTA_EvaluatedUnit)==304,"evaluated unit container");
unsigned ffta_evaluated_init(FFTA_EvaluatedUnit *scope,const uint8_t *source);
void ffta_evaluated_close(FFTA_EvaluatedUnit *scope);
void *ffta_evaluated_allocate(unsigned requested);
uint8_t *ffta_evaluated_exposed(uint8_t *unit);
uint8_t *ffta_evaluated_wound(uint8_t *unit);
void ffta_evaluated_retire_heap(void *allocation);
uint8_t *ffta_evaluated_job(uint8_t *unit);
unsigned ffta_evaluated_origin(const uint8_t *unit);
uint8_t *ffta_evaluated_potion(uint8_t *unit);
void ffta_evaluated_reindex_heap(unsigned a,unsigned b);
#endif
