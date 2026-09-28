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
_Static_assert(sizeof(FFTA_EvaluatedUnit)==(FFTA_CHEMIST_PROGRESSION?308u:304u),"evaluated unit container");
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
#if FFTA_CHEMIST_PROGRESSION
/* Borrow ownership during a synchronous, read-only formula/provider group.
 * Never span an allocator, container-identity mutation or native execution.
 * The unit-copy hook invalidates callers before borrowing its own fresh views.
 * Values are still read live; only exact container ownership is borrowed. */
typedef struct FFTA_UnitReadScope FFTA_UnitReadScope;
struct FFTA_UnitReadScope {
    uintptr_t self;FFTA_UnitReadScope *previous;uint8_t *unit,*exposed;
};
void ffta_unit_read_begin(FFTA_UnitReadScope *,const uint8_t *);
void ffta_unit_read_end(FFTA_UnitReadScope *);
void ffta_unit_read_invalidate(void);
#endif
#endif
