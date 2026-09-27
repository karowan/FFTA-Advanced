#include "chemist-progression.h"
#include "job-state.h"

/* Declared valid bit widths of the existing schema-2 fields. Byte9 has no
 * producer or consumer. No arbitrary truncation: packing fails if a field
 * contains a bit outside its contract. 134 old bits + 40 new bits fit in the
 * existing 22-byte flash row, with two zero padding bits. RAM offsets stay
 * unchanged for every pre-existing field. */
static const uint8_t widths[27]={3,6,1,8,3,6,6,7,4,0,6,5,8,8,8,8,8,8,8,8,8,7,8,8,8,8,8};
unsigned ffta_cp_record_pack(uint8_t *out,const uint8_t *in) {
    for(unsigned i=0;i<27;i++)if((unsigned)in[i]>>widths[i])return 0;
    for(unsigned i=0;i<22;i++)out[i]=0;
    unsigned bit=0;
    for(unsigned i=0;i<27;i++)for(unsigned n=0;n<widths[i];n++,bit++)
        out[bit/8]|=(uint8_t)(((in[i]>>n)&1u)<<(bit%8));
    return bit==174;
}
unsigned ffta_cp_record_unpack(uint8_t *out,const uint8_t *in) {
    if(in[21]&192u)return 0;
    unsigned bit=0;
    for(unsigned i=0;i<27;i++) {
        out[i]=0;
        for(unsigned n=0;n<widths[i];n++,bit++)out[i]|=(uint8_t)(((in[bit/8]>>(bit%8))&1u)<<n);
    }
    return bit==174;
}
