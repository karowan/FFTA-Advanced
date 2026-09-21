#include <stdint.h>
#include "registry.h"

extern unsigned ffta_original_area_list(const uint8_t *,unsigned,unsigned,uint8_t *);

unsigned ffta_arc_confirm_facing(unsigned fallback,const uint8_t *selection) {
    unsigned action=selection[0xec]|((unsigned)selection[0xed]<<8);
    const uint8_t *wrapper=*(const uint8_t *const *)selection;
    if((action==FFTA_SLD_AX_A3 || action==FFTA_GLD_AX_A2) && wrapper && wrapper[0x1f]<4)
        return wrapper[0x1f];
    return fallback;
}

unsigned ffta_arc_launch_facing(unsigned fallback,const uint8_t *battle_manager) {
    unsigned action=battle_manager[0xa6]|((unsigned)battle_manager[0xa7]<<8);
    const uint8_t *wrapper=*(const uint8_t *const *)(battle_manager+4);
    if((action==FFTA_SLD_AX_A3 || action==FFTA_GLD_AX_A2) && wrapper && wrapper[0x1f]<4)
        return wrapper[0x1f];
    return fallback;
}

void ffta_arc_commit_facing(uint8_t *action_object) {
    unsigned action=action_object[0x10]|((unsigned)action_object[0x11]<<8);
    const uint8_t *wrapper=*(const uint8_t *const *)action_object;
    if((action==FFTA_SLD_AX_A3 || action==FFTA_GLD_AX_A2) && wrapper && wrapper[0x1f]<4)
        action_object[8]=wrapper[0x1f];
}

void ffta_arc_ai_facing(uint8_t *battle_manager) {
    unsigned action=battle_manager[0xa6]|((unsigned)battle_manager[0xa7]<<8);
    if(action!=FFTA_SLD_AX_A3 && action!=FFTA_GLD_AX_A2)return;
    /* BFDB0 publishes the evaluated direction separately from the AI's
     * end-turn facing. Validate the selected node and exact actor wrapper. */
    const uint8_t *node=(const uint8_t *)0x02015488u;
    uint8_t *wrapper=*(uint8_t **)(battle_manager+4);
    unsigned selected=node[8]|((unsigned)node[9]<<8);
    if(wrapper && *(uint8_t *const *)node==wrapper && selected==action && node[0x1b1]==1 && node[0x1b0]<4)
        wrapper[0x1f]=node[0x1b0];
}

unsigned ffta_arc_geometry(unsigned actor_x,unsigned actor_y,unsigned target_x,unsigned target_y) {
    typedef unsigned (*TileReader)(unsigned,unsigned);
    TileReader valid=(TileReader)0x0801cc7du,height=(TileReader)0x0801cc19u,flags=(TileReader)0x0801cd09u;
    if(actor_x>15 || actor_y>15 || target_x>15 || target_y>15 || !valid(actor_x,actor_y) || !valid(target_x,target_y))return 0;
    int dx=(int)target_x-(int)actor_x,dy=(int)target_y-(int)actor_y;
    if((!dx&&!dy) || dx<-1 || dx>1 || dy<-1 || dy>1 || (flags(target_x,target_y)&9u))return 0;
    unsigned from=(uint8_t)height(actor_x,actor_y),to=(uint8_t)height(target_x,target_y);
    /* Native A0014 rejects both endpoints when9D79C returns zero height. */
    if(!from || !to)return 0;
    int delta=(int)to-(int)from;
    return delta>=-2 && delta<=2;
}

/* Native9D66C directions:0 south,1 west,2 north,3 east. The tile records
 * consumed by battle selectors are four bytes; native writes x,y,height and
 * leaves byte3 to its caller. Preserve that convention and bounded output. */
unsigned ffta_arc_tiles(unsigned actor_x,unsigned actor_y,unsigned facing,uint8_t *output) {
    static const int8_t forward[4][2]={{0,1},{-1,0},{0,-1},{1,0}};
    typedef unsigned (*TileReader)(unsigned,unsigned);
    TileReader valid=(TileReader)0x0801cc7du;
    TileReader height=(TileReader)0x0801cc19u;
    if(!output || actor_x>15 || actor_y>15 || facing>3 || !valid(actor_x,actor_y))return 0;
    int dx=forward[facing][0],dy=forward[facing][1];
    unsigned count=0;
    /* Center-front first, then the two flanks. No caster tile is generated. */
    static const int8_t lateral[3]={0,-1,1};
    for(unsigned i=0;i<3;++i) {
        int x=(int)actor_x+dx-dy*lateral[i];
        int y=(int)actor_y+dy+dx*lateral[i];
        if(!ffta_arc_geometry(actor_x,actor_y,(unsigned)x,(unsigned)y))continue;
        int top=(uint8_t)height((unsigned)x,(unsigned)y);
        output[4*count]=(uint8_t)x;output[4*count+1]=(uint8_t)y;
        output[4*count+2]=(uint8_t)top;++count;
    }
    return count;
}

unsigned ffta_area_list(const uint8_t *descriptor,unsigned facing,unsigned mode,uint8_t *output) {
    unsigned action=descriptor[8]|((unsigned)descriptor[9]<<8);
    if(action!=FFTA_SLD_AX_A3 && action!=FFTA_GLD_AX_A2)
        return ffta_original_area_list(descriptor,facing,mode,output);
    return ffta_arc_tiles(descriptor[4],descriptor[5],(uint8_t)facing,output);
}

unsigned ffta_area_list_dispatch(const uint8_t *descriptor,unsigned facing,unsigned mode,uint8_t *output,
                                 unsigned caller,uintptr_t native_r7,uintptr_t native_r8) {
    unsigned action=descriptor[8]|((unsigned)descriptor[9]<<8);
    if(action==FFTA_SLD_AX_A3 || action==FFTA_GLD_AX_A2) {
        /* The directional cursor already records the requested facing on its
         * actor wrapper. Re-deriving it from an auto-selected diagonal unit
         * turns a north/south arc sideways when its center tile is invalid.
         * Only these two UI callers expose this wrapper; AI keeps its explicit
         * evaluated direction, including inverse attack-position searches. */
        const uint8_t *wrapper=0;
        if(caller==0x080b6909u && native_r8)
            wrapper=*(const uint8_t *const *)native_r8;
        else if(caller==0x080b59a5u)wrapper=(const uint8_t *)native_r7;
        if(wrapper && wrapper[0x1f]<4)facing=wrapper[0x1f];
    }
    return ffta_area_list(descriptor,facing,mode,output);
}
