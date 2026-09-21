#ifndef FFTA_CHEMIST_ITEMS_H
#define FFTA_CHEMIST_ITEMS_H
#include <stdint.h>
typedef struct { uint16_t item[2]; unsigned count,donor; } FFTA_ChemistRecipe;
unsigned ffta_chemist_action(unsigned action);
unsigned ffta_chemist_recipe(unsigned action,unsigned selected,FFTA_ChemistRecipe *out);
unsigned ffta_chemist_stocked(unsigned action,unsigned selected);
unsigned ffta_chemist_pay(unsigned action,unsigned selected);
unsigned ffta_chemist_eligibility(const uint8_t *context);
int ffta_chemist_hp(const uint8_t *context);
int ffta_chemist_mp(const uint8_t *context);
int ffta_chemist_revive(const uint8_t *context);
#endif
