#include "job-state.h"
#include "persistent.h"

/* This bank requires the job-state builder's explicit1KiB heap reservation.
 * It does not overlap the inventory view at3F800 or owner roots at3FF30. */
#define LIVE ((uint8_t *)0x02000000u)
#define BANK ((JobBank *)0x0203f400u)
#define BANK_MAGIC 0x32534a46u
#define PAYLOAD (FFTA_JOB_UNIT_COUNT*FFTA_JOB_RECORD_BYTES)
#define FOOTER FFTA_JOB_FOOTER_BYTES
typedef struct { uint32_t magic; uint8_t reserved[12];
    uint8_t units[FFTA_JOB_UNIT_COUNT][FFTA_JOB_RECORD_BYTES]; } JobBank;
_Static_assert(sizeof(JobBank)==FFTA_JOB_BANK_BYTES,"reserved job-state bank");
/* Fixed high EWRAM: the AI choice root (ai-choice.c) starts at 0x0203F728. */
_Static_assert(0x0203f400u+FFTA_JOB_BANK_BYTES<=0x0203f728u,"job-state bank below the AI choice root");
extern uint8_t *ffta_copied_job_state(uint8_t *) __attribute__((weak));
extern unsigned ffta_copied_job_origin(const uint8_t *) __attribute__((weak));
extern uint8_t *ffta_copied_job_potion(uint8_t *) __attribute__((weak));
extern void ffta_copied_job_reindex(unsigned,unsigned) __attribute__((weak));
extern unsigned ffta_copied_job_peers(uint8_t *,uint8_t **,unsigned) __attribute__((weak));
static unsigned word(const uint8_t *p) {
    return p[0]|((unsigned)p[1]<<8)|((unsigned)p[2]<<16)|((unsigned)p[3]<<24);
}
static void put_word(uint8_t *p,unsigned x) {
    for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(x>>(8*i));
}
static unsigned canonical(const uint8_t *unit) {
    uintptr_t address=(uintptr_t)unit,delta=address-0x02000080u;
    if(delta<24u*264u && delta%264u==0)return 1+delta/264u;
    delta=address-0x02002fc4u;
    return delta<12u*264u && delta%264u==0 ? 25+delta/264u : 0;
}
void ffta_job_reset(void) {
    for(unsigned i=0;i<12;i++)BANK->reserved[i]=0;
    for(unsigned n=0;n<36;n++)for(unsigned i=0;i<FFTA_JOB_RECORD_BYTES;i++)BANK->units[n][i]=0;
    BANK->magic=BANK_MAGIC;
}
void ffta_job_record_reindex(uint8_t *record,unsigned a,unsigned b) {
    if(!record || !a || a>36 || b>36 || a==b)return;
    /* Only these two assigned bytes contain canonical source tokens. */
    if(record[1]==a) { record[1]=(uint8_t)b;if(!b)record[2]=0; }
    else if(b && record[1]==b)record[1]=(uint8_t)a;
    if(record[5]==a)record[5]=(uint8_t)b;
    else if(b && record[5]==b)record[5]=(uint8_t)a;
}
static void reindex(unsigned a,unsigned b) {
    for(unsigned i=0;i<36;i++)ffta_job_record_reindex(BANK->units[i],a,b);
    if(ffta_copied_job_reindex)ffta_copied_job_reindex(a,b);
}
void ffta_job_swap(unsigned a,unsigned b) {
    if(a>=24 || b>=24 || a==b || BANK->magic!=BANK_MAGIC || ffta_storage_format(LIVE)!=1)return;
    for(unsigned i=0;i<FFTA_JOB_RECORD_BYTES;i++) {
        uint8_t value=BANK->units[a][i];BANK->units[a][i]=BANK->units[b][i];BANK->units[b][i]=value;
    }
    reindex(a+1,b+1);
}
void ffta_job_forget_origin(unsigned token) {
    if(!token || token>36 || BANK->magic!=BANK_MAGIC || ffta_storage_format(LIVE)!=1)return;
    reindex(token,0);
}
uint8_t *ffta_job_state(uint8_t *unit) {
    if(!unit || BANK->magic!=BANK_MAGIC || ffta_storage_format(LIVE)!=1)return 0;
    unsigned token=canonical(unit);
    if(token)return BANK->units[token-1];
    return ffta_copied_job_state ? ffta_copied_job_state(unit) : 0;
}
unsigned ffta_job_origin(const uint8_t *unit) {
    if(!unit)return 0;
    unsigned token=canonical(unit);
    return token ? token : ffta_copied_job_origin ? ffta_copied_job_origin(unit) : 0;
}
unsigned ffta_job_peers(uint8_t *unit,uint8_t **output,unsigned capacity) {
    if(!output || !ffta_job_state(unit))return 0;
    if(canonical(unit)) {
        if(capacity<36)return 0;
        for(unsigned i=0;i<36;i++)output[i]=LIVE+(i<24 ? 0x80u+i*264u : 0x2fc4u+(i-24)*264u);
        return 36;
    }
    return ffta_copied_job_peers ? ffta_copied_job_peers(unit,output,capacity) : 0;
}
uint8_t *ffta_job_peer(uint8_t *unit,unsigned origin) {
    if(!origin || origin>36)return 0;
    uint8_t *peers[36],*found=0;unsigned count=ffta_job_peers(unit,peers,36);
    for(unsigned i=0;i<count;i++)if(ffta_job_origin(peers[i])==origin) {
        if(found)return 0;
        found=peers[i];
    }
    return found;
}
uint8_t *ffta_job_potion(uint8_t *unit) {
    unsigned token=canonical(unit);
    if(token && token<=24)return LIVE+0x1e80+token-1;
    return ffta_copied_job_potion ? ffta_copied_job_potion(unit) : 0;
}
/* Native CRC32 has the same explicit initial-seed contract as the save code. */
static unsigned crc(const uint8_t *p,unsigned size) {
    return ((unsigned (*)(const uint8_t *,unsigned,unsigned))0x0813adf1u)(p,size,0);
}
void ffta_job_footer_encode(uint8_t *output,unsigned generation) {
    static const uint8_t magic[8]={'F','F','T','A','J','S','0','2'};
    for(unsigned i=0;i<FOOTER;i++)output[i]=0;
    for(unsigned i=0;i<8;i++)output[i]=magic[i];
    output[8]=2;output[9]=FFTA_JOB_RECORD_BYTES;output[10]=FFTA_JOB_UNIT_COUNT;
    put_word(output+12,generation);put_word(output+20,PAYLOAD);
    if(BANK->magic==BANK_MAGIC)
        for(unsigned n=0;n<FFTA_JOB_UNIT_COUNT;n++)for(unsigned i=0;i<FFTA_JOB_RECORD_BYTES;i++)
            output[32+n*FFTA_JOB_RECORD_BYTES+i]=BANK->units[n][i];
    put_word(output+16,crc(output,FOOTER));
}
/* Validate the complete old/new envelope before publishing. Legacy reserved
 * bytes3/15 never represented effects; clear them before assigning new jobs. */
unsigned ffta_job_footer_decode(uint8_t *input,unsigned generation) {
    static const uint8_t prefix[7]={'F','F','T','A','J','S','0'};
    for(unsigned i=0;i<7;i++)if(input[i]!=prefix[i])return 0;
    unsigned legacy=input[7]=='1',width=legacy?16u:FFTA_JOB_RECORD_BYTES;
    if((!legacy && input[7]!='2') || input[8]!=(legacy?1u:2u) ||
       input[9]!=width || input[10]!=FFTA_JOB_UNIT_COUNT || input[11] ||
       word(input+12)!=generation || word(input+20)!=width*FFTA_JOB_UNIT_COUNT)return 0;
    for(unsigned i=24;i<32;i++)if(input[i])return 0;
    unsigned expected=word(input+16);put_word(input+16,0);
    unsigned actual=crc(input,32u+width*FFTA_JOB_UNIT_COUNT);put_word(input+16,expected);
    if(actual!=expected)return 0;
    ffta_job_reset();
    for(unsigned n=0;n<FFTA_JOB_UNIT_COUNT;n++)for(unsigned i=0;i<width;i++)
        if(!legacy || (i!=3 && i!=15))BANK->units[n][i]=input[32+n*width+i];
    return 1;
}
