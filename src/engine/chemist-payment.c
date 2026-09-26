#include "native-unit.h"
#include "chemist-items.h"
#include "registry.h"
#include "job-state.h"
/* Payment boundary of the native executor (A45C6). A zero result takes the
 * native "cannot pay" branch at A4968, which never completes the turn: the
 * battle stops with no menu. Targeting accepts any unit or tile in range
 * (e.g. Potion on an adjacent enemy), so a Chemist action must never refuse
 * here. The recipe is paid only for a recipient in the actor's own party;
 * otherwise nothing is consumed and the action continues, and per-recipient
 * eligibility (ffta_chemist_eligibility: party side only) leaves every other
 * unit unaffected. */
extern unsigned ffta_previous_paid(uint8_t *,unsigned);
static unsigned party_recipient(uint8_t *actor,unsigned action,unsigned selected,const unsigned *frame) {
    unsigned origin=ffta_job_origin(actor);
    if(!origin || origin>24)return 0;
    if(action==FFTA_CHM_A5)return 1;
    /* Native A433C saved selected coordinates, not a preview pointer.
     * Resolve only this actor's exact owner cohort after movement. */
    if(!frame)return 0;
    uint8_t *peers[36],*target=0;
    unsigned count=ffta_job_peers(actor,peers,36);
    for(unsigned i=0;i<count;i++)if(peers[i][0xf6]==frame[0x44/4] && peers[i][0xf7]==frame[0x48/4]) {
        if(target)return 0; /* ambiguous occupied tile is not authority */
        target=peers[i];
    }
    if(!target || (((actor[0x29]>>7)^((actor[0xeb]>>5)&1u))!=(target[0x29]>>7)))return 0;
    /* Revival eligibility reads native context flags as well. Give
     * every single-target recipe a complete zeroed context instead
     * of borrowing stale preview memory at the payment boundary. */
    unsigned context[13];
    for(unsigned i=0;i<13;i++)context[i]=0;
    context[0]=(uintptr_t)actor;
    context[1]=context[2]=(uintptr_t)target;context[3]=action|(selected<<16);
    return ffta_chemist_eligibility((const uint8_t *)context);
}
unsigned ffta_chemist_payment_gate(uint8_t *actor,unsigned action,unsigned selected,const unsigned *frame) {
    if(!ffta_chemist_action(action))return ffta_previous_paid(actor,action);
    if(party_recipient(actor,action,selected,frame))ffta_chemist_pay(action,selected);
    return 1;
}
