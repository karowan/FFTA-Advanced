#include <stdint.h>
#include "blade-wound.h"
extern unsigned ffta_physical_eligibility(const uint8_t *);
extern int ffta_physical_magnitude(const uint8_t *);
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }

/* Native law kind16 is the harmful-status group. Specific Poison/status laws
 * must not acquire a fabricated native status bit for Blade Wound.
 * The common native actor/KO and movement gates execute before this branch.
 * Frame24 holds signed HP damage, not an item ID; frame54 is the optional
 * committed native status-result mask. Positive MP damage does not enter24.
 */
unsigned ffta_higan_harmful_law(const uint32_t *frame) {
    const uint8_t *actor=(const uint8_t *)frame[5];
    uint8_t *target=(uint8_t *)frame[6];
    if(!actor || !target || !half(target+0x18) || (target[0xe8]&0x40) ||
       ((unsigned (*)(const uint8_t *))0x080cd50du)(target)==11)return 0;
    if(frame[21]) {
        /* Actual post-action callers provide the HP result after interception.
         * Reapplying a wound is an application even if its value is identical.
         * Future automatic custom cures need the original application event
         * carried through this result path, rather than the remaining record.
         */
        return (int16_t)frame[9]>0 &&
            ffta_wound_record_remaining(ffta_owned_wound(target));
    }
    uint8_t query[0x34];
    for(unsigned i=0;i<sizeof(query);++i)query[i]=0;
    *(const uint8_t **)query=actor;*(uint8_t **)(query+4)=target;
    *(uint8_t **)(query+8)=target;query[12]=355&255;query[13]=355>>8;
    query[0x26]=0x10;
    if(!ffta_physical_eligibility(query))return 0;
    volatile uint32_t *rng=(volatile uint32_t *)0x030034b0u;
    uint32_t saved=*rng;
    int damage=ffta_physical_magnitude(query);
    unsigned applies=damage>0 && (unsigned)damage<half(target+0x18);
    if(applies && ((unsigned (*)(const uint8_t *))0x0812e6a5u)(target)==13 &&
       ((unsigned (*)(const uint8_t *,const uint8_t *,unsigned,unsigned))0x0812e6e1u)(actor,target,355,13))applies=0;
    *rng=saved;
    return applies;
}
