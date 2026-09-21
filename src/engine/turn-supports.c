#include "turn-supports.h"
#include "registry.h"
#include "job-state.h"
#include "action-snapshot.h"
#include "bard.h"
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static unsigned support(const uint8_t *u){return u?((unsigned (*)(const uint8_t *))0x080cd50du)(u):0;}
/* Owned12/13: turn-start tile.14 low3: active1, movement2, net>=2 4.
 * Its upper5 and byte19 bits3..4 retain the original signed-byte allowance.
 * Byte19 bits5..6 store min(2, remaining), bit7 authenticates the ledger;
 * bits0..2 remain Geomancer's independent Steady timer. Old saves without
 * bit7 cannot invent remaining movement before their next native turn start.
 * These explicit-owner fields survive native copies and suspend transport.
 * Neither a character identity match nor the native command-spent flag proves
 * movement. Only the observed completion/cancellation callers write this tag. */
static unsigned original_allowance(const uint8_t *s){return (s[14]>>3)|(((s[19]>>3)&3u)<<5);}
static unsigned ledger_valid(const uint8_t *s){return s && (s[14]&1u) && (s[19]&128u);}
static void remaining(uint8_t *s,unsigned n){s[19]=(uint8_t)((s[19]&159u)|((n>2?2:n)<<5));}
static void clear_turn(uint8_t *s){s[12]=s[13]=s[14]=0;s[19]&=7u;}
void ffta_turn_close_movement(uint8_t *u){uint8_t *s=ffta_job_state(u);if(ledger_valid(s))remaining(s,0);}
unsigned ffta_turn_original_allowance(const uint8_t *u){
 const uint8_t *s=ffta_job_state((uint8_t *)u);return ledger_valid(s)?original_allowance(s):0;
}
unsigned ffta_turn_step_remaining(const uint8_t *u){
 const uint8_t *s=ffta_job_state((uint8_t *)u);unsigned n=ledger_valid(s)?(s[19]>>5)&3u:0;
 return n<=2?n:0;
}
static unsigned route_cost(const uint8_t *w,const uint8_t *s){
 unsigned x=half(w+8)>>5,y=half(w+12)>>5;
 const uint8_t *grid=*(const uint8_t *const *)(w+0x3c);
 /* Native97504 bounds path-grid coordinates to0..15 before querying the
  * board.1CC7C alone truncates its operands to bytes and is not this guard. */
 if(!grid || x>15 || y>15 || grid[0x986]!=s[12] || grid[0x987]!=s[13] ||
    !((unsigned (*)(const uint8_t *))0x08149369u)(grid) ||
    !((unsigned (*)(unsigned,unsigned))0x0801cc7du)(x,y) ||
    !((unsigned (*)(const uint8_t *,unsigned,unsigned))0x08149385u)(grid,x,y))return 0;
 /* Native1493AC reads the accumulated terrain cost in node byte4. Native
  * route nodes also carry coordinates/height, not the total points spent. */
 return ((unsigned (*)(const uint8_t *,unsigned,unsigned))0x081493adu)(grid,x,y);
}
void ffta_turn_event(uint8_t *u,unsigned event){
 uint8_t *s=ffta_job_state(u);if(!s)return;
 if(event==1){
  int native=((int (*)(const uint8_t *))0x080ca395u)(u);
  unsigned n=native>=0&&native<=127?(unsigned)native:0;
  s[12]=u[0xf6];s[13]=u[0xf7];s[14]=(uint8_t)(1u|((n&31u)<<3));
  s[19]=(uint8_t)((s[19]&7u)|((n>>5)<<3)|128u);remaining(s,n);
 }
 else if(event>=2 && event<=5)clear_turn(s);
}
void ffta_turn_end(uint8_t *u){uint8_t *s=ffta_job_state(u);if(s)clear_turn(s);}
extern unsigned ffta_original_turn_flag(unsigned,unsigned);
unsigned ffta_turn_flag(unsigned flag,unsigned value,unsigned caller){
 if(flag==4 && ((caller==0x080968d3u && value) || (caller==0x08096343u && !value))){
  const uint8_t *w=*(const uint8_t *const *)0x0200f4ecu;
  if(w){
   uint8_t *u=*(uint8_t *const *)w,*s=ffta_job_state(u);
   if(s && (s[14]&1u)){
    if(!value){
     s[14]=(uint8_t)((s[14]&248u)|1u);
     if(ledger_valid(s))remaining(s,original_allowance(s));
    } /* Native undo returns wrapper to the original tile. */
    else {
     int x=(int)(half(w+8)>>5)-s[12],y=(int)(half(w+12)>>5)-s[13];
     unsigned distance=(unsigned)(x<0?-x:x)+(unsigned)(y<0?-y:y);
     s[14]=(uint8_t)((s[14]&248u)|3u|(distance>=2?4u:0));
     if(ledger_valid(s)){
      unsigned used=route_cost(w,s),allowance=original_allowance(s);
      remaining(s,used && used<=allowance?allowance-used:0);
     }
    }
   }
  }
 }
 return ffta_original_turn_flag(flag,value);
}
static unsigned readiness(const uint8_t *u){
 const uint8_t *s=ffta_job_state((uint8_t *)u);
 return u && s && half(u+0x18) && !(u[0xe8]&0x40u) && !(u[0xeb]&0x30u)?s[14]:0;
}
unsigned ffta_turn_snapshot_flags(const uint8_t *u){
 return (readiness(u)&3u)==1 && support(u)==FFTA_SAM_S1?FFTA_COMPOSURE_READY:0;
}
unsigned ffta_turn_extra_flags(const uint8_t *u){
 return (readiness(u)&7u)==7 && support(u)==FFTA_GLD_AX_S1?FFTA_FOLLOW_THROUGH_READY:0;
}
static unsigned factor(const uint8_t *a,unsigned physical){
 if(!a || ffta_action_origin()==FFTA_ACTION_NATIVE_REACTION || ffta_action_origin()==FFTA_ACTION_EXPLICIT_COMBO ||
    (ffta_action_unit_extra_flags(a)&FFTA_BARD_FORCED))return 20;
 if(ffta_action_unit_flags(a)&FFTA_COMPOSURE_READY)return 25;
 return physical && (ffta_action_unit_extra_flags(a)&FFTA_FOLLOW_THROUGH_READY)?27:20;
}
unsigned ffta_turn_damage_numerator(const uint8_t *a,const uint8_t *t,unsigned action,unsigned physical){
 if(!a || !t || action==265)return 20;
 unsigned f=ffta_action_unit_flags(t);
 if((f&24u)==24u)return 20;
 if(!(f&8u) && a!=t && action!=265 && ((unsigned (*)(const uint8_t *))0x0812e6a5u)(t)==13 &&
    ((unsigned (*)(const uint8_t *,unsigned))0x080c7ea5u)(t,0x15) &&
    (!action || !((unsigned (*)(unsigned,unsigned))0x080ccd51u)(action,17)))return 20;
 return factor(a,physical);
}
unsigned ffta_turn_healing_numerator(const uint8_t *a){return factor(a,0);}
