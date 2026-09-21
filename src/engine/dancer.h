#ifndef FFTA_DANCER_H
#define FFTA_DANCER_H
#include <stdint.h>
#define FFTA_DNC_POLKA (1u<<8)
#define FFTA_DNC_FROLIC (1u<<9)
#define FFTA_DNC_FURY_READY (1u<<10)
#define FFTA_DNC_RHYTHM_READY (1u<<11)
#define FFTA_DNC_CHARGED (1u<<12)
#define FFTA_DNC_ADMITTED (1u<<29)
#define FFTA_DNC_QUEUED (1u<<30)
#define FFTA_DNC_FURY_ACTION 441u
#define FFTA_DNC_RHYTHM_ACTION 442u
#define FFTA_DNC_FURY_KIND 143u
#define FFTA_DNC_RHYTHM_KIND 144u
unsigned ffta_dancer_virtual(unsigned);
unsigned ffta_dancer_physical(unsigned);
unsigned ffta_dancer_eligibility(const uint8_t *);
int ffta_dancer_magnitude(const uint8_t *);
int ffta_dancer_witch_hunt(const uint8_t *);
int ffta_dancer_attack(const uint8_t *,unsigned,unsigned,int);
unsigned ffta_dancer_power(const uint8_t *,unsigned,unsigned,unsigned);
unsigned ffta_dancer_flags(const uint8_t *);
unsigned ffta_dancer_debuff(const uint8_t *,unsigned);
unsigned ffta_dancer_ai_redundant(const uint8_t *,unsigned);
uint64_t ffta_dancer_scaled(uint64_t,uint64_t,const uint8_t *,const uint8_t *,unsigned,unsigned);
void ffta_dancer_event(uint8_t *,unsigned);
void ffta_dancer_turn_end(uint8_t *);
void ffta_dancer_action_event(const uint8_t *,unsigned,unsigned);
void ffta_dancer_hp_loss(uint8_t *,unsigned,unsigned);
void ffta_dancer_queue(unsigned *);
unsigned ffta_dancer_reaction_eligibility(const uint8_t *);
uint8_t *ffta_dancer_fury_apply(uint8_t *);
void ffta_dancer_drain(uint8_t *,unsigned,uint8_t *);
unsigned ffta_dancer_status_visual(uint8_t *,unsigned);
#endif
