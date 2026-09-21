#include <stdint.h>
#include "registry.h"
#include "action-snapshot.h"
extern unsigned ffta_sea_legs(const uint8_t *);
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
static void put_half(uint8_t *p,unsigned v) { p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8); }
static int absolute(int n) { return n<0?-n:n; }
unsigned ffta_viking_near_water(const uint8_t *actor) {
    if(!actor)return 0;
    int x=actor[0xf6],y=actor[0xf7];
    int height=((int (*)(unsigned,unsigned))0x0801cc19u)(x,y);
    static const int8_t delta[5][2]={{0,0},{1,0},{-1,0},{0,1},{0,-1}};
    for(unsigned i=0;i<5;i++) {
        int nx=x+delta[i][0],ny=y+delta[i][1];
        if(nx<0 || ny<0 || nx>15 || ny>15 || !((unsigned (*)(unsigned,unsigned))0x0801cc7du)(nx,ny))continue;
        int other=((int (*)(unsigned,unsigned))0x0801cc19u)(nx,ny);
        if(absolute(height-other)<=2 && (((unsigned (*)(unsigned,unsigned))0x0801cd09u)(nx,ny)&2u))return 1;
    }
    return 0;
}
void ffta_viking_tsunami_hp_loss(uint8_t *target) {
    const uint8_t *actor=ffta_action_actor();
    uint8_t *object=(uint8_t *)ffta_action_result_object();
    if(!target || !object || object[0x2c0]>15 || !ffta_viking_near_water(actor))return;
    /* A433C's single direct HP stage calls this only after actual loss.
     * Publish its independent MP rider into the exact native recipient row:
     * A322C..A3250 uses row+C bit2 and signed row+20 for MP presentation.
     * Keep the rider even on lethal HP damage; displacement requires survival.
     */
    for(unsigned i=0;i<object[0x2c0];i++) {
        uint8_t *row=object+0x20+44u*i;
        uint8_t *wrapper=*(uint8_t **)row;
        if(!wrapper || *(uint8_t **)wrapper!=target)continue;
        unsigned amount=half(target+0x1c);if(amount>8)amount=8;
        if(amount) {
            put_half(target+0x1c,half(target+0x1c)-amount);
            put_half(row+0xc,half(row+0xc)|2u);
            put_half(row+0x20,half(row+0x20)+amount);
        }
        return;
    }
}
uint8_t *ffta_viking_tsunami_apply(uint8_t *context) {
    if(!context || (context[0x26]&0x10u) || ffta_action_phase()!=FFTA_ACTION_RESULT ||
       ffta_action_id()!=FFTA_VIK_A8)return context;
    uint8_t *target=*(uint8_t **)(context+8);
    const uint8_t *actor=*(const uint8_t *const *)context;
    const uint8_t *original=*(const uint8_t *const *)(context+4);
    const uint8_t *object=ffta_action_result_object();
    if(!target || !actor || !original || !object || !half(target+0x18) ||
       (target[0xe8]&0x40u) || !ffta_action_hp_lost(target))return context;
    if(ffta_sea_legs(original))return context;
    int ox=object[0xa],oy=object[0xb];
    if(original[0xf6]==ox && original[0xf7]==oy) { ox=actor[0xf6];oy=actor[0xf7]; }
    int dx=(int)original[0xf6]-ox,dy=(int)original[0xf7]-oy;
    if(absolute(dx)==absolute(dy))return context;
    /* The native planner reads only origin coordinates. It keeps the game's
     * occupied-tile, bounds, height, native immunity and companion checks. */
    uint8_t origin[248];for(unsigned i=0;i<sizeof(origin);i++)origin[i]=0;
    origin[0xf6]=(uint8_t)ox;origin[0xf7]=(uint8_t)oy;
    uint8_t *manager=((uint8_t *(*)(void))0x08096d7du)();
    uint8_t *wrapper=((uint8_t *(*)(uint8_t *,const uint8_t *))0x08099561u)(manager,original);
    uint8_t *companion=wrapper?*(uint8_t **)(wrapper+4):0;uint8_t x=0,y=0;
    if(((unsigned (*)(uint8_t *,const uint8_t *,const uint8_t *,uint8_t *,uint8_t *,uint8_t *))0x08098e7du)(manager,origin,original,companion,&x,&y)) {
        context[0x26]|=8u;target[0xf6]=x;target[0xf7]=y;
    }
    return context;
}
