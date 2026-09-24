#include <stdint.h>
#include "teaching-families.h"

/* Native equipment help builds at most three rows (C8D14). Original
 * multi-race jobs 5..22 merge consecutive entries into one row with cycling
 * badges; its row buffers and per-row UI state hold exactly three rows.
 * Expansion classes teach each lesson to every racial job in turn, so apply
 * the same merge to consecutive same-family entries teaching one lesson. */
static const uint8_t native_group[18]={2,1,3,3,2,1,2,1,1,1,1,1,1,1,1,1,1,2};

static const uint8_t *lesson_of(unsigned job,unsigned index) {
    typedef const uint8_t *(*Lesson)(unsigned,unsigned);
    const uint8_t *jobs=*(const uint8_t *const *)0x080c8de4u;
    return ((Lesson)0x080cd481u)(jobs[job*52u+4u],index);
}

static unsigned lesson_name(unsigned job,unsigned index) {
    const uint8_t *lesson=lesson_of(job,index);
    return lesson[0]|(unsigned)lesson[1]<<8;
}

static unsigned family_of(unsigned job) {
    return job>=FFTA_TEACHING_FAMILY_FIRST && job<FFTA_TEACHING_FAMILY_FIRST+sizeof ffta_teaching_family
        ?ffta_teaching_family[job-FFTA_TEACHING_FAMILY_FIRST]:0;
}

unsigned ffta_teaching_group_size(const uint8_t *set,unsigned index) {
    unsigned job=set[2u+index*2u],family,name,count=1;
    if(job>=5u && job<=22u)return native_group[job-5u];
    family=family_of(job);
    if(!family)return 1;
    name=lesson_name(job,set[3u+index*2u]);
    while(count<3u && index+count<set[0]) {
        unsigned other=set[2u+(index+count)*2u],seen;
        if(family_of(other)!=family || lesson_name(other,set[3u+(index+count)*2u])!=name)break;
        for(seen=0;seen<count && set[2u+(index+seen)*2u]!=other;seen++);
        if(seen<count)break;
        count++;
    }
    return count;
}

/* Consumers look up each row's AP by searching for its first job. When a job
 * learns two lessons from one item, also require the row's lesson name. */
unsigned ffta_teaching_row_match(const uint8_t *row,const uint8_t *entry) {
    return row[4]==entry[0] && lesson_name(entry[0],entry[1])==(row[0]|(unsigned)row[1]<<8);
}

/* Original items never mix lesson types, so equipment help shows one type
 * icon. The shop list uses the first lesson; use the first row elsewhere. */
const uint8_t *ffta_teaching_first_lesson(const uint8_t *rows,const uint8_t *set,const uint8_t *fallback) {
    unsigned i;
    if(!(rows[0]|rows[1]))return fallback;
    for(i=0;i<set[0];i++)
        if(ffta_teaching_row_match(rows+4,set+2u+i*2u))return lesson_of(set[2u+i*2u],set[3u+i*2u]);
    return fallback;
}
