#include "execution-scope.h"
#include "registry.h"
#define SCOPE_MAGIC 0x31584546u
/* Private Samurai build reserves four additional bytes beyond the existing
 * twenty-byte copy-owner root. There is no implicit mutable ROM-module BSS. */
#define ACTIVE ((FFTA_ExecutionScope *volatile *)0x0203ff44u)
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
static unsigned stack_scope(const FFTA_ExecutionScope *scope) {
    uintptr_t p=(uintptr_t)scope,sp;
    __asm__ volatile("mov %0, sp":"=r"(sp));
    return !(p&3u) && p>=sp && p>=0x03000000u &&
        p<=0x03008000u-sizeof(*scope);
}
static FFTA_ExecutionScope *current(void) {
    FFTA_ExecutionScope *scope=*ACTIVE;
    return stack_scope(scope) && scope->self==(uintptr_t)scope &&
        scope->magic==SCOPE_MAGIC ? scope : 0;
}
unsigned ffta_execution_open(FFTA_ExecutionScope *scope,const uint8_t *actor,unsigned action) {
    FFTA_ExecutionScope *previous=current();
    /* Standalone original actions do not touch the private root. A nested
     * action receives its own scope so it cannot overwrite an outer capture. */
    if(!actor || !stack_scope(scope) || (action!=FFTA_SAM_A9 && !previous))return 0;
    if(scope==previous)return 0;
    scope->previous=previous;scope->actor=actor;scope->action=action;
    scope->target=0;scope->object=0;scope->row=0;scope->reference=0;
    scope->armed=0;scope->ready=0;scope->self=(uintptr_t)scope;
    scope->magic=SCOPE_MAGIC;*ACTIVE=scope;return 1;
}
void ffta_execution_close(FFTA_ExecutionScope *scope) {
    if(current()!=scope || !scope)return;
    *ACTIVE=scope->previous;
    scope->magic=0;scope->self=0;scope->previous=0;
    scope->actor=0;scope->target=0;scope->object=0;scope->row=0;
    scope->reference=0;scope->action=0;scope->armed=0;scope->ready=0;
}
void ffta_execution_arm(uint8_t *object,uint8_t *row,const uint8_t *context) {
    FFTA_ExecutionScope *scope=current();
    if(!scope)return;
    scope->armed=0;scope->ready=0;
    if(scope->action!=FFTA_SAM_A9 || !object || !row || !context ||
       half(context+12)!=FFTA_SAM_A9 || half(object+0x10)!=FFTA_SAM_A9 ||
       (context[0x26]&0x10) || *(const uint8_t *const *)context!=scope->actor)return;
    uintptr_t offset=(uintptr_t)row-(uintptr_t)object-0x20u;
    if(offset>=15u*0x2cu || offset%0x2cu)return;
    const uint8_t *wrapper=*(const uint8_t *const *)object;
    if(!wrapper || *(const uint8_t *const *)wrapper!=scope->actor)return;
    scope->target=*(const uint8_t *const *)(context+4);
    if(!scope->target)return;
    scope->object=object;scope->row=row;scope->armed=1;
}
void ffta_execution_capture(int reference,unsigned action,const uint8_t *actor,const uint8_t *target) {
    FFTA_ExecutionScope *scope=current();
    if(!scope || !scope->armed || action!=FFTA_SAM_A9 ||
       scope->actor!=actor || scope->target!=target)return;
    scope->reference=reference;scope->ready=1;
}
void ffta_execution_disarm(void) {
    FFTA_ExecutionScope *scope=current();if(scope)scope->armed=0;
}
unsigned ffta_execution_take(uint8_t *object,uint8_t *row,const uint8_t *target,int *reference) {
    FFTA_ExecutionScope *scope=current();
    if(!scope || scope->armed || !scope->ready || !reference ||
       scope->object!=object || scope->row!=row || scope->target!=target)return 0;
    *reference=scope->reference;scope->ready=0;return 1;
}
