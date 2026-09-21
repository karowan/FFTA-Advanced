#include "job-state.h"
#include "persistent.h"
extern unsigned ffta_job_original_save(unsigned,uint8_t *);
extern int ffta_job_original_migrate(uint8_t *);
extern int ffta_job_original_give(unsigned,unsigned);
extern void ffta_job_original_clear(uint8_t *,unsigned);
extern int ffta_job_original_swap(uint8_t *,unsigned,unsigned);
extern void ffta_copy_owners_reset(void);
static unsigned word(const uint8_t *p) {
    return p[0]|((unsigned)p[1]<<8)|((unsigned)p[2]<<16)|((unsigned)p[3]<<24);
}
_Static_assert(0x3ca8u+FFTA_JOB_FOOTER_BYTES<=0x4000u,"native fourth flash page");
unsigned ffta_job_save(unsigned slot,uint8_t *source) {
    if(slot!=2 || !source)return ffta_job_original_save(slot,source);
    /* Native flash transactions are synchronous. Its last sector is written
     * and verified from this same source; native CRC covers only3CA8 bytes.
     * Preserve the adjacent native staging region exactly on every return. */
    uint8_t tail[FFTA_JOB_FOOTER_BYTES],marker[4];
    for(unsigned i=0;i<FFTA_JOB_FOOTER_BYTES;i++)tail[i]=source[0x3ca8+i];
    for(unsigned i=0;i<4;i++)marker[i]=source[0x1f04+i];
    ffta_job_footer_encode(source+0x3ca8,*(const unsigned *)0x03000860u+1u);
    source[0x1f04]='J';source[0x1f05]='S';source[0x1f06]='T';source[0x1f07]='1';
    unsigned result=ffta_job_original_save(slot,source);
    for(unsigned i=0;i<FFTA_JOB_FOOTER_BYTES;i++)source[0x3ca8+i]=tail[i];
    for(unsigned i=0;i<4;i++)source[0x1f04+i]=marker[i];
    return result;
}
int ffta_job_load(uint8_t *state) {
    int result=ffta_job_original_migrate(state);
    if(result<0)return result;
    unsigned extended=state[0x1f04]=='J' && state[0x1f05]=='S' &&
                      state[0x1f06]=='T' && state[0x1f07]=='1';
    if(state[0x10]!=2 || !extended) { ffta_job_reset();return result; }
    uint8_t descriptor[24]={0},footer[FFTA_JOB_FOOTER_BYTES];
    unsigned found=((unsigned (*)(unsigned,uint8_t *))0x0813b061u)(2,descriptor);
    if(found!=4 || descriptor[0]!=4 || descriptor[1] || descriptor[5]>=16)return -3;
    ((void (*)(unsigned,unsigned,uint8_t *,unsigned))0x08141b15u)(descriptor[5],0xca8,footer,FFTA_JOB_FOOTER_BYTES);
    if(!ffta_job_footer_decode(footer,word(state+8)))return -3;
    return result;
}
int ffta_job_give(unsigned id,unsigned amount) {
    unsigned first=ffta_storage_format((uint8_t *)0x02000000u)==0;
    int result=ffta_job_original_give(id,amount);
    if(first && ffta_storage_format((uint8_t *)0x02000000u)==1)ffta_job_reset();
    return result;
}
int ffta_job_swap_persistent(uint8_t *state,unsigned a,unsigned b) {
    int result=ffta_job_original_swap(state,a,b);
    if(result && state==(uint8_t *)0x02000000u)ffta_job_swap(a,b);
    return result;
}
void ffta_job_clear(uint8_t *destination,unsigned size) {
    uintptr_t first=(uintptr_t)destination,last=first+size;
    if((first==0x020159d0u || first==0x0201f550u || first==0x0200f3c4u) &&
       (last==0x0203f400u || last==0x0203f000u))ffta_copy_owners_reset();
    if(last>=first && size>=264)for(unsigned i=0;i<36;i++) {
        uint8_t *unit=(uint8_t *)(i<24 ? 0x02000080u+i*264 : 0x02002fc4u+(i-24)*264);
        if(first<=(uintptr_t)unit && last>=(uintptr_t)unit+264) {
            ffta_job_forget_origin(i+1);
            uint8_t *record=ffta_job_state(unit);
            if(record)for(unsigned j=0;j<FFTA_JOB_RECORD_BYTES;j++)record[j]=0;
        }
    }
    ffta_job_original_clear(destination,size);
}
