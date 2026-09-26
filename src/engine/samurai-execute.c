#include <stdint.h>
#include "registry.h"
#include "samurai-state.h"
#include "execution-scope.h"
#include "action-snapshot.h"

/* Native executor A433C entry (every executed action). Its action snapshot
 * used to be an 820-byte local held on the IWRAM stack for the whole action,
 * under every nested result, reaction and Doublecast chain; the deepest chain
 * (Doublecast into a Shell target) came within 56 bytes of resident IWRAM
 * code. The snapshot now lives in a lent root result-bank frame; the stack
 * frame remains only as a fallback when no bank frame is free, and only with
 * stack room for the deepest measured chain; otherwise the action runs
 * without a snapshot (as bank-less forecasts already do). */
extern unsigned ffta_original_samurai_execute(uint8_t *,uint8_t *,unsigned,unsigned,
    unsigned,unsigned,unsigned,unsigned);
extern void ffta_samurai_completed_results(uint8_t *,unsigned,unsigned,const uint8_t *);

static __attribute__((noinline)) unsigned run(FFTA_ActionSnapshot *snapshot,uint8_t *output,uint8_t *wrapper,
    unsigned x,unsigned y,unsigned action,unsigned item,unsigned mode,unsigned last) {
    uint8_t *actor=wrapper?*(uint8_t **)wrapper:0;
    unsigned nested=ffta_centered_factor(actor,FFTA_SAM_A3)==5 && !ffta_centered_active(actor);
    FFTA_ExecutionScope scope;
    unsigned opened=ffta_execution_open(&scope,actor,action);
    unsigned snapshotted=ffta_snapshot_begin(snapshot,actor,0,1);
    if(snapshotted)ffta_action_started(actor,action,FFTA_ACTION_NATIVE_PRIMARY,FFTA_ACTION_UNCLASSIFIED);
    unsigned result=ffta_original_samurai_execute(output,wrapper,x,y,action,item,mode,last);
    ffta_samurai_completed_results(actor,action,1,output);
    if(snapshotted)ffta_action_completed(actor);
    if(!nested)ffta_centered_retire(actor);
    if(opened)ffta_execution_close(&scope);
    if(snapshotted)ffta_snapshot_end(snapshot);
    return result;
}
static __attribute__((noinline)) unsigned on_stack(uint8_t *output,uint8_t *wrapper,unsigned x,unsigned y,
    unsigned action,unsigned item,unsigned mode,unsigned last) {
    FFTA_ActionSnapshot snapshot;
    return run(&snapshot,output,wrapper,x,y,action,item,mode,last);
}
unsigned ffta_samurai_execute(uint8_t *output,uint8_t *wrapper,unsigned x,unsigned y,
    unsigned action,unsigned item,unsigned mode,unsigned last) {
    uintptr_t token;
    FFTA_ActionSnapshot *lent=ffta_snapshot_lend(&token);
    if(!lent)return ffta_stack_room(sizeof(FFTA_ActionSnapshot)+FFTA_EXECUTE_STACK_RESERVE)?
        on_stack(output,wrapper,x,y,action,item,mode,last):run(0,output,wrapper,x,y,action,item,mode,last);
    unsigned result=run(lent,output,wrapper,x,y,action,item,mode,last);
    ffta_snapshot_return(&token);
    return result;
}
