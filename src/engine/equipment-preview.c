#include <stdint.h>
#include "job-icons.h"

/* The original 7x6 panel is retained. A second page contains jobs116..125.
 * Page identity belongs to an offscreen tilemap cell on this modal surface;
 * no save bytes, unit fields or persistent scratch RAM are borrowed. */
/* Six native pixels high, proportional widths, no vertical stretching.
 * Compare against the original job-label lettering at rows5..10. */
static const struct { uint8_t width,rows[6]; } letters[26]={
 {3,{2,5,5,7,5,5}},{3,{6,5,6,5,5,6}},{3,{3,4,4,4,4,3}},
 {3,{6,5,5,5,5,6}},{3,{7,4,6,4,4,7}},{3,{7,4,6,4,4,4}},
 {4,{6,8,8,11,9,6}},{3,{5,5,7,5,5,5}},{3,{7,2,2,2,2,7}},
 {3,{1,1,1,1,5,2}},{4,{9,10,12,10,9,9}},{3,{4,4,4,4,4,7}},
 {5,{17,27,21,21,17,17}},{4,{9,13,13,11,11,9}},
 {3,{2,5,5,5,5,2}},{3,{6,5,5,6,4,4}},{4,{6,9,9,9,11,7}},
 {3,{6,5,6,5,5,5}},{3,{3,4,2,1,1,6}},{3,{7,2,2,2,2,2}},
 {3,{5,5,5,5,5,2}},{3,{5,5,5,5,5,2}},{5,{21,21,21,31,10,10}},
 {3,{5,5,2,2,5,5}},{3,{5,5,2,2,2,2}},{3,{7,1,2,2,4,7}}
};
/* Full-size seven-pixel page hint; one bitmap row per native pixel. */
static unsigned hint_glyph(unsigned c,unsigned y) {
    static const char chars[]="JLROBS12/";
    static const uint8_t rows[][7]={
        {7,2,2,2,18,18,12},{16,16,16,16,16,16,31},
        {30,17,17,30,20,18,17},{14,17,17,17,17,17,14},
        {30,17,17,30,17,17,30},{15,16,16,14,1,1,30},
        {4,12,4,4,4,4,14},{14,17,1,2,4,8,31},
        {1,1,2,4,8,16,16}
    };
    for(unsigned i=0;chars[i];++i)if(c==(unsigned)chars[i])return rows[i][y];
    return 0;
}
static void pixel(uint8_t *tiles,unsigned width,unsigned x,unsigned y,unsigned color) {
    unsigned b=((y>>3)*(width>>3)+(x>>3))*32+(y&7)*4+((x&7)>>1);
    unsigned shift=(x&1)*4;
    tiles[b]=(uint8_t)((tiles[b]&~(15u<<shift))|(color<<shift));
}
unsigned ffta_preview_job(unsigned page,unsigned cell) {
    if(page==0&&cell<42)return 2+cell;
    if(page==1&&cell<10)return 116+cell;
    return 0;
}
static volatile uint16_t *map(unsigned shop) {
    return (volatile uint16_t *)(shop?0x06005800u:0x06005000u);
}
static void hint(unsigned shop,unsigned page) {
    uint8_t tiles[288];
    for(unsigned n=0;n<sizeof tiles;++n)tiles[n]=0;
    const char *text=page?"L/R JOBS 2/2":"L/R JOBS 1/2";
    for(unsigned c=0;text[c];++c)for(unsigned y=0;y<7;++y)
        for(unsigned x=0;x<5;++x)if(hint_glyph((unsigned)text[c],y)&(16u>>x))
            pixel(tiles,72,c*6+x,y,3);
    volatile uint16_t *v=(volatile uint16_t *)(shop?0x0600f000u:0x06004800u);
    for(unsigned i=0;i<144;++i)v[i]=(uint16_t)(tiles[i*2]|tiles[i*2+1]<<8);
    volatile uint16_t *m=map(shop);
    for(unsigned i=0;i<9;++i)m[19*32+1+i]=(uint16_t)(0xd000u+(shop?0x380u:0x240u)+i);
    m[19*32+31]=(uint16_t)(0xa700u|page);
}
static void label(uint8_t *tiles,unsigned job) {
    static const char labels[10][4]={"SAM","DKN","VIK","DKN","CHM","GEO","CHM","BRD","DNC","MYK"};
    if(job<116||job>125)return;
    /* Restore the colored panel, then draw a one-pixel native dark outline.
     * Palette indices3/4 are the original lettering's light/dark pair. */
    for(unsigned y=4;y<12;++y)for(unsigned x=17;x<31;++x)pixel(tiles,32,x,y,12);
    unsigned width=2;
    for(unsigned c=0;c<3;++c)width+=letters[labels[job-116][c]-'A'].width;
    for(unsigned pass=0;pass<2;++pass) {
        unsigned left=31-width;
        for(unsigned c=0;c<3;++c) {
            unsigned g=labels[job-116][c]-'A',w=letters[g].width;
            for(unsigned y=0;y<6;++y)for(unsigned x=0;x<w;++x)
                if(letters[g].rows[y]&(1u<<(w-1-x))) {
                    if(pass)pixel(tiles,32,left+x,5+y,3);
                    else for(int dy=-1;dy<=1;++dy)for(int dx=-1;dx<=1;++dx)
                        if(left+x+dx<31)pixel(tiles,32,left+x+dx,5+y+dy,4);
                }
            left+=w+1;
        }
    }
}
unsigned ffta_icon_decode(void *destination,unsigned job) {
    job&=255;
    if(job<116||job>125)
        return ((unsigned (*)(void *,unsigned))FFTA_ORIGINAL_ICON)(destination,job);
    uint8_t *pixels=(uint8_t *)destination;
    for(unsigned i=0;i<256;++i)pixels[i]=original_job_icons[job-116][i];
    label(pixels,job);
    return 0;
}
void ffta_preview_draw(unsigned item,unsigned shop,unsigned page) {
    uint16_t tiles[128];
    volatile uint16_t *m=map(shop);
    volatile uint16_t *graphics=(volatile uint16_t *)(shop?0x0600b000u:0x06000020u);
    page&=1;shop=!!shop;
    for(unsigned y=2;y<19;++y)for(unsigned x=1;x<29;++x)m[y*32+x]=0;
    unsigned row=0,column=0;
    for(unsigned i=0;i<42;++i) {
        unsigned job=ffta_preview_job(page,i);
        if(!job)break;
        ((void (*)(void *,unsigned))0x080cb9e1u)(tiles,job);
        for(unsigned n=0;n<128;++n)graphics[i*128+n]=tiles[n];
        unsigned eligible=((unsigned (*)(unsigned,unsigned))0x080cb5a9u)(job,item);
        unsigned palette=((unsigned (*)(unsigned))0x080cba15u)(job);
        if(!eligible)palette-=shop?6:13;
        unsigned tile=(shop?0x180u:1u)+i*8;
        for(unsigned y=0;y<2;++y)for(unsigned x=0;x<4;++x)
            m[(2+row*3+y)*32+1+column*4+x]=(uint16_t)((palette<<12)+tile+y*4+x);
        if(++column==7){column=0;++row;}
    }
    hint(shop,page);
}
unsigned ffta_preview_turn(unsigned shop) {
    unsigned keys=*(volatile uint16_t *)0x03000002u;
    volatile uint16_t *m=map(shop);
    if(keys&3) {
        for(unsigned x=1;x<=9;++x)m[19*32+x]=0;
        m[19*32+31]=0;
        return keys&3;
    }
    if(keys&0x300) {
        unsigned item;
        if(shop)item=*(uint16_t *)(*(uintptr_t *)0x0200f428u+0x44ecu);
        else item=((unsigned (*)(unsigned,unsigned,int))0x080876f5u)(0,0,-1);
        ffta_preview_draw(item,shop,(m[19*32+31]&1)^1);
        ((void (*)(unsigned))0x08141541u)(0x65);
    }
    return 0;
}
