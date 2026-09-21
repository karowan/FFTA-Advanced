#include <stdint.h>
#include "execution-scope.h"
#include "blade-wound.h"
#include "registry.h"
extern void ffta_physical_before_hit(const uint8_t *);
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
void ffta_wound_event(uint8_t *unit,unsigned event) {
    /* KO, Petrify, battle end, changed job and broad harmful-status remedies.
     * Start turn, Dispel and equipment edits must preserve a harmful wound. */
    if(event>=2 && event<=6)ffta_wound_record_clear(ffta_owned_wound(unit));
}
int ffta_samurai_magnitude(const uint8_t *context,uint8_t *object,uint8_t *row) {
    ffta_physical_before_hit(context);
    ffta_execution_arm(object,row,context);
    /* Preserve the complete native dispatcher: descriptor callback, native
     * factor and story protection. Capture introduces no second RNG sample. */
    int result=((int (*)(void))0x08131b21u)();
    ffta_execution_disarm();
    return result;
}
void ffta_higanbana_commit(uint8_t *target,unsigned before,uint8_t *object,uint8_t *row) {
    if(!target || !object || half(object+0x10)!=FFTA_SAM_A9)return;
    int reference=0;
    if(!ffta_execution_take(object,row,target,&reference))return;
    unsigned after=half(target+0x18);
    if(before<=after)return;
    uint8_t *record=ffta_owned_wound(target);
    if(!after) { ffta_wound_record_clear(record);return; }
    /* Shared custom harmful-status policy uses native Immunity support11.
     * KO/Petrify cannot acquire a wound; a failed application preserves an
     * existing wound. Inoculation will join this gate when implemented. */
    if((target[0xe8]&0x40) || ((unsigned (*)(const uint8_t *))0x080cd50du)(target)==11)return;
    ffta_wound_record_replace(record,reference);
}
