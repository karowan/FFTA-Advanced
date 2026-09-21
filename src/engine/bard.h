#ifndef FFTA_BARD_H
#define FFTA_BARD_H
#include <stdint.h>
#define FFTA_BARD_MARCH 1u
#define FFTA_BARD_INSPIRED 2u
#define FFTA_BARD_ENCOURAGEMENT (1u<<2)
#define FFTA_BARD_BOOST_READY (1u<<3)
#define FFTA_BARD_ENCORE_READY (1u<<4)
#define FFTA_BARD_CHARGED (1u<<5)
#define FFTA_BARD_FORCED (1u<<6)
#define FFTA_BARD_BOOST_ADMITTED (1u<<24)
#define FFTA_BARD_ENCORE_ADMITTED (1u<<25)
#define FFTA_BARD_REACTION_QUEUED (1u<<26)
#define FFTA_BARD_ENCOURAGE_ADMITTED (1u<<27)
#define FFTA_BARD_ENCOURAGE_QUEUED (1u<<28)
#define FFTA_BARD_ENCOURAGE_ACTION 438u
#define FFTA_BARD_BOOST_ACTION 439u
#define FFTA_BARD_ENCORE_ACTION 440u
#define FFTA_BARD_ENCOURAGE_KIND 140u
#define FFTA_BARD_BOOST_KIND 141u
#define FFTA_BARD_ENCORE_KIND 142u
unsigned ffta_bard_incanted(unsigned);
unsigned ffta_bard_clear_voice(const uint8_t *);
unsigned ffta_bard_magick_numerator(const uint8_t *,unsigned);
void ffta_bard_passive_event(uint8_t *,unsigned);
void ffta_bard_passive_turn_end(uint8_t *);
void ffta_bard_action_event(const uint8_t *,unsigned,unsigned);
void ffta_bard_hp_loss(uint8_t *,unsigned,unsigned);
void ffta_bard_queue(unsigned *);
unsigned ffta_bard_passive_flags(const uint8_t *);
unsigned ffta_bard_reaction_eligibility(const uint8_t *);
int ffta_bard_reaction_magnitude(const uint8_t *);
uint8_t *ffta_bard_reaction_apply(uint8_t *);
uint8_t *ffta_bard_application(uint8_t *);
unsigned ffta_bard_buff(const uint8_t *,unsigned);
unsigned ffta_bard_snapshot_flags(const uint8_t *);
unsigned ffta_bard_outgoing(const uint8_t *,const uint8_t *,unsigned,unsigned);
unsigned ffta_bard_eligibility(const uint8_t *);
int ffta_bard_healing(const uint8_t *);
int ffta_bard_mp(const uint8_t *);
uint8_t *ffta_bard_buff_apply(uint8_t *);
void ffta_bard_event(uint8_t *,unsigned);
void ffta_bard_turn_end(uint8_t *);
unsigned ffta_bard_status_visual(uint8_t *,unsigned);
int ffta_bard_ai_value(int,const uint8_t *,const uint8_t *,unsigned);
void ffta_bard_ai_row(uint8_t *,const uint8_t *,const uint8_t *,unsigned);
#endif
