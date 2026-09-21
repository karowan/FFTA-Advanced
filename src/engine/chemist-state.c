#include "chemist-state.h"
#include "curable-status.h"
#include "job-state.h"
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
static uint8_t *owned(const uint8_t *unit) {
 uint8_t *p=ffta_job_state((uint8_t *)unit);
 return p ? p+FFTA_JOB_CHM_OFFSET:0;
}
static unsigned value(const uint8_t *unit) {
 const uint8_t *p=owned(unit);return p ? *p&FFTA_CHM_INOCULATED_MASK:0;
}
static void store(uint8_t *unit,unsigned v) {
 uint8_t *p=owned(unit);if(p)*p=(uint8_t)((*p&~FFTA_CHM_INOCULATED_MASK)|(v&FFTA_CHM_INOCULATED_MASK));
}
unsigned ffta_inoculated_active(const uint8_t *unit) {
 unsigned v=value(unit);return (v&3u)==1 || (v&3u)==2;
}
unsigned ffta_inoculated_grant(uint8_t *unit,unsigned own_turn) {
 if(!owned(unit))return 0;
 unsigned first=!ffta_inoculated_active(unit);store(unit,2u|(own_turn?4u:0));return first;
}
void ffta_chemist_turn_end(uint8_t *unit) {
 unsigned v=value(unit);
 if((v&3u)>2)store(unit,0);
 else if(v&4u)store(unit,v&3u);
 else if(v)store(unit,v-1);
}
void ffta_chemist_event(uint8_t *unit,unsigned event) {
 uint8_t *p=owned(unit);if(!p)return;
 if(event==1)*p&=(uint8_t)~FFTA_CHM_POTION_LOCK;
 /* KO/Petrify/end/job change clear the owned current mechanics. Dispel
  * removes the beneficial status, not the Auto-Potion cooldown. Harmful
  * remedies and equipment changes cannot erase preventive medicine. */
 else if(event>=2 && event<=5)*p&=(uint8_t)~(FFTA_CHM_INOCULATED_MASK|FFTA_CHM_POTION_LOCK);
 else if(event==7)store(unit,0);
}
unsigned ffta_chemist_native_curable(unsigned status) {
 /* Exact native Cureall application79 removal predicate. Its independently
  * raw set is6,8,9,10,12,26,27,28. Native12 is beneficial Conceal;
  * its removal is reveal bookkeeping, not a curable ailment. */
 return status<44 && status!=12 && ((unsigned (*)(unsigned,unsigned,unsigned))0x081339a9u)(79,status,1);
}
static unsigned enemy_application(const uint8_t *context) {
 if(!context)return 0;
 const uint8_t *actor=*(const uint8_t *const *)context;
 const uint8_t *recipient=*(const uint8_t *const *)(context+8);
 if(!actor || !recipient || actor==recipient)return 0;
 unsigned acting_side=((half(actor+0x28)>>15)^((actor[0xeb]>>5)&1))&1;
 return acting_side!=((half(recipient+0x28)>>15)&1);
}
extern unsigned ffta_chemist_auto_cureall(const uint8_t *);
unsigned ffta_chemist_prevent_native(const uint8_t *context,unsigned status) {
 return ffta_chemist_native_curable(status) &&
     ((enemy_application(context) && ffta_inoculated_active(*(const uint8_t *const *)(context+8))) || ffta_chemist_auto_cureall(context));
}
unsigned ffta_chemist_prevent_custom(const uint8_t *context,unsigned tag) {
 /* All five named tags share the approved policy. Only Blade Wound and
  * Challenged have current provider integrations; later reservations do not
  * enable their actions. No inventory or action claims are changed here. */
 return tag>=FFTA_CURABLE_BLADE_WOUND && tag<=FFTA_CURABLE_HEATHEN_FROLIC &&
     ((enemy_application(context) && ffta_inoculated_active(*(const uint8_t *const *)(context+8))) || ffta_chemist_auto_cureall(context));
}
uint8_t *ffta_chemist_inoculation(uint8_t *context) {
 if(!context)return context;
 uint8_t *recipient=*(uint8_t **)(context+8);
 if(!recipient || !half(recipient+0x18) || (recipient[0xe8]&0x44))return context;
 unsigned token=ffta_job_origin(recipient);
 if(!token)return context;
 uintptr_t canonical=token<=24 ? 0x02000080u+(token-1)*264u : 0x02002fc4u+(token-25)*264u;
 /* Native query callers sometimes pass a live unit. Only an explicit owned
  * copy can receive predicted state; never redirect a copy back to live. */
 if((context[0x26]&0x10) && (uintptr_t)recipient==canonical)return context;
 const uint8_t *actor=*(const uint8_t *const *)context;
 ffta_inoculated_grant(recipient,actor && token==ffta_job_origin(actor));
 return context;
}
/* This gate is reached only after the native callback's own resistance/Astra
 * and (Bad Breath) per-component RNG tests. The caller continuation proves
 * which setter/timer block is being suppressed. No unrelated helper user is
 * rerouted; Slow in Bad Breath keeps its original roll and application. */
unsigned ffta_chemist_status_gate(const uint8_t *context,unsigned status,unsigned caller,unsigned *frame) {
 unsigned continuation=0,expected=255,bad_breath=0;
 switch(caller) {
 case 0x08131f29:expected=8;continuation=0x08131f3b;break;
 case 0x08132505:expected=10;continuation=0x08132517;break;
 case 0x08132635:expected=28;continuation=0x0813264f;break;
 case 0x08132919:expected=26;continuation=0x08132933;break;
 case 0x08132971:expected=6;continuation=0x081329ad;break;
 case 0x08132c71:expected=27;continuation=0x08132c8b;break;
 case 0x081331dd:expected=9;continuation=0x081331ef;break;
 case 0x0813274b:expected=10;continuation=0x0813275d;bad_breath=1;break;
 case 0x08132791:expected=28;continuation=0x081327a3;bad_breath=1;break;
 case 0x081327d7:expected=27;continuation=0x081327e9;bad_breath=1;break;
 case 0x0813281d:expected=8;continuation=0x0813282f;bad_breath=1;break;
 case 0x08132863:expected=9;continuation=0x08132875;bad_breath=1;break;
 case 0x081328a9:expected=26;continuation=0x081328bb;bad_breath=1;break;
 default:return 0;
 }
 if(status!=expected || !ffta_chemist_prevent_native(context,status))return 0;
 if(bad_breath)frame[7]=(frame[7]-1u)&255u; /* undo this component's prior count */
 frame[9]=continuation;return 1;
}
extern void ffta_previous_centered_event(uint8_t *,unsigned);
extern void ffta_previous_centered_turn_end(uint8_t *);
void ffta_chemist_combined_event(uint8_t *unit,unsigned event) {
 ffta_previous_centered_event(unit,event);ffta_chemist_event(unit,event);
}
void ffta_chemist_combined_turn_end(uint8_t *unit) {
 ffta_previous_centered_turn_end(unit);ffta_chemist_turn_end(unit);
}
