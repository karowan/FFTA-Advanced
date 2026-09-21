#ifndef FFTA_DARK_KNIGHT_STATE_H
#define FFTA_DARK_KNIGHT_STATE_H
#include <stdint.h>
#include "job-state.h"
#define FFTA_DRK_LAST_RESORT (1u<<22)
#define FFTA_DRK_TBN (1u<<23)
#define FFTA_DRK_TBN_CONSUMING (1u<<24)
#define FFTA_DRK_DARK_WARD_QUEUED 512u
#define FFTA_DRK_VENGEANCE_QUEUED 1024u
unsigned ffta_drk_last_resort(const uint8_t *);
unsigned ffta_drk_tbn(const uint8_t *);
unsigned ffta_drk_beneficial(const uint8_t *);
void ffta_drk_grant_last_resort(uint8_t *,unsigned);
unsigned ffta_drk_grant_tbn(uint8_t *,const uint8_t *);
void ffta_drk_lifecycle_event(uint8_t *,unsigned);
void ffta_drk_lifecycle_turn_end(uint8_t *);
uint8_t *ffta_drk_last_resort_apply(uint8_t *);
uint8_t *ffta_drk_tbn_apply(uint8_t *);
#endif
