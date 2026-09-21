#include <stdint.h>

/* New projectile policy, not a claim about vanilla FFTA projectiles:
 * a straight segment one raw native height unit above both tile centers.
 * Every closed tile square touched by it is covered, including corner-only
 * contacts. Endpoints are excluded; units and terrain flag masks are ignored.
 * Call after the action's ordinary range/height/target validation. */
struct RayFraction { int n,d; };

static int fraction_greater(struct RayFraction a,struct RayFraction b) {
    return a.n*b.d>b.n*a.d;
}

static int clip_axis(int origin,int delta,int low,int high,
    struct RayFraction *enter,struct RayFraction *leave) {
    if (!delta) return origin>=low && origin<=high;
    struct RayFraction a,b;
    if (delta>0) {
        a.n=low-origin;a.d=delta;b.n=high-origin;b.d=delta;
    } else {
        a.n=origin-high;a.d=-delta;b.n=origin-low;b.d=-delta;
    }
    if (fraction_greater(a,*enter)) *enter=a;
    if (fraction_greater(*leave,b)) *leave=b;
    return !fraction_greater(*enter,*leave);
}

unsigned ffta_projectile_los(unsigned actor_x,unsigned actor_y,
    unsigned target_x,unsigned target_y) {
    /* Native battle coordinates are0..15. The native validity reader then
     * enforces the current map's origin/dimensions before reading its grid.
     * Reject oversized inputs before native readers truncate to a byte. */
    if (actor_x>15 || actor_y>15 || target_x>15 || target_y>15) return 0;
    typedef unsigned (*TileReader)(unsigned,unsigned);
    TileReader valid=(TileReader)0x0801cc7du;
    TileReader height=(TileReader)0x0801cc19u;
    if (!valid(actor_x,actor_y) || !valid(target_x,target_y)) return 0;
    int start_height=(int)(uint8_t)height(actor_x,actor_y)+1;
    int delta_height=(int)(uint8_t)height(target_x,target_y)+1-start_height;
    int origin_x=2*(int)actor_x+1,origin_y=2*(int)actor_y+1;
    int delta_x=2*((int)target_x-(int)actor_x);
    int delta_y=2*((int)target_y-(int)actor_y);
    unsigned min_x=actor_x<target_x?actor_x:target_x;
    unsigned max_x=actor_x>target_x?actor_x:target_x;
    unsigned min_y=actor_y<target_y?actor_y:target_y;
    unsigned max_y=actor_y>target_y?actor_y:target_y;
    for (unsigned y=min_y;y<=max_y;++y) {
        for (unsigned x=min_x;x<=max_x;++x) {
            if ((x==actor_x && y==actor_y) || (x==target_x && y==target_y)) continue;
            struct RayFraction enter={0,1},leave={1,1};
            if (!clip_axis(origin_x,delta_x,2*(int)x,2*(int)x+2,&enter,&leave) ||
                !clip_axis(origin_y,delta_y,2*(int)y,2*(int)y+2,&enter,&leave)) continue;
            if (!valid(x,y)) return 0;
            int top=(uint8_t)height(x,y);
            /* A linear ray is lowest at entry uphill, exit downhill. Equality
             * blocks, including zero-length exact-corner intersections.
             * All products fit signed32: coords<=15, heights<=256, den<=30. */
            struct RayFraction lower=delta_height>=0?enter:leave;
            if ((top-start_height)*lower.d>=delta_height*lower.n) return 0;
        }
    }
    return 1;
}
