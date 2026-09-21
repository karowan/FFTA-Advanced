#ifndef FFTA_UNIT_QUERY_H
#define FFTA_UNIT_QUERY_H
#include <stdint.h>
#include "job-state.h"
/* Native forecasts allocate distinct actor/recipient copies even for self.
 * Only registered source identities in an explicit query can alias; bytewise
 * copies and actual execution still require the exact same unit pointer. */
static inline unsigned ffta_query_same_unit(const uint8_t *context,
                                          const uint8_t *actor,const uint8_t *target){
 if(!actor || !target)return 0;
 if(actor==target)return 1;
 if(!context || !(context[0x26]&16u))return 0;
 unsigned origin=ffta_job_origin(actor);
 return origin && origin==ffta_job_origin(target);
}
#endif
