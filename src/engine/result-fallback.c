#include "action-snapshot.h"
/* Installed replacement for action-snapshot.c's stack_result (memory-fixes
 * stage; same body as the source there). Reached only when fresh_result finds
 * no free bank frame; the old path always added an 880-byte stack frame,
 * which on deep chains overran resident IWRAM code by up to ~150 bytes. */
extern unsigned run_result(uint8_t *,uint8_t *,uint8_t *,unsigned,unsigned,void *,unsigned,unsigned,
    unsigned,const unsigned *);
static __attribute__((noinline)) unsigned on_stack(uint8_t *object,uint8_t *wrapper,uint8_t *manager,unsigned flags_value,
    unsigned mode,void *scratch,unsigned secondary,unsigned last,unsigned caller,const unsigned *native_frame) {
    uint8_t *actor=object && *(uint8_t **)object?**(uint8_t ***)object:0;
    FFTA_ActionSnapshot snapshot;
    unsigned opened=ffta_snapshot_begin(&snapshot,actor,0,1);
    unsigned result=run_result(object,wrapper,manager,flags_value,mode,scratch,secondary,last,caller,native_frame);
    if(opened)ffta_snapshot_end(&snapshot);
    return result;
}
unsigned ffta_result_fallback(uint8_t *object,uint8_t *wrapper,uint8_t *manager,unsigned flags_value,
    unsigned mode,void *scratch,unsigned secondary,unsigned last,unsigned caller,const unsigned *native_frame) {
    if(ffta_stack_room(sizeof(FFTA_ActionSnapshot)+FFTA_RESULT_STACK_RESERVE))
        return on_stack(object,wrapper,manager,flags_value,mode,scratch,secondary,last,caller,native_frame);
    return run_result(object,wrapper,manager,flags_value,mode,scratch,secondary,last,caller,native_frame);
}
