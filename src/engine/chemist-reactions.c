#include "action-snapshot.h"
#include "chemist-state.h"
#include "job-state.h"
#include "registry.h"
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
extern unsigned ffta_native_free_count(unsigned);
extern int ffta_native_lose_item(unsigned,unsigned);
extern unsigned ffta_action_reactions_enabled(void);
/* Common native R admission: universal mask intersection0/31/32/43,
 * plus explicit living/Petrify. Incoming curable status is tested against
 * this action-start snapshot, never retroactively against its own setter. */
unsigned ffta_chemist_reaction_admission(const uint8_t *unit) {
 if(!unit || !half(unit+0x18))return 0;
 return !(unit[0xe8]&0x41u) && !(unit[0xeb]&0x80u) &&
        !(unit[0xec]&1u) && !(unit[0xed]&8u);
}
unsigned ffta_chemist_snapshot_flags(const uint8_t *unit) {
 if(!ffta_chemist_reaction_admission(unit))return 0;
 unsigned reaction=((unsigned (*)(const uint8_t *))0x080cd4d5u)(unit);
 if(reaction==FFTA_CHM_R2)return FFTA_ACTION_FLAG_AUTO_CUREALL;
 if(reaction==FFTA_CHM_R1)return FFTA_ACTION_FLAG_AUTO_POTION;
 return 0;
}
static unsigned frozen_enemy(const uint8_t *actor,const uint8_t *recipient) {
 unsigned a=ffta_action_unit_flags(actor),r=ffta_action_unit_flags(recipient);
 if(actor==recipient || (r&4u))return 0;
 return (((a>>7)^(a>>8))&1u)!=((r>>7)&1u);
}
unsigned ffta_chemist_auto_cureall(const uint8_t *context) {
 if(!context)return 0;
 const uint8_t *actor=*(const uint8_t *const *)context;
 uint8_t *recipient=*(uint8_t *const *)(context+8);
 if(!actor || !recipient || !half(recipient+0x18))return 0;
 unsigned origin=ffta_job_origin(recipient);
 if(!origin || origin>24)return 0; /* exact player inventory owner only */
 if(!(ffta_action_unit_flags(recipient)&FFTA_ACTION_FLAG_AUTO_CUREALL) || !frozen_enemy(actor,recipient))return 0;
 unsigned query=(context[0x26]&0x10u) || ffta_action_phase()==FFTA_ACTION_QUERY;
 if(query) {
  /* A law/preview may inherit a paid latch, but cannot acquire one or debit. */
  return ffta_action_claimed(recipient,FFTA_ACTION_CLAIM_AUTO_CUREALL) || ffta_native_free_count(374)!=0;
 }
 if(ffta_action_phase()!=FFTA_ACTION_RESULT || !ffta_action_origin() ||
    !ffta_action_reactions_enabled())return 0;
 if(ffta_action_claimed(recipient,FFTA_ACTION_CLAIM_AUTO_CUREALL))return 1;
 if(!ffta_native_free_count(374))return 0;
 /* The authenticated recipient is present in this exact scope. No yield or
  * callback occurs between debit and claim; unknown copies fail above. */
 ffta_native_lose_item(374,1);
 return ffta_action_claim(recipient,FFTA_ACTION_CLAIM_AUTO_CUREALL);
}
#include "reaction-queue.h"
#define AUTO_POTION_ADMITTED 4u
#define AUTO_POTION_SCHEDULED 2048u
#define AUTO_CUREALL_PRESENTED 4096u
void ffta_chemist_hp_loss(uint8_t *unit,unsigned before,unsigned after) {
 unsigned origin=ffta_job_origin(unit);
 if(!origin || origin>24 || before<=after || !after ||
    ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY || !ffta_action_reactions_enabled() ||
    !(ffta_action_unit_flags(unit)&FFTA_ACTION_FLAG_AUTO_POTION) ||
    !frozen_enemy(ffta_action_actor(),unit))return;
 ffta_action_claim(unit,AUTO_POTION_ADMITTED);
}
void ffta_chemist_reaction_queue(unsigned *frame) {
 if(ffta_action_phase()!=FFTA_ACTION_COMPLETING || ffta_action_origin()!=FFTA_ACTION_NATIVE_PRIMARY)return;
 for(unsigned i=0;i<64;i++) {
  uint8_t *unit=(uint8_t *)ffta_action_unit_at(i);if(!unit)break;
  unsigned origin=ffta_job_origin(unit);if(!origin || origin>24)continue;
  if(ffta_action_claimed(unit,FFTA_ACTION_CLAIM_AUTO_CUREALL) &&
     !ffta_action_claimed(unit,AUTO_CUREALL_PRESENTED)) {
   if(ffta_reaction_queue_append(frame,unit,unit,432,137,0))
    ffta_action_claim(unit,AUTO_CUREALL_PRESENTED);
   return;
  }
  if(!ffta_action_claimed(unit,AUTO_POTION_ADMITTED) ||
     ffta_action_claimed(unit,AUTO_POTION_SCHEDULED) || !ffta_chemist_reaction_admission(unit))continue;
  uint8_t *state=ffta_job_state(unit),*preference=ffta_job_potion(unit);
  if(!state || !preference || *preference>1 || (state[FFTA_JOB_CHM_OFFSET]&FFTA_CHM_POTION_LOCK) ||
     half(unit+0x18)*2u>half(unit+0x1a))continue;
  unsigned item=362u+*preference;
  if(!ffta_native_free_count(item))continue;
  /* One request per empty-queue callback rechecks stock after every preceding
   * reaction. Scheduling is distinct from the consumption-only turn lock. */
  if(ffta_reaction_queue_append(frame,unit,unit,251u+*preference,136,item))
   ffta_action_claim(unit,AUTO_POTION_SCHEDULED);
  return;
 }
}
int ffta_chemist_reaction_consumption(unsigned item,unsigned amount,const uint8_t *object) {
 unsigned kind=ffta_action_reaction_kind();
 if(kind!=136 || amount!=1 || item!=ffta_action_reaction_value() ||
    !object || half(object+0x10)!=251u+(item==363))return ffta_native_lose_item(item,amount);
 uint8_t *unit=**(uint8_t ***)object;
 unsigned origin=ffta_job_origin(unit);
 if(!origin || origin>24 || (item!=362 && item!=363))return -1;
 unsigned before=ffta_native_free_count(item);
 int result=ffta_native_lose_item(item,1);
 if(before && ffta_native_free_count(item)+1==before) {
  uint8_t *state=ffta_job_state(unit);if(state)state[FFTA_JOB_CHM_OFFSET]|=FFTA_CHM_POTION_LOCK;
  ffta_action_claim(unit,FFTA_ACTION_CLAIM_AUTO_POTION);
 }
 return result;
}
uint8_t *ffta_chemist_inert_presentation(uint8_t *context) { return context; }
