#ifndef FFTA_EXPANSION_MEMORY_H
#define FFTA_EXPANSION_MEMORY_H
#include "chemist-progression.h"
/* The ten new teaching items extend the 4-byte inventory view from FF30 to
 * FF58. All six transient roots move as one versioned layout, above that
 * view. They cannot occupy F000 (Passing Step) or the expanded saved bank.
 * Every reader/writer of these roots must be rebuilt in the same stage. */
#define FFTA_COPY_ROOT (FFTA_CHEMIST_PROGRESSION?0x0203ff60u:0x0203ff30u)
#define FFTA_EXECUTION_ROOT (FFTA_CHEMIST_PROGRESSION?0x0203ff74u:0x0203ff44u)
#define FFTA_SNAPSHOT_ROOT (FFTA_CHEMIST_PROGRESSION?0x0203ff78u:0x0203ff48u)
#define FFTA_AI_CHOICE_ROOT (FFTA_CHEMIST_PROGRESSION?0x0203ff7cu:0x0203f728u)
#define FFTA_MYSTIC_DAMAGE_ROOT (FFTA_CHEMIST_PROGRESSION?0x0203ff80u:0x0203f72cu)
#define FFTA_FIGHT_ROOT (FFTA_CHEMIST_PROGRESSION?0x0203ff84u:0x0203f730u)
/* Stack-owned read scopes only; not part of any save or allocation layout. */
#define FFTA_UNIT_READ_ROOT 0x0203ff88u
#endif
