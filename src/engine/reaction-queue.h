#ifndef FFTA_REACTION_QUEUE_H
#define FFTA_REACTION_QUEUE_H
#include <stdint.h>
/* Native A433C local frame, valid only inside its authenticated empty-queue
 * dispatch callback. The API owns no RAM and never retains this pointer. */
unsigned ffta_reaction_queue_append(unsigned *frame,const uint8_t *acting,
 const uint8_t *target,unsigned action,unsigned kind,unsigned payload);
unsigned ffta_reaction_queue_dispatch(unsigned *frame);
unsigned ffta_reaction_request_metadata(const unsigned *frame,const uint8_t *object,const uint8_t *original_wrapper);
#endif
