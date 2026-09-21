#include <stdint.h>
#include "abilities.h"

static const uint8_t *job_record(unsigned job) {
    return *(const uint8_t *const *)0x080c8598+52*job;
}
/* Follow the same job aliases as C8570's range selectors, with a finite guard
 * for malformed fallback cycles. Item remains the native race-zero bank. */
unsigned ffta_command_job(const uint8_t *unit,unsigned slot) {
    if (!unit || slot<1 || slot>3) return 0;
    if (slot==3 || unit[0x34+slot]==1) return 1;
    unsigned job=slot==1 ? unit[5] : unit[8];
    unsigned fallback=slot==1 ? unit[7] : unit[8];
    for (unsigned n=0;n<126;++n) {
        if (job>125) return 0;
        unsigned alias=job_record(job)[5];
        if (!alias) return job;
        unsigned next=alias==255 ? fallback : alias;
        if (next==job) return 0;
        job=next;
    }
    return 0;
}
unsigned ffta_command_custom_job(const uint8_t *unit,unsigned slot) {
    unsigned job=ffta_command_job(unit,slot);
    return (job==2 && unit[6]==1) || (job==16 && unit[6]==2) ? job : 0;
}
/* Zero means native iteration. A marked result carries the next actual
 * lesson ID; FFFF means end. No global iterator or artificial AP index. */
unsigned ffta_command_successor(const uint8_t *unit,unsigned slot,unsigned current) {
    unsigned job=ffta_command_custom_job(unit,slot);
    if (!job) return 0;
    for (unsigned i=0;i<ffta_job_lesson_count(job);++i) {
        unsigned lesson=ffta_job_lesson_at(job,i);
        if (lesson>current) return 0x10000u|lesson;
    }
    return 0x1ffffu;
}
static unsigned has_custom(const uint8_t *unit) {
    return ffta_command_custom_job(unit,1) || ffta_command_custom_job(unit,2);
}
typedef struct { const uint8_t *bank; unsigned job,first,count; } Range;
static Range range(uint8_t *unit,unsigned slot) {
    uint8_t first,last;
    Range r;
    r.bank=((const uint8_t *(*)(uint8_t *,unsigned,uint8_t *,uint8_t *))0x080cce61)(unit,slot,&first,&last);
    r.job=ffta_command_custom_job(unit,slot);r.first=first;
    r.count=r.job ? ffta_job_lesson_count(r.job) : last>=first ? (unsigned)last-first+1 : 0;
    return r;
}
static unsigned lesson_at(const Range *r,unsigned position) {
    return r->job ? ffta_job_lesson_at(r->job,position) : r->first+position;
}
static int is_action(const uint8_t *record) { return record[6]==1 || record[6]==4; }
static unsigned action_id(const uint8_t *record) { return *(const uint16_t *)(record+4); }
static unsigned action_value(unsigned action,unsigned selector) {
    return ((unsigned (*)(unsigned,unsigned))0x080ccd51)(action,selector);
}
static uint8_t *battle_unit(void) { return *(uint8_t **)(*(uint8_t **)0x0200f438+0x18); }
/* Builders receive a stack-owned native descriptor, not a slot number. Match
 * that descriptor against the current unit's own native slot resolution. */
unsigned ffta_descriptor_successor(const uint8_t *descriptor,unsigned current) {
    uint8_t *unit=battle_unit();
    for (unsigned slot=1;slot<=2;++slot) {
        if (unit[0x34+slot]!=descriptor[6] || !ffta_command_custom_job(unit,slot)) continue;
        uint8_t first,last;
        const uint8_t *bank=((const uint8_t *(*)(uint8_t *,unsigned,uint8_t *,uint8_t *))0x080cce61)(unit,slot,&first,&last);
        if (bank==*(const uint8_t *const *)descriptor && first==descriptor[4] && last==descriptor[5])
            return ffta_command_successor(unit,slot,current);
    }
    return 0;
}
extern unsigned ffta_original_battle_command(unsigned);
extern unsigned ffta_original_special_action(void);
extern unsigned ffta_original_action_command(uint8_t *,unsigned);
extern unsigned ffta_original_action21(uint8_t *);

unsigned ffta_battle_command(unsigned selection) {
    selection=(uint8_t)selection;
    if (selection!=6 && selection!=7) return ffta_original_battle_command(selection);
    uint8_t *unit=battle_unit();unsigned slot=selection-5;
    if (!ffta_command_custom_job(unit,slot)) return ffta_original_battle_command(selection);
    void *manager=((void *(*)(void))0x08096d7d)();
    unsigned restricted=((unsigned (*)(void *,uint8_t *))0x080970e9)(manager,unit);
    Range r=range(unit,slot);
    for (unsigned i=0;i<r.count;++i) {
        unsigned lesson=lesson_at(&r,i);const uint8_t *record=r.bank+8*lesson;
        if (is_action(record) && ffta_ability_available(unit,lesson) &&
            (!restricted || action_value(action_id(record),0x15))) return 1;
    }
    return 0;
}
unsigned ffta_special_action(void) {
    uint8_t *unit=battle_unit();
    if (!has_custom(unit)) return ffta_original_special_action();
    for (unsigned slot=1;slot<=3;++slot) {
        if (!unit[0x34+slot]) continue;
        Range r=range(unit,slot);
        for (unsigned i=0;i<r.count;++i) {
            unsigned lesson=lesson_at(&r,i);const uint8_t *record=r.bank+8*lesson;
            if (is_action(record) && ffta_ability_available(unit,lesson) && action_value(action_id(record),0x13)) return 1;
        }
    }
    return 0;
}
unsigned ffta_action_command(uint8_t *unit,unsigned action) {
    action=(uint16_t)action;
    if (!has_custom(unit)) return ffta_original_action_command(unit,action);
    for (unsigned slot=1;slot<=3;++slot) {
        unsigned command=unit[0x34+slot];
        if (!command) continue;
        Range r=range(unit,slot);
        for (unsigned i=0;i<r.count;++i) {
            const uint8_t *record=r.bank+8*lesson_at(&r,i);
            if (is_action(record) && action_id(record)==action) return command;
        }
    }
    return 0;
}
unsigned ffta_action21(uint8_t *unit) {
    if (!has_custom(unit)) return ffta_original_action21(unit);
    if (((unsigned (*)(uint8_t *))0x080c8299)(unit)) return 0;
    for (unsigned slot=1;slot<=3;++slot) {
        unsigned command=unit[0x34+slot];
        if (!command || command==1) continue;
        Range r=range(unit,slot);
        for (unsigned i=0;i<r.count;++i) {
            unsigned lesson=lesson_at(&r,i);const uint8_t *record=r.bank+8*lesson;
            if (is_action(record) && ffta_ability_available(unit,lesson) && action_id(record)==0x21) return 1;
        }
    }
    return 0;
}
