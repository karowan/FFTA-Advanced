#ifndef FFTA_GEOMANCER_H
#define FFTA_GEOMANCER_H
#include <stdint.h>
#define FFTA_GEO_ATTUNEMENT (1u<<13)
#define FFTA_GEO_STONE_READY (1u<<14)
#define FFTA_GEO_WRATH_READY (1u<<15)
#define FFTA_GEO_REFUGE (1u<<18)
#define FFTA_GEO_WISP (1u<<16)
#define FFTA_GEO_WISP_STRONG (1u<<17)
#define FFTA_GEO_ROCK 1u
#define FFTA_GEO_VEGETATION 2u
#define FFTA_GEO_WATER 4u
#define FFTA_GEO_HEAT 8u
#define FFTA_GEO_ICE 16u
#define FFTA_GEO_ADMITTED (1u<<21)
#define FFTA_GEO_QUEUED (1u<<22)
#define FFTA_GEO_REFUNDED (1u<<23)
#define FFTA_GEO_REFUND (1u<<31)
#define FFTA_GEO_STONE_ACTION 443u
#define FFTA_GEO_WRATH_ACTION 444u
#define FFTA_GEO_STONE_KIND 145u
#define FFTA_GEO_WRATH_KIND 146u
unsigned ffta_geo_flags(const uint8_t *);
unsigned ffta_geo_weakness(const uint8_t *,const uint8_t *,unsigned);
unsigned ffta_geo_factor(const uint8_t *,const uint8_t *,unsigned,unsigned);
void ffta_geo_hp_loss(uint8_t *,unsigned,unsigned);
void ffta_geo_action_event(const uint8_t *,unsigned,unsigned);
void ffta_geo_queue(unsigned *);
unsigned ffta_geo_reaction_eligibility(const uint8_t *);
int ffta_geo_magnitude(const uint8_t *);
void ffta_geo_mobility(uint8_t *);
void ffta_geo_tile(uint8_t *,int,int,const uint8_t *);
unsigned ffta_geo_updraft(const uint8_t *,unsigned);
unsigned ffta_geo_grounded(const uint8_t *);
unsigned ffta_geo_field_kind(const uint8_t *);
unsigned ffta_geo_field_at(const uint8_t *,int,int,unsigned);
unsigned ffta_geo_refuge(const uint8_t *);
unsigned ffta_geo_field_eligibility(const uint8_t *);
uint8_t *ffta_geo_updraft_apply(uint8_t *);
void ffta_geo_field_action(const uint8_t *,unsigned,unsigned);
void ffta_geo_event(uint8_t *,unsigned);
void ffta_geo_turn_end(uint8_t *);
int ffta_geo_move(const uint8_t *);
unsigned ffta_geo_status_visual(uint8_t *,unsigned);
unsigned ffta_geo_affinity(const uint8_t *);
unsigned ffta_geo_wisp(const uint8_t *);
unsigned ffta_geo_steady(const uint8_t *);
void ffta_geo_wisp_hp_loss(uint8_t *,unsigned,unsigned);
uint8_t *ffta_geo_ward_apply(uint8_t *);
unsigned ffta_geo_rider(const uint8_t *);
unsigned ffta_geo_choices(const uint8_t *,unsigned,uint8_t *);
unsigned ffta_geo_element(const uint8_t *,unsigned,unsigned);
uint8_t *ffta_geo_torrent_apply(uint8_t *);
unsigned ffta_geo_push_destination(const uint8_t *,unsigned,uint8_t *,uint8_t *);
#endif
