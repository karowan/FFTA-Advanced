#include "geomancer-map.h"
#include "geomancer.h"
#include "job-state.h"

static unsigned tile(int x,int y){
 return x>=0 && x<16 && y>=0 && y<16 &&
  ((unsigned (*)(unsigned,unsigned))0x0801cc7du)(x,y);
}
static int height(unsigned x,unsigned y){
 return (uint8_t)((unsigned (*)(unsigned,unsigned))0x0801cc19u)(x,y);
}
unsigned ffta_geo_field_board(uint8_t *owner,uint8_t *out){
 if(!out)return 0;
 for(unsigned i=0;i<256;i++)out[i]=0;
 uint8_t *peers[FFTA_JOB_UNIT_COUNT];
 unsigned count=ffta_job_peers(owner,peers,FFTA_JOB_UNIT_COUNT),covered=0;
 static const int8_t dx[5]={0,-1,1,0,0},dy[5]={0,0,0,-1,1};
 for(unsigned i=0;i<count;i++){
  unsigned kind=ffta_geo_field_kind(peers[i]);if(!kind)continue;
  const uint8_t *s=ffta_job_state(peers[i]);
  int x=s[FFTA_JOB_GEO_FIELD_X],y=s[FFTA_JOB_GEO_FIELD_Y],h=height(x,y);
  for(unsigned n=0;n<5;n++){
   int tx=x+dx[n],ty=y+dy[n];if(!tile(tx,ty))continue;
   int delta=height(tx,ty)-h;if(delta < -2 || delta > 2)continue;
   unsigned index=(unsigned)(tx+16*ty);
   if(!out[index])covered++;
   out[index]|=(uint8_t)(1u<<(kind-1));
  }
 }
 return covered;
}
unsigned ffta_geo_project_tile(int x,int y,FFTA_GeoProjection *out){
 if(!out || !tile(x,y))return 0;
 int h=height(x,y);int16_t wx,wy,wz,px,py,depth;
 ((void (*)(unsigned,unsigned,unsigned,int16_t *,int16_t *,int16_t *))
  0x0801ca79u)(x,h,y,&wx,&wy,&wz);
 ((void (*)(int,int,int,int16_t *,int16_t *,int16_t *))
  0x0801c919u)(wx,wy,wz,&px,&py,&depth);
 px-=16;py-=8;out->x=px;out->y=py;
 for(unsigned q=0;q<4;q++){
  int ox=(q&1u)*16,oy=(q>>1)*8;
  /* 1D624 replaces C918's world-depth result with the tile-index sum.
   * The two lower quarters include an equal-height forward neighbor. */
  depth=(int16_t)(x+y);
  if((q==2 && y<15 && height(x,y+1)==h) ||
     (q==3 && x<15 && height(x+1,y)==h))depth++;
  unsigned priority=((unsigned (*)(int,int,int,unsigned,unsigned,unsigned))
   0x0801ec29u)(px+ox,py+oy,depth,h,1,0);
  unsigned back=(uint8_t)priority==
   (uint8_t)((unsigned (*)(void))0x0801e63du)();
  if(!back){
   const uint8_t *clipping=((const uint8_t *(*)(unsigned))0x0801ad39u)(0);
   int tx=(px>>3)+(int)(q&1u)*2,ty=(py>>3)+(int)(q>>1);
   /* Native clipping is32 halfword strips per row, not a64-cell tilemap. */
   unsigned entry=*(const uint16_t *)(clipping+ty*64+(tx>>1)*2);
   if(!entry)back=1;
  }
  out->plane[q]=(uint8_t)back;
 }
 return 1;
}
