#ifndef FFTA_BATTLE_WORKSPACE_H
#define FFTA_BATTLE_WORKSPACE_H
#include <stdint.h>
#include "chemist-progression.h"
#define FFTA_WORKSPACE_MANAGER_BYTES (FFTA_CHEMIST_PROGRESSION?0x450u:0x440u)
#define FFTA_WORKSPACE_PARENT_EXTRA (FFTA_CHEMIST_PROGRESSION?0x4d0u:0x4c0u)
#define FFTA_WORKSPACE_HEADER_OFFSET (FFTA_CHEMIST_PROGRESSION?0x440u:0x430u)
#define FFTA_WORKSPACE_GEOMANCER 0xcu
#define FFTA_WORKSPACE_RESULTS 0x10u
#define FFTA_WORKSPACE_EXTRA 0x19e0u
#define FFTA_WORKSPACE_EXTENSION 0x2210u
#define FFTA_WORKSPACE_DOUBLECAST 0x2610u
#define FFTA_WORKSPACE_FIGHT_LAWS 0x2620u
#define FFTA_WORKSPACE_CHEMIST 0x2660u
#define FFTA_WORKSPACE_DELAYED 0x2e60u
#define FFTA_WORKSPACE_BYTES (FFTA_CHEMIST_PROGRESSION?0x3060u:0x2660u)
/* Exact native constructor ownership, never inferred from character data. */
uint8_t *ffta_owned_battle_manager(void);
void ffta_battle_workspace_register(uint8_t *manager);
void *ffta_battle_workspace(unsigned offset);
unsigned ffta_additional_workspace_prepare(void);
void ffta_additional_workspace_retire(void *allocation);
#endif
