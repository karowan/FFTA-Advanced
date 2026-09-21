#include <stdint.h>
#include "registry.h"

/* This is the native eight-argument A0014 geometry ABI. Coordinates belong to
 * the evaluated action (including Move previews), not unit F6/F7 or an owner.
 * The trampoline replays the displaced native entry and runs its full body. */
extern unsigned ffta_original_combat_geometry(const uint8_t *unit,
    unsigned actor_x, unsigned actor_y, unsigned target_x, unsigned target_y,
    unsigned action, unsigned item, unsigned mode);
extern unsigned ffta_projectile_los(unsigned,unsigned,unsigned,unsigned);
extern unsigned ffta_arc_geometry(unsigned,unsigned,unsigned,unsigned);

unsigned ffta_combat_geometry(const uint8_t *unit,
    unsigned actor_x, unsigned actor_y, unsigned target_x, unsigned target_y,
    unsigned action, unsigned item, unsigned mode) {
    /* The directional list selects facing. Each possible recipient lies in
     * the eight neighboring cells; native Earth Render's cardinal-only
     * geometry would otherwise discard both flanks. Keep its native terrain
     * and positive-height endpoint rules in the shared arc predicate. */
    if((uint16_t)action==FFTA_SLD_AX_A3 || (uint16_t)action==FFTA_GLD_AX_A2)
        return ffta_arc_geometry((uint8_t)actor_x,(uint8_t)actor_y,
            (uint8_t)target_x,(uint8_t)target_y);
    unsigned result=ffta_original_combat_geometry(unit,actor_x,actor_y,
        target_x,target_y,action,item,mode);
    if (!result) return result;
    if ((uint16_t)action==FFTA_SLD_AX_A2)
        return ffta_projectile_los((uint8_t)actor_x,(uint8_t)actor_y,
            (uint8_t)target_x,(uint8_t)target_y);
    if ((uint16_t)action!=FFTA_SLD_AX_A1 &&
        (uint16_t)action!=FFTA_SLD_AX_A4 &&
        (uint16_t)action!=FFTA_GLD_AX_A1 &&
        (uint16_t)action!=FFTA_GLD_AX_A3 &&
        (uint16_t)action!=FFTA_GLD_AX_A4 &&
        (uint16_t)action!=FFTA_DRK_A2 && (uint16_t)action!=FFTA_DRK_A3) return result;

    /* Preserve native terrain/shape/validity checks first. Its ordinary melee
     * rule permits three levels down and two up; the approved new-job rule
     * is symmetric two for axes and three for the ranged sword arts.
     * Native1CC18 returns the raw tile-height byte used by
     * the native spell and weapon height checks; no unit-record lookup or
     * graphical-coordinate conversion is appropriate here. */
    typedef unsigned (*TileHeight)(unsigned,unsigned);
    TileHeight height=(TileHeight)0x0801cc19u;
    unsigned from=(uint8_t)height((uint8_t)actor_x,(uint8_t)actor_y);
    unsigned to=(uint8_t)height((uint8_t)target_x,(uint8_t)target_y);
    unsigned difference=from>to ? from-to : to-from;
    return difference<=(((uint16_t)action==FFTA_DRK_A2 || (uint16_t)action==FFTA_DRK_A3)?3:2);
}
