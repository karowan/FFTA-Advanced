#ifndef FFTA_MYSTIC_KNIGHT_H
#define FFTA_MYSTIC_KNIGHT_H
#include <stdint.h>
/* Second external snapshot word, independent of the saved22-byte record. */
#define FFTA_MYK_ENCHANT_MASK 15u
#define FFTA_MYK_SEQUENCE_SHIFT 4u
#define FFTA_MYK_WEAVE (1u<<6)
#define FFTA_MYK_WARD (1u<<7)
#define FFTA_MYK_SHELL_READY (1u<<8)
#define FFTA_MYK_PARRY_READY (1u<<9)
#define FFTA_MYK_SEEN_PHYSICAL (1u<<16)
#define FFTA_MYK_SEEN_MAGIC (1u<<17)
#define FFTA_MYK_SHELL_USED (1u<<18)
#define FFTA_MYK_PARRY_USED (1u<<19)
#define FFTA_MYK_ENCHANTED (1u<<20)
#define FFTA_MYK_RESOURCE_USED (1u<<21)
void ffta_myk_resource(uint8_t *,unsigned,uint8_t *,uint8_t *);
void ffta_myk_resource_for_action(uint8_t *,unsigned,uint8_t *,uint8_t *,unsigned);
void ffta_myk_fight_after_hp(uint8_t *,unsigned);
#define FFTA_MYK_DISPEL_CHOICES 21u
#define FFTA_MYK_FLARE_RELEASE 445u
int ffta_myk_ai_self_value(int,const uint8_t *);
void ffta_myk_ai_self_row(uint8_t *,const uint8_t *);
void ffta_myk_ai_spellbreak_row(uint8_t *,const uint8_t *,const uint8_t *,unsigned);
int ffta_myk_ai_spellbreak_value(int,const uint8_t *,const uint8_t *,unsigned);
unsigned ffta_myk_usable(uint8_t *,unsigned,unsigned);
unsigned ffta_myk_accuracy(const uint8_t *);
unsigned ffta_myk_element(const uint8_t *,unsigned,unsigned);
int ffta_myk_defense(int,unsigned,const uint8_t *,unsigned);
unsigned ffta_myk_fight_kind(const uint8_t *,unsigned);
int ffta_myk_fight_element(const uint8_t *,unsigned,unsigned);
unsigned ffta_myk_fight_sleep(const uint8_t *);
int ffta_myk_fight_restorative(int,const uint8_t *);
int ffta_myk_success(const uint8_t *,uint8_t *,uint8_t *);
unsigned ffta_myk_law_hit(const uint8_t *,unsigned,const uint8_t *,unsigned);
unsigned ffta_myk_dispel_native(unsigned);
unsigned ffta_myk_dispellable(const uint8_t *,unsigned);
unsigned ffta_myk_dispel(uint8_t *,unsigned);
unsigned ffta_myk_dispel_random(uint8_t *);
unsigned ffta_myk_dispel_available(const uint8_t *,unsigned);
unsigned ffta_myk_action(unsigned);
unsigned ffta_myk_strike(unsigned);
unsigned ffta_myk_weapon(unsigned);
unsigned ffta_myk_blade(unsigned);
unsigned ffta_myk_enchantment(const uint8_t *);
unsigned ffta_myk_sequence(const uint8_t *);
unsigned ffta_myk_status_icon(const uint8_t *,unsigned);
unsigned ffta_myk_status_visual(uint8_t *,unsigned);
void ffta_myk_law_begin(void);
void ffta_myk_law_record(const uint8_t *,const unsigned *,unsigned);
unsigned ffta_myk_fight_status_forecast(const uint8_t *,const uint8_t *);
int ffta_myk_ai_break_value(const uint8_t *,const uint8_t *);
int ffta_myk_ai_strike_value(int,const uint8_t *,const uint8_t *,unsigned);
uint32_t ffta_myk_resource_plan_after_cost(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned);
uint32_t ffta_myk_resource_plan(const uint8_t *,const uint8_t *,unsigned,unsigned);
uint32_t ffta_myk_fight_resource_forecast(const uint8_t *,const uint8_t *);
int ffta_myk_fight_ai_value(int,const uint8_t *,const uint8_t *);
int ffta_myk_fight_component_preview(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned);
unsigned ffta_myk_sequence_category(const uint8_t *,unsigned);
void ffta_myk_grant(uint8_t *,unsigned);
void ffta_myk_clear(uint8_t *);
void ffta_myk_event(uint8_t *,unsigned);
void ffta_myk_action_event(const uint8_t *,unsigned,unsigned);
unsigned ffta_myk_weave_factor(const uint8_t *,unsigned);
unsigned ffta_myk_ward_factor(const uint8_t *);
unsigned ffta_myk_parry_factor(const uint8_t *,const uint8_t *,unsigned);
void ffta_myk_parry_hit(const uint8_t *,uint8_t *,unsigned);
void ffta_myk_shell_hit(const uint8_t *);
int ffta_myk_shell_preview(int,const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned,unsigned,unsigned);
int ffta_myk_doublecast_menu_forecast(int,const uint8_t *,const uint8_t *,unsigned,unsigned);
unsigned ffta_myk_element_kind(unsigned);
unsigned ffta_myk_release_kind(unsigned);
unsigned ffta_myk_doublecast_event(const uint8_t *,unsigned,unsigned);
void ffta_myk_doublecast_restore(const uint8_t *);
unsigned ffta_myk_doublecast_defer(unsigned *);
const uint8_t *ffta_myk_doublecast_wrapper(const unsigned *,const uint8_t *);
int ffta_myk_doublecast_forecast(const uint8_t *,const uint8_t *,unsigned,unsigned);
uint64_t ffta_damage_ratio(uint64_t,uint64_t,unsigned,unsigned);
unsigned ffta_myk_eligibility(const uint8_t *);
int ffta_myk_magnitude(const uint8_t *);
unsigned ffta_myk_incoming_flags(const uint8_t *,const uint8_t *,unsigned,unsigned);
#endif
