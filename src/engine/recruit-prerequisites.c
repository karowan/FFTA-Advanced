#include <stdint.h>

extern unsigned ffta_job_prerequisite_count(uint8_t *,unsigned);

/* Recruitment has its own reconciliation loop, separate from Change Job.
 * Only expanded lesson lists need replacing; retain the original loop for
 * every other job, including native special/monster records. */
int ffta_recruit_prerequisite_count(uint8_t *unit,unsigned job) {
    if(job!=2 && job!=16 && (job<116 || job>125)) return -1;
    return (int)ffta_job_prerequisite_count(unit,job);
}
