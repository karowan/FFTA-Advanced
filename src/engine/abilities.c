#include "abilities.h"
#include "job-lessons.h"
#include "persistent.h"

extern uint8_t *ffta_party_ap_address(uint8_t *, uint8_t *, unsigned);
extern uint8_t *ffta_owned_extra_ap(uint8_t *,unsigned);

static const uint8_t *job_record(unsigned job) {
    const uint8_t *records=*(const uint8_t *const *)0x080c8598;
    return records+52*job;
}
static unsigned job_value(unsigned job, unsigned selector) {
    return ((unsigned (*)(unsigned,unsigned,unsigned))0x080c8571)(job,job,selector);
}
static int custom_list(unsigned job) {
    for (unsigned i=0;i<sizeof(ffta_job_lessons)/sizeof(ffta_job_lessons[0]);++i)
        if (ffta_job_lessons[i].id==job) return (int)i;
    return -1;
}
unsigned ffta_job_lesson_count(unsigned job) {
    if (job>125) return 0;
    int list=custom_list(job);
    if (list>=0) return ffta_job_lessons[list].count;
    unsigned first=job_value(job,0x25),last=job_value(job,0x26);
    return last>=first ? last-first+1 : 0;
}
unsigned ffta_job_lesson_at(unsigned job, unsigned position) {
    if (job>125) return 0;
    int list=custom_list(job);
    if (list>=0) return position<ffta_job_lessons[list].count ? ffta_job_lessons[list].indices[position] : 0;
    unsigned first=job_value(job,0x25),last=job_value(job,0x26);
    return last>=first && position<=last-first ? first+position : 0;
}

/* Native AP bytes remain inline, including their availability bit. Human
 * additions use the roster sidecar or an explicitly live copy owner's tail. */
uint8_t *ffta_ap_address(uint8_t *unit, unsigned index) {
    if (!unit) return 0;
    index=(uint8_t)index;
    if (index<142) return unit+0x40+index;
    if (unit[6]!=1 || ffta_storage_format((const uint8_t *)0x02000000)!=1) return 0;
    return ffta_owned_extra_ap(unit,index);
}
unsigned ffta_ability_available(uint8_t *unit, unsigned index) {
    uint8_t *ap=ffta_ap_address(unit,index);
    return ap && (*ap&0x80) ? 1 : 0;
}
unsigned ffta_ap_value(uint8_t *unit,unsigned index) {
    uint8_t *ap=ffta_ap_address(unit,index);
    return ap ? *ap : 0;
}
void ffta_ability_revoke(uint8_t *unit,unsigned index) {
    uint8_t *ap=ffta_ap_address(unit,index);
    if (ap) *ap&=0x7f;
}
void ffta_ability_grant(uint8_t *unit, unsigned index) {
    uint8_t *ap=ffta_ap_address(unit,index);
    if (ap) *ap|=0x80;
}
void ffta_ap_set_value(uint8_t *unit,unsigned index,unsigned value) {
    uint8_t *ap=ffta_ap_address(unit,index);
    if (ap) *ap=(uint8_t)value;
}
unsigned ffta_ap_write_and_equipment_check(uint8_t *unit,unsigned index,unsigned value) {
    ffta_ap_set_value(unit,index,value);
    return ((unsigned (*)(uint8_t *,unsigned))0x080cd1fdu)(unit,index);
}
static const uint8_t *ability_record(unsigned race,unsigned index) {
    const uint8_t *const *races=*(const uint8_t *const *const *)0x080257e8;
    return races[race]+8*index;
}
unsigned ffta_job_mastered(uint8_t *unit,unsigned job) {
    if (!unit || job>125) return 0;
    job=(uint8_t)job;
    unsigned count=ffta_job_lesson_count(job);
    for (unsigned i=0;i<count;++i) {
        unsigned index=ffta_job_lesson_at(job,i);
        const uint8_t *record=ability_record(unit[6],index);
        if (!record[6]) continue;
        uint8_t *ap=ffta_ap_address(unit,index);
        if (!ap || (*ap&0x7f)<record[7]) return 0;
    }
    return 1;
}
unsigned ffta_job_action_count(uint8_t *unit,unsigned job,unsigned include_equipped) {
    if (!unit || job>125 || unit[6]!=job_value(job,1)) return 0;
    unsigned result=0,count=ffta_job_lesson_count(job);
    for (unsigned i=0;i<count;++i) {
        unsigned index=ffta_job_lesson_at(job,i);
        const uint8_t *record=ability_record(unit[6],index);
        if (record[6]!=1 && record[6]!=4) continue;
        uint8_t *ap=ffta_ap_address(unit,index);
        if (ap && (((*ap&0x7f)>=record[7]) || (include_equipped && (*ap&0x80)))) ++result;
    }
    return result;
}
unsigned ffta_job_prerequisite_count(uint8_t *unit,unsigned job) {
    if (!unit || job>125 || unit[6]!=job_value(job,1)) return 0;
    unsigned result=0;
    for (unsigned i=0;i<ffta_job_lesson_count(job);++i) {
        unsigned index=ffta_job_lesson_at(job,i);
        const uint8_t *record=ability_record(unit[6],index);
        if (record[6]==1 && (ffta_ap_value(unit,index)&0x7f)>=record[7]) ++result;
    }
    return result;
}
/* Original unlock rules remain native. Only the ten approved jobs use this
 * predicate; visibility elsewhere must not turn a clan flag into per-unit AP. */
unsigned ffta_new_job_eligible(uint8_t *unit,unsigned job) {
    if (!unit || job<116 || job>125 || unit[6]!=job_record(job)[4]) return 0;
    const uint8_t *requirements=*(const uint8_t *const *)0x080c8b18;
    requirements+=4*job_record(job)[0x30];
    for (unsigned i=0;i<2;++i) {
        unsigned required_job=requirements[i*2],required_count=requirements[i*2+1];
        if (required_count && ffta_job_prerequisite_count(unit,required_job)<required_count) return 0;
    }
    return 1;
}

unsigned ffta_new_lesson_job(unsigned race,unsigned index) {
    static const uint8_t original_counts[6]={0,142,77,95,85,88};
    race=(uint8_t)race;index=(uint16_t)index;
    if (!race || race>5 || index<original_counts[race]) return 0;
    for (unsigned i=0;i<sizeof(ffta_job_lessons)/sizeof(ffta_job_lessons[0]);++i) {
        if (ffta_job_lessons[i].race!=race) continue;
        for (unsigned j=0;j<ffta_job_lessons[i].count;++j)
            if (ffta_job_lessons[i].indices[j]==index) return ffta_job_lessons[i].id;
    }
    return 0;
}
unsigned ffta_new_secondary_job(const uint8_t *unit) {
    unsigned command=unit[0x36];
    return command>=116 && command<=125 && job_record(command)[4]==unit[6] ? command : 0;
}

extern unsigned ffta_original_commands(uint8_t *,uint8_t *);
unsigned ffta_commands(uint8_t *unit,uint8_t *output) {
    unsigned count=ffta_original_commands(unit,output);
    /* All five native callers have a 256-byte output buffer. Retain native
     * ordering and special/Item rules, then append only this race's additions. */
    for (unsigned job=116;job<=125;++job) {
        if (unit[6]!=job_record(job)[4]) continue;
        unsigned known=ffta_new_job_eligible(unit,job);
        for (unsigned i=0;!known && i<ffta_job_lesson_count(job);++i) {
            unsigned index=ffta_job_lesson_at(job,i);
            const uint8_t *record=ability_record(unit[6],index);
            if ((record[6]==1 || record[6]==4) && ffta_ap_value(unit,index)) known=1;
        }
        if (!known) continue;
        unsigned found=0;
        for (unsigned i=0;i<count;++i) if (output[i]==job) found=1;
        if (!found && count<255) output[count++]=(uint8_t)job;
    }
    return count;
}

extern unsigned ffta_original_command_browse(unsigned);
unsigned ffta_command_browse(unsigned command) {
    command=(uint8_t)command;
    if (command!=2 && command!=8 && (command<116 || command>125))
        return ffta_original_command_browse(command);
    uint8_t *menu=*(uint8_t **)0x03002818u;
    uint8_t *preview=menu+0x1be4;
    preview[0x36]=(uint8_t)command;
    unsigned job=((unsigned (*)(uint8_t *))0x080c9079)(preview);
    preview[8]=(uint8_t)job;
    if (job!=2 && job!=16 && (job<116 || job>125))
        return command>=116 ? 0 : ffta_original_command_browse(command);
    uint8_t *unit=*(uint8_t **)(menu+0x1d0c);
    if (!unit || unit[6]!=job_record(job)[4]) return 0;
    /* This is the native command browsing/grey-row rule: any learned AP byte
     * in the job suffices. Battle action usability remains a separate check. */
    for (unsigned i=0;i<ffta_job_lesson_count(job);++i)
        if (ffta_ap_value(unit,ffta_job_lesson_at(job,i))) return 1;
    return 0;
}
