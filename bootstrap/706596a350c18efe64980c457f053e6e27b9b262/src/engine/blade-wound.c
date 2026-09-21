#include "blade-wound.h"
#include "battle-state.h"

/* Byte accesses also support the unaligned evaluated-unit tail. Bits 0..13
 * hold floor(P/2), bits 14..15 hold the remaining two/one pulses. Zero is
 * inactive. Count 3 is invalid and must never generate damage. This module
 * owns only the record; native HP application and owner-copy hooks are separate.
 */
static unsigned read_record(const uint8_t *record) {
    return record ? record[0]|((unsigned)record[1]<<8) : 0;
}
static void write_record(uint8_t *record,unsigned value) {
    if(record) { record[0]=(uint8_t)value;record[1]=(uint8_t)(value>>8); }
}
uint8_t *ffta_state_wound(uint8_t *state,const uint8_t *unit) {
    /* Reuse the exact canonical/staging ownership and format check. */
    uint8_t *packed=ffta_state_exposed(state,unit);
    return packed ? state+FFTA_WOUND_OFFSET+FFTA_WOUND_BYTES*
        (unsigned)(packed-state-FFTA_EXPOSED_OFFSET) : 0;
}
unsigned ffta_wound_record_remaining(const uint8_t *record) {
    unsigned count=read_record(record)>>14;
    return count<3 ? count : 0;
}
void ffta_wound_record_clear(uint8_t *record) { write_record(record,0); }
unsigned ffta_wound_record_replace(uint8_t *record,int reference) {
    /* Reject unrepresentable input instead of truncating or silently capping.
     * The native noncritical reference bound must be checked at integration.
     * No immediate pulse: a refresh replaces both outstanding old pulses. */
    if(!record || reference<=0 || reference>32767)return 0;
    write_record(record,0x8000u+(unsigned)reference/2u);
    return 1;
}
unsigned ffta_wound_record_tick(uint8_t *record) {
    unsigned value=read_record(record),count=value>>14;
    if(count!=1 && count!=2) { write_record(record,0);return 0; }
    unsigned pulse=value&0x3fffu;
    write_record(record,count==2 ? 0x4000u+ pulse : 0);
    return pulse;
}
void ffta_state_wound_swap(uint8_t *state,unsigned a,unsigned b) {
    if(!state || a>=24 || b>=24)return;
    uint8_t *left=ffta_state_wound(state,state+0x80u+a*264u);
    uint8_t *right=ffta_state_wound(state,state+0x80u+b*264u);
    if(!left || !right)return;
    unsigned value=read_record(left);
    write_record(left,read_record(right));write_record(right,value);
}
void ffta_state_wound_clear(uint8_t *state,const uint8_t *unit) {
    ffta_wound_record_clear(ffta_state_wound(state,unit));
}
