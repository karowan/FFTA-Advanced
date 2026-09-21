#include <stdint.h>
#include "abilities.h"
#include "persistent.h"
extern unsigned ffta_ap_value(uint8_t *,unsigned);

/* Expansion-format reserved bytes, following Quin history at 1E79 and before
 * per-unit preferences at 1E80. Existing saves have zero here. No layout or
 * version change: the native save already transports this entire block. */
static unsigned discovered(unsigned job) {
    uint8_t *state=(uint8_t *)0x02000000;
    unsigned bit=1u<<(job-116),known=0;
    int persistent=ffta_storage_format(state)==1;
    if (persistent) known=state[0x1e7a]|((unsigned)state[0x1e7b]<<8);
    if (known&bit) return 1;
    for (unsigned slot=0;slot<24;++slot) {
        uint8_t *member=state+0x80+264*slot;
        static const uint8_t races[10]={1,1,2,2,3,3,5,5,4,4};
        if (!member[4] || member[6]!=races[job-116]) continue;
        unsigned found=member[7]==job || ffta_new_job_eligible(member,job);
        /* Recover prior use from old saves without mistaking an equipment
         * availability bit for earned AP. Current-job recruits count too. */
        for (unsigned n=0;!found && n<ffta_job_lesson_count(job);++n)
            found=(ffta_ap_value(member,ffta_job_lesson_at(job,n))&127)!=0;
        if (!found) continue;
        if (persistent) {
            known|=bit;
            state[0x1e7a]=(uint8_t)known;
            state[0x1e7b]=(uint8_t)(known>>8);
        }
        return 1;
    }
    return 0;
}

/* These helpers only write the native twelve-byte wheel array. Expanded
 * candidates stay on this invocation's stack; no global job-list ABI changes. */
static unsigned candidates(uint8_t *unit,uint8_t *list) {
    unsigned count=((unsigned (*)(uint8_t *,uint8_t *))0x080c8a25)(unit,list);
    if (!count || count>12 || unit[6]<1 || unit[6]>5) return count;
    static const uint8_t races[10]={1,1,2,2,3,3,5,5,4,4};
    for (unsigned n=0;n<10;++n) if (races[n]==unit[6]) {
        unsigned job=116+n;
        unsigned eligible=ffta_new_job_eligible(unit,job);
        if (!discovered(job) && !eligible) continue;
        list[count++]=(uint8_t)(job|(eligible?128:0));
    }
    /* The native wheel sorts each visible page by low-seven-bit job ID.
     * Sort before slicing too, so its first entry remains a stable page key. */
    for (unsigned i=1;i<count;++i) {
        uint8_t value=list[i];unsigned j=i;
        while (j && (list[j-1]&127)>(value&127)) { list[j]=list[j-1];--j; }
        list[j]=value;
    }
    return count;
}
static unsigned page_size(unsigned count) { return count>12 ? (count+1)/2 : count; }
static unsigned write_page(uint8_t *out,const uint8_t *list,unsigned count,unsigned start) {
    unsigned size=page_size(count),n=count-start;
    if (n>size) n=size;
    for (unsigned i=0;i<12;++i) out[i]=i<n ? list[start+i] : 0;
    return n;
}
unsigned ffta_wheel_initial(uint8_t *unit,uint8_t *out) {
    uint8_t list[16]={0};
    unsigned count=candidates(unit,list),start=0;
    if (count>14) return 0;
    if (count>12) for (unsigned i=0;i<count;++i)
        if ((list[i]&127)==unit[7]) { start=i<page_size(count)?0:page_size(count);break; }
    return write_page(out,list,count,start);
}
/* Called only in native wheel state4 after its animation timer reaches0.
 * The displayed first ID identifies its page; there is no persistent paging
 * state to leak between units, menu allocations, or saved games. */
unsigned ffta_wheel_turn(void) {
    uint8_t *menu=*(uint8_t **)0x03002818;
    unsigned keys=*(volatile uint16_t *)0x03000002;
    if (!(keys&0x300) || (keys&3) || menu[0x25]) return 0;
    uint8_t *unit=*(uint8_t **)(menu+0x1d0c),list[16]={0};
    unsigned count=candidates(unit,list);
    if (count<=12 || count>14) return 0;
    unsigned size=page_size(count);
    unsigned start=(menu[0x1278]&127)==(list[0]&127) ? size : 0;
    unsigned old_count=*(uint32_t *)(menu+0x1270);
    if (old_count>12) return 0;
    void *sprites=*(void **)0x03000e34;
    for (unsigned i=0;i<old_count;++i)
        ((void (*)(void *,unsigned))0x0804c7a1)(sprites,i);
    ((void (*)(void *,unsigned))0x0804c7a1)(sprites,0x1a);
    ((void (*)(unsigned))0x08141541)(0x65);
    return write_page(menu+0x1278,list,count,start);
}
unsigned ffta_wheel_can_confirm(void) {
    uint8_t *menu=*(uint8_t **)0x03002818;
    unsigned index=menu[0x1275],count=*(uint32_t *)(menu+0x1270);
    if (index>=count || count>12) return 0;
    unsigned job=menu[0x1287+28*index];
    if (job<116 || job>125) return 1;
    return ffta_new_job_eligible(*(uint8_t **)(menu+0x1d0c),job);
}
static unsigned donor(unsigned job) {
    /* Approved frontal Dancer badge shares the native plum colors of job30. */
    static const uint8_t donors[10]={6,3,13,15,25,27,41,36,30,30};
    job=(uint8_t)job;
    return job>=116 && job<=125 ? donors[job-116] : job;
}
extern void ffta_original_job_icon(void *,unsigned);
extern unsigned ffta_original_job_palette(unsigned);
void ffta_job_icon(void *dest,unsigned job) { ffta_original_job_icon(dest,donor(job)); }
unsigned ffta_job_palette(unsigned job) { return ffta_original_job_palette(donor(job)); }

/* Staging guard only: these reactions have no implementation yet. Keep them
 * out of the original 16-row compatibility bank until their real rules land. */
extern unsigned ffta_original_reaction_available(uint8_t *);
unsigned ffta_reaction_staging_guard(uint8_t *unit) {
    unsigned reaction=((unsigned (*)(uint8_t *))0x080cd4d5)(unit);
    return reaction>=128 ? 0 : ffta_original_reaction_available(unit);
}
