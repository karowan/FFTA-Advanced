#include <stdint.h>
#include "registry.h"

extern unsigned ffta_area_list_dispatch(const uint8_t *,unsigned,unsigned,uint8_t *,unsigned,uintptr_t,uintptr_t);

/* Wind Draw stops before the first impassable or out-of-height panel. The
 * evaluated actor coordinates own the origin, including an uncommitted Move.
 * Units do not obstruct the line. */
unsigned ffta_samurai_line_geometry(unsigned ax,unsigned ay,unsigned tx,unsigned ty) {
    typedef unsigned (*TileReader)(unsigned,unsigned);
    TileReader valid=(TileReader)0x0801cc7du,height=(TileReader)0x0801cc19u,flags=(TileReader)0x0801cd09u;
    if(ax>15 || ay>15 || tx>15 || ty>15 || !valid(ax,ay))return 0;
    int dx=(int)tx-(int)ax,dy=(int)ty-(int)ay;
    if((dx&&dy)||(!dx&&!dy))return 0;
    unsigned distance=(unsigned)(dx<0?-dx:dx)+(unsigned)(dy<0?-dy:dy);
    if(distance>3)return 0;
    int sx=(dx>0)-(dx<0),sy=(dy>0)-(dy<0);
    int origin=(uint8_t)height(ax,ay);
    if(!origin)return 0;
    for(unsigned i=1;i<=distance;++i) {
        unsigned x=(unsigned)((int)ax+sx*(int)i),y=(unsigned)((int)ay+sy*(int)i);
        if(!valid(x,y)||(flags(x,y)&9u))return 0;
        int top=(uint8_t)height(x,y),delta=top-origin;
        if(!top || delta<-2 || delta>2)return 0;
    }
    return 1;
}

unsigned ffta_samurai_line_tiles(unsigned ax,unsigned ay,unsigned facing,uint8_t *output) {
    static const int8_t directions[4][2]={{0,1},{-1,0},{0,-1},{1,0}};
    if(!output || facing>3 || ax>15 || ay>15)return 0;
    unsigned count=0;
    for(unsigned distance=1;distance<=3;++distance) {
        unsigned x=(unsigned)((int)ax+directions[facing][0]*(int)distance);
        unsigned y=(unsigned)((int)ay+directions[facing][1]*(int)distance);
        if(!ffta_samurai_line_geometry(ax,ay,x,y))break;
        output[4*count]=(uint8_t)x;output[4*count+1]=(uint8_t)y;
        output[4*count+2]=(uint8_t)((unsigned (*)(unsigned,unsigned))0x0801cc19u)(x,y);
        ++count;
    }
    return count;
}

unsigned ffta_samurai_area_dispatch(const uint8_t *descriptor,unsigned facing,unsigned mode,uint8_t *output,
                                    unsigned caller,uintptr_t native_r7,uintptr_t native_r8) {
    unsigned action=descriptor[8]|((unsigned)descriptor[9]<<8);
    if(action!=FFTA_SAM_A2 && action!=FFTA_DRK_A7)
        return ffta_area_list_dispatch(descriptor,facing,mode,output,caller,native_r7,native_r8);
    const uint8_t *wrapper=0;
    if(caller==0x080b6909u && native_r8)wrapper=*(const uint8_t *const *)native_r8;
    else if(caller==0x080b59a5u)wrapper=(const uint8_t *)native_r7;
    if(wrapper && wrapper[0x1f]<4)facing=wrapper[0x1f];
    return ffta_samurai_line_tiles(descriptor[4],descriptor[5],(uint8_t)facing,output);
}
