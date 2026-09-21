#ifndef FFTA_PERSISTENT_H
#define FFTA_PERSISTENT_H
#include <stdint.h>
int ffta_storage_format(const uint8_t *state);
int ffta_migrate_inventory(uint8_t *state);
unsigned ffta_owned(const uint8_t *state, unsigned id);
int ffta_give_item(uint8_t *state, unsigned id, unsigned amount);
int ffta_lose_item(uint8_t *state, unsigned id, unsigned amount);
#endif
