#include "action-snapshot.h"
/* Lend a root result-bank frame to a caller that would otherwise hold an
 * 820-byte FFTA_ActionSnapshot on the IWRAM stack. Same ownership rules as
 * action-snapshot.c's fresh results and the Mystic Shell forecast: a slot is
 * free when no token holds it and its frame is neither initialized nor on
 * the live snapshot chain; the borrower's stack token authenticates the frame
 * (stack_frame requires the token address above SP and holding the frame). */
#define MAGIC 0x31534e41u
#define ACTIVE ((FFTA_ActionSnapshot *volatile *)0x0203ff48u)
typedef struct { uintptr_t *token; FFTA_ActionSnapshot frame; } ResultStorage;
_Static_assert(sizeof(ResultStorage)==824,"external result snapshot ABI");
extern ResultStorage *ffta_additional_result_storage(void);
extern unsigned ffta_additional_workspace_prepare(void);

static unsigned readable(const FFTA_ActionSnapshot *s) {
    uintptr_t p=(uintptr_t)s;
    return !(p&3u) && ((p>=0x02000000u && p<=0x02040000u-sizeof(*s)) ||
                       (p>=0x03000000u && p<=0x03008000u-sizeof(*s)));
}
static unsigned on_chain(const FFTA_ActionSnapshot *frame) {
    const FFTA_ActionSnapshot *s=*ACTIVE;
    for(unsigned i=0;i<16 && readable(s) && s->magic==MAGIC && s->self==(uintptr_t)s;i++,s=s->previous)
        if(s==frame)return 1;
    return 0;
}
FFTA_ActionSnapshot *ffta_snapshot_lend(uintptr_t *token) {
    if(!token)return 0;
    *token=0;
    ffta_additional_workspace_prepare();
    ResultStorage *bank=ffta_additional_result_storage();
    if(!bank)return 0;
    for(unsigned i=0;i<8;i++)
        if(!bank[i].token && !bank[i].frame.magic && !on_chain(&bank[i].frame)) {
            *token=(uintptr_t)&bank[i].frame;bank[i].token=token;
            return &bank[i].frame;
        }
    return 0;
}
void ffta_snapshot_return(uintptr_t *token) {
    ResultStorage *bank=token && *token?ffta_additional_result_storage():0;
    if(bank)for(unsigned i=0;i<8;i++)if(bank[i].token==token)bank[i].token=0;
    if(token)*token=0;
}
