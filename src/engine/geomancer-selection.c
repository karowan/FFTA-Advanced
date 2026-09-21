#include <stdint.h>
#include "registry.h"
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
extern unsigned ffta_geo_original_center(const uint8_t *,unsigned,unsigned,unsigned,unsigned);
unsigned ffta_geo_center(const uint8_t *wrapper,unsigned x,unsigned y,unsigned choice,
                         unsigned action,const uint8_t *selection,unsigned caller){
 /* These two native player calls follow the range/cross tile-list builders.
  * Field placement needs a legal center, not an eligible recipient. Keep the
  * true empty recipient list; inventing a target would corrupt forecasts,
  * laws and the final result object. Other callers keep native behavior. */
 if((action==FFTA_GEO_A7 || action==FFTA_GEO_A9) &&
    (caller==0x080b780fu || caller==0x080b76b3u) && selection && wrapper &&
    *(const uint8_t *const *)selection==wrapper &&
    *(const uint8_t *const *)0x0200f4ecu==wrapper && half(selection+0xec)==action &&
    x<16 && y<16 && selection[0x109]==x && selection[0x10a]==y){
  const uint8_t *m=*(const uint8_t *const *)0x0200f438u;
  unsigned count=half(selection+0x110);
  if(m && m[4]>=6 && m[4]<=11 && *(const uint8_t *const *)(m+24)==*(const uint8_t *const *)wrapper &&
     count<=25 && selection[0xf6]<=1 && ((unsigned (*)(unsigned,unsigned))0x0801cc7du)(x,y)){
   for(unsigned i=0;i<count;i++){
    const uint8_t *tile=selection+0x112+4*i;
    if(tile[0]==x && tile[1]==y)return 1;
   }
  }
 }
 return ffta_geo_original_center(wrapper,x,y,choice,action);
}
