#include "reaction-queue.h"
#include "action-snapshot.h"
#include "reaction-ids.h"
extern unsigned ffta_action_owns_native_frame(const unsigned *);
extern unsigned ffta_additional_action_limit(void);
static unsigned action_limit(void) {
 unsigned n=ffta_additional_action_limit();return n?n:FFTA_GLOBAL_ACTION_COUNT;
}
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
static unsigned valid_ram(uintptr_t p,unsigned n) { return !(p&3u) && p>=0x02000000u && p<=0x02040000u-n; }
static unsigned valid_frame(const unsigned *f) {
 uintptr_t p=(uintptr_t)f,sp;
 __asm__ volatile("mov %0, sp":"=r"(sp));
 return ffta_action_owns_native_frame(f) && p>=sp && !(p&3u) && p>=0x03000000u && p<=0x03008000u-0xb8 &&
   valid_ram(f[0x20/4],0x26c0) && valid_ram(f[0x68/4],256) && f[0x68/4]>=0x0200000cu &&
   ((const uint16_t *)(f[0x68/4]-12))[2]==0x616cu &&
   ((const uint16_t *)(f[0x68/4]-12))[3]*4u>=268u &&
   f[0x6c/4]>=f[0x68/4] && f[0x6c/4]<=f[0x68/4]+240 &&
   !((f[0x6c/4]-f[0x68/4])&15u) &&
   f[0x70/4]>=f[0x6c/4] && f[0x70/4]<=f[0x68/4]+240 &&
   !((f[0x70/4]-f[0x68/4])&15u);
}
static unsigned known_unit(const uint8_t *unit) {
 for(unsigned i=0;i<64;i++) {const uint8_t *p=ffta_action_unit_at(i);if(!p)return 0;if(p==unit)return 1;}
 return 0;
}
static const uint8_t *wrapper_for(const unsigned *f,const uint8_t *unit) {
 const uint8_t *primary=(const uint8_t *)f[0x24/4];
 if(valid_ram((uintptr_t)primary,4) && *(const uint8_t *const *)primary==unit)return primary;
 const uint8_t *output=(const uint8_t *)f[0x20/4];unsigned count=output[0x26bd];
 if(count>13)return 0;
 for(unsigned i=0;i<count;i++) {
  const uint8_t *object=output+i*0x2c4;unsigned rows=object[0x2c0];
  if(rows>15)return 0;
  for(unsigned j=0;j<rows;j++) {
   const uint8_t *w=*(const uint8_t *const *)(object+0x20+j*0x2c);
   if(valid_ram((uintptr_t)w,4) && *(const uint8_t *const *)w==unit)return w;
  }
 }
 extern const uint8_t *ffta_additional_reaction_wrapper(const unsigned *,const uint8_t *);
 const uint8_t *saved=ffta_additional_reaction_wrapper(f,unit);
 return valid_ram((uintptr_t)saved,4) && *(const uint8_t *const *)saved==unit?saved:0;
}
unsigned ffta_reaction_queue_append(unsigned *f,const uint8_t *acting,const uint8_t *target,
 unsigned action,unsigned kind,unsigned payload) {
 if(!valid_frame(f) || !acting || !target || !known_unit(acting) || !known_unit(target) || kind<128 || kind>255 || action>=action_limit() || payload>65535 ||
    ffta_action_phase()!=FFTA_ACTION_COMPLETING || ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY)return 0;
 const uint8_t *output=(const uint8_t *)f[0x20/4];
 /* Fourteen native object slots include the scratch-next slot touched even
  * during queue exhaustion. Keep at most13 displayed objects and reserve
  * one output for each pending custom single-result request. */
 unsigned pending=(f[0x70/4]-f[0x6c/4])/16;
 if(output[0x26bd]+pending>=13 || f[0x70/4]>=f[0x68/4]+240)return 0;
 const uint8_t *wrapper=wrapper_for(f,acting);
 if(!wrapper || !wrapper_for(f,target))return 0;
 uint8_t *request=(uint8_t *)f[0x70/4];
 for(unsigned i=0;i<16;i++)if(request[i])return 0;
 *(const uint8_t **)request=wrapper;
 *(const uint8_t **)(request+4)=(const uint8_t *)f[0x24/4];
 request[8]=(uint8_t)action;request[9]=(uint8_t)(action>>8);
 request[10]=target[0xf6];request[11]=target[0xf7];request[12]=0;
 request[13]=(uint8_t)payload;request[14]=(uint8_t)kind;request[15]=(uint8_t)(payload>>8);
 f[0x70/4]+=16;return 1;
}
unsigned ffta_reaction_request_metadata(const unsigned *f,const uint8_t *object,const uint8_t *original_wrapper) {
 if(!valid_frame(f) || !valid_ram((uintptr_t)object,0x2c4) || (const uint8_t *)f[0x24/4]!=original_wrapper ||
    f[0x6c/4]<f[0x68/4]+16)return 0;
 const uint8_t *r=(const uint8_t *)(f[0x6c/4]-16);
 if(r[14]<128 || *(const uint8_t *const *)r!=*(const uint8_t *const *)object ||
    *(const uint8_t *const *)(r+4)!=original_wrapper || half(r+8)!=half(object+0x10))return 0;
 return ((unsigned)r[14]<<8)|((unsigned)r[13]<<16)|((unsigned)r[15]<<24);
}
extern void ffta_action_queue_complete(unsigned *);
unsigned ffta_reaction_queue_dispatch(unsigned *f) {
 if(!valid_frame(f))return 0;
 uint8_t *r=(uint8_t *)f[0x6c/4];
 if(!*(unsigned *)r)ffta_action_queue_complete(f);
 r=(uint8_t *)f[0x6c/4];
 if(!*(unsigned *)r || r[14]<128)return 0;
 if(!valid_ram(*(unsigned *)r,4))return 0;
 const uint8_t *actor=**(const uint8_t *const *const *)r;
 if(!actor || half(r+8)>=action_limit() || *(unsigned *)(r+4)!=f[0x24/4])return 0;
 f[0x44/4]=r[10];f[0x48/4]=r[11];f[0x4c/4]=half(r+8);
 f[0x50/4]=0;f[0x74/4]=*(unsigned *)r;f[0x38/4]=1;
 /* Reuse the native weapon/item argument buffer exactly as native queued
  * Counter does. Every custom request has one result, never an offhand. */
 unsigned selected=r[14]==136 ? r[13]|((unsigned)r[15]<<8):half(actor+0x2a);
 *(volatile uint16_t *)0x0200f888u=(uint16_t)selected;
 *(volatile uint8_t *)0x0200f890u=0;
 return 1;
}
