#include <stdint.h>
#include "registry.h"
#include "action-snapshot.h"
#include "job-state.h"
#include "dark-knight-state.h"
#include "viking-state.h"
#include "chemist-state.h"
#include "blade-wound.h"
#include "battle-state.h"
#include "execution-scope.h"
#include "reaction-ids.h"
#include "bard.h"
#include "turn-supports.h"
#include "dancer.h"
#include "passing-step.h"
#include "geomancer.h"
#include "mystic-knight.h"
#include "battle-workspace.h"
#include "custom-laws.h"
extern unsigned ffta_counter_draw_flags(const uint8_t *);
extern void ffta_counter_draw_hp_loss(uint8_t *,unsigned,unsigned);
extern void ffta_counter_draw_queue(unsigned *);
extern unsigned ffta_counter_draw_eligibility(const uint8_t *);
extern unsigned ffta_viking_reaction_eligibility(const uint8_t *);
extern void ffta_viking_reaction_queue(unsigned *);
extern int ffta_integrated_restoration_stage(int,const uint8_t *);

static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
/* Manager-owned bank; individual frames also require live stack tokens. */
void *ffta_integrated_result_storage(void){return ffta_battle_workspace(FFTA_WORKSPACE_RESULTS);}
extern unsigned ffta_primary_weapon(const uint8_t *);
extern unsigned ffta_drk_weapon_valid(unsigned,unsigned);
extern unsigned ffta_drk_snapshot_flags(const uint8_t *);
extern unsigned ffta_chemist_snapshot_flags(const uint8_t *);
extern unsigned ffta_chemist_beneficial(const uint8_t *);
extern unsigned ffta_drk_eligibility(const uint8_t *);
extern unsigned ffta_viking_physical_eligibility(const uint8_t *);
extern unsigned ffta_chemist_eligibility(const uint8_t *);
extern unsigned ffta_chemist_prevent_custom(const uint8_t *,unsigned);
extern void ffta_drk_action_event(const uint8_t *,unsigned,unsigned);
extern void ffta_viking_action_event(const uint8_t *,unsigned,unsigned);
extern void ffta_drk_hp_loss(uint8_t *,unsigned,unsigned);
extern void ffta_viking_hp_loss(uint8_t *,unsigned,unsigned);
extern void ffta_chemist_hp_loss(uint8_t *,unsigned,unsigned);
extern void ffta_drk_reaction_queue(unsigned *);
extern void ffta_chemist_reaction_queue(unsigned *);
extern unsigned ffta_viking_action_category(const uint8_t *,unsigned);

unsigned ffta_integrated_snapshot_flags(const uint8_t *u) {
    unsigned result=ffta_counter_draw_flags(u)|ffta_drk_snapshot_flags(u)|ffta_viking_snapshot_flags(u)|ffta_chemist_snapshot_flags(u);
    /* Existing Samurai/axe debuffs qualify an ally's later Opportunist hit.
     * Read only the explicit unit's owned record; action snapshots freeze
     * this tag before any rider can create or remove that status. */
    const uint8_t *exposed=ffta_owned_exposed((uint8_t *)u);
    if((exposed && (*exposed&1u)) ||
       ffta_wound_record_remaining(ffta_owned_wound((uint8_t *)u)))
        result|=FFTA_ACTION_FLAG_HARMFUL;
    if(ffta_dancer_debuff(u,0)||ffta_dancer_debuff(u,1)||ffta_geo_wisp(u))result|=FFTA_ACTION_FLAG_HARMFUL;
    return result|ffta_turn_snapshot_flags(u);
}
unsigned ffta_integrated_beneficial(const uint8_t *u) {
    return ffta_drk_beneficial(u)||ffta_viking_war_cry(u)||ffta_chemist_beneficial(u)||ffta_bard_snapshot_flags(u)||ffta_geo_updraft(u,0)||ffta_geo_updraft(u,1)||ffta_geo_steady(u)||ffta_myk_enchantment(u);
}
unsigned ffta_integrated_extra_snapshot_flags(const uint8_t *u){return ffta_bard_snapshot_flags(u)|ffta_bard_passive_flags(u)|ffta_turn_extra_flags(u)|ffta_dancer_flags(u)|ffta_geo_flags(u);}
/*445 is an internal formula template, never an executable queued action. */
unsigned ffta_integrated_action_limit(void){return 445;}
/* The live manager owns both banks; slots share exact live snapshot owners. */
void *ffta_integrated_snapshot_storage(void){return ffta_battle_workspace(FFTA_WORKSPACE_EXTRA);}
uint16_t *ffta_additional_extension_snapshot_storage(void){return ffta_battle_workspace(FFTA_WORKSPACE_EXTENSION);}
void ffta_integrated_action_event(const uint8_t *u,unsigned action,unsigned event) {
    if(!event){ffta_myk_doublecast_restore(u);ffta_myk_law_begin();}
    ffta_drk_action_event(u,action,event);
    ffta_viking_action_event(u,action,event);
    ffta_bard_action_event(u,action,event);
    ffta_dancer_action_event(u,action,event);
    ffta_passing_action_event(u,action,event);
    ffta_geo_action_event(u,action,event);
    ffta_myk_action_event(u,action,event);
}
void ffta_integrated_hp_loss(uint8_t *u,unsigned before,unsigned after) {
    ffta_drk_hp_loss(u,before,after);
    ffta_viking_hp_loss(u,before,after);
    ffta_chemist_hp_loss(u,before,after);
    ffta_counter_draw_hp_loss(u,before,after);
    ffta_bard_hp_loss(u,before,after);
    ffta_dancer_hp_loss(u,before,after);
    ffta_geo_hp_loss(u,before,after);
}
extern unsigned ffta_original_action_hp_apply(uint8_t *,int);
unsigned ffta_integrated_direct_hp_apply(uint8_t *unit,int delta) {
    unsigned before=half(unit+0x18);
    unsigned result=ffta_original_action_hp_apply(unit,delta);
    /* An actual successful direct HP write authenticates consumption even
     * when the eligible pre-barrier amount was rounded from one to zero.
     * Misses, previews, MP-only writes and displacement never reach here. */
    unsigned flags=ffta_action_unit_flags(unit);
    if(delta>=0 && before && ffta_action_origin()==FFTA_ACTION_NATIVE_PRIMARY &&
       (flags&(FFTA_DRK_TBN|FFTA_DRK_TBN_CONSUMING))==(FFTA_DRK_TBN|FFTA_DRK_TBN_CONSUMING))
        ffta_action_claim(unit,32u);
    ffta_action_barrier_candidate(unit,0);
    ffta_action_note_hp_loss(unit,before,half(unit+0x18));
    return result;
}
unsigned ffta_integrated_native_hp_apply(uint8_t *unit,int delta,unsigned caller) {
    /* Verified native result-row +1E application sites. The ordinary
     * descriptor path A315A uses the explicit direct helper above through
     * the composed Dark Sword/Samurai rider. A2CC8 and A3590 instead read
     * row+1C (displacement damage); A337E swaps HP/MP. None is another hit.
     * Unknown callers keep the exact native write without earning damage
     * claims. The LR comes directly from the installed assembly entry. */
    if(caller==0x080a2b8bu){
        unsigned before=half(unit+0x18);
        unsigned result=ffta_integrated_direct_hp_apply(unit,delta);
        ffta_myk_fight_after_hp(unit,before);
        return result;
    }
    if(caller==0x080a2607u || caller==0x080a3293u)
        return ffta_integrated_direct_hp_apply(unit,delta);
    return ffta_original_action_hp_apply(unit,delta);
}
void ffta_integrated_reaction_queue(unsigned *frame) {
    if(ffta_myk_doublecast_defer(frame))return;
    ffta_drk_reaction_queue(frame);
    ffta_counter_draw_queue(frame);
    ffta_viking_reaction_queue(frame);
    ffta_chemist_reaction_queue(frame);
    ffta_bard_queue(frame);
    ffta_dancer_queue(frame);
    ffta_geo_queue(frame);
}
const uint8_t *ffta_integrated_reaction_wrapper(const unsigned *frame,const uint8_t *unit) {
    return ffta_myk_doublecast_wrapper(frame,unit);
}
unsigned ffta_integrated_action_category(const uint8_t *u,unsigned action) {
    if(ffta_myk_action(action))return ffta_myk_strike(action)?FFTA_ACTION_PHYSICAL:FFTA_ACTION_MAGICAL;
    if(action>=FFTA_GEO_A1 && action<=FFTA_GEO_A9)return FFTA_ACTION_MAGICAL;
    if(action>=FFTA_DNC_A1 && action<=FFTA_DNC_A9)return ffta_dancer_physical(action)?FFTA_ACTION_PHYSICAL:0;
    if(action>=FFTA_BRD_A1 && action<=FFTA_BRD_A8)return action==FFTA_BRD_A6?0:FFTA_ACTION_MAGICAL;
    return ffta_viking_action_category(u,action);
}
unsigned ffta_integrated_weapon_valid(unsigned action,unsigned item) {
    if(ffta_myk_action(action))return ffta_myk_weapon(item);
    if(action==FFTA_COUNTER_DRAW_ACTION)return item && ((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(item,3)==9;
    if(action==FFTA_VIK_A3 || action==FFTA_VIK_A6)
        return item && ((unsigned (*)(unsigned,unsigned))0x080ca7a5u)(item,3)==31;
    return ffta_drk_weapon_valid(action,item);
}
unsigned ffta_integrated_eligibility(const uint8_t *context) {
    unsigned action=half(context+12);
    if(ffta_myk_action(action))return ffta_myk_eligibility(context);
    if(action>=FFTA_GEO_A1 && action<=FFTA_GEO_A9)return ffta_geo_field_eligibility(context);
    if(action==FFTA_GEO_STONE_ACTION||action==FFTA_GEO_WRATH_ACTION)return ffta_geo_reaction_eligibility(context);
    if(action==FFTA_DNC_FURY_ACTION||action==FFTA_DNC_RHYTHM_ACTION)return ffta_dancer_reaction_eligibility(context);
    if(action>=FFTA_DNC_A1 && action<=FFTA_DNC_A9)return ffta_dancer_eligibility(context);
    if(action>=FFTA_BARD_ENCOURAGE_ACTION && action<=FFTA_BARD_ENCORE_ACTION)return ffta_bard_reaction_eligibility(context);
    if(action>=FFTA_BRD_A1 && action<=FFTA_BRD_A8)return ffta_bard_eligibility(context);
    if(action==FFTA_COUNTER_DRAW_ACTION)return ffta_counter_draw_eligibility(context);
    if(action==FFTA_ABSORB_ACTION || action==FFTA_GIL_SNAPPER_ACTION)return ffta_viking_reaction_eligibility(context);
    if(action>=FFTA_CHM_A1 && action<=FFTA_CHM_A10)return ffta_chemist_eligibility(context);
    if(action>=FFTA_VIK_A1 && action<=FFTA_VIK_A9)return ffta_viking_physical_eligibility(context);
    return ffta_drk_eligibility(context);
}

extern unsigned ffta_exposed_native_physical(const uint8_t *);
extern unsigned ffta_exposed_incoming_numerator(int,const uint8_t *);
extern unsigned ffta_drk_outgoing_numerator(const uint8_t *,const uint8_t *,unsigned,unsigned);
extern unsigned ffta_drk_incoming_numerator(const uint8_t *,const uint8_t *,unsigned,unsigned);
extern unsigned ffta_drk_incoming_effects(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned);
unsigned ffta_integrated_incoming_numerator(const uint8_t *a,const uint8_t *t,unsigned id,unsigned physical){
    if(id!=FFTA_MYK_A12)return ffta_drk_incoming_numerator(a,t,id,physical);
    unsigned retained=ffta_myk_incoming_flags(a,t,id,~0u);
    return ffta_drk_incoming_effects(a,t,id,physical,~retained);
}
extern unsigned ffta_viking_outgoing_numerator(const uint8_t *,const uint8_t *,unsigned);
void ffta_integrated_barrier_candidate(const uint8_t *actor,const uint8_t *target,unsigned action,unsigned pre_barrier) {
    if(ffta_action_phase()!=FFTA_ACTION_RESULT || ffta_action_id()!=action)return;
    const uint8_t *context=(const uint8_t *)0x0200f3f0u;
    if(action && (half(context+12)!=action || (context[0x26]&0x10u)))return;
    /* Shatter Guard's physical-rider helper explicitly makes and retires a
     * private defender with Protect removed. Commit belongs to the original
     * recipient supplied by that same native effect context, not the retired
     * copy. This is a direct context relationship, never a roster lookup. */
    const uint8_t *evaluated_target=target;
    if((action==FFTA_SLD_AX_A4 || action==FFTA_MYK_A12) && *(const uint8_t *const *)context==actor)
        target=*(const uint8_t *const *)(context+4);
    unsigned a=ffta_action_unit_flags(actor),t=ffta_action_unit_flags(target);
    if(action==FFTA_MYK_A12)t=ffta_myk_incoming_flags(actor,evaluated_target,action,t);
    unsigned eligible=actor && target && actor!=target && !(t&4u) &&
        (((a>>7)^(a>>8))&1u)!=((t>>7)&1u) && (t&FFTA_DRK_TBN) &&
        !((t&8u) && (t&16u)) && pre_barrier;
    ffta_action_barrier_candidate(target,eligible);
}
static unsigned custom_physical(unsigned action) {
    return ffta_myk_strike(action) || ffta_dancer_physical(action) || (action>=347 && action<=358) || action==360 || action==361 || action==362 || action==363 ||
        action==FFTA_VIK_A3 || action==FFTA_VIK_A6 || action==FFTA_COUNTER_DRAW_ACTION || (action>=424 && action<=431);
}
unsigned ffta_integrated_direct_kind(const uint8_t *context) {
    if(!context)return 0;
    unsigned action=half(context+12);
    const uint8_t *d=*(const uint8_t *const *)(context+0x30);
    if(!d || d[1]>=93 || ((const uint8_t *)0x083a87b0u)[d[1]*12u+4]!=1)return 0;
    if(custom_physical(action) && (d[3]==30 || d[3]==39 || d[3]==43))return 1;
    if(ffta_exposed_native_physical(context))return 1;
    return ((unsigned (*)(unsigned,unsigned))0x080ccd51u)(action,28) &&
        (d[3]==30 || d[3]==39 || d[3]==43)?2:0;
}
static int physical(int damage,const uint8_t *actor,const uint8_t *target,unsigned action,unsigned *deferred_barrier) {
    if(damage<=0) {
        if(deferred_barrier)*deferred_barrier=0;
        else ffta_integrated_barrier_candidate(actor,target,action,0);
        return damage;
    }
    uint64_t result=(uint64_t)(unsigned)damage*ffta_exposed_incoming_numerator(damage,target)*
        ffta_poise_hp_factor(actor,target,action)*ffta_blade_ward_factor(actor,target)*
        ffta_drk_outgoing_numerator(actor,target,action,1)*ffta_integrated_incoming_numerator(actor,target,action,1)*
        ffta_viking_outgoing_numerator(actor,target,action)*ffta_bard_outgoing(actor,target,action,1)*ffta_turn_damage_numerator(actor,target,action,1);
    unsigned pre_barrier=(unsigned)ffta_dancer_scaled(result*2u,128000000000ULL,actor,target,action,1);
    if(deferred_barrier)*deferred_barrier=pre_barrier;
    else ffta_integrated_barrier_candidate(actor,target,action,pre_barrier);
    result=ffta_dancer_scaled(result,128000000000ULL,actor,target,action,1);
    return result>999u?999:(int)result;
}
int ffta_integrated_exposed_native_stage(int damage,const uint8_t *context) {
    if(!context)return damage;
    if(damage<0)return ffta_integrated_restoration_stage(damage,context);
    unsigned action=half(context+12);
    if(custom_physical(action))return damage; /* Already one complete rational finalizer. */
    const uint8_t *actor=*(const uint8_t *const *)context;
    const uint8_t *target=*(const uint8_t *const *)(context+8);
    if(damage<=0) { ffta_integrated_barrier_candidate(actor,target,action,0);return damage; }
    unsigned kind=ffta_integrated_direct_kind(context);
    if(kind==1)return physical(damage,actor,target,action,0);
    if(kind!=2) { ffta_integrated_barrier_candidate(actor,target,action,0);return damage; }
    uint64_t product=(uint64_t)(unsigned)damage*ffta_poise_hp_factor(actor,target,action)*
        ffta_drk_outgoing_numerator(actor,target,action,0)*ffta_integrated_incoming_numerator(actor,target,action,0)*
        ffta_viking_outgoing_numerator(actor,target,action)*ffta_bard_outgoing(actor,target,action,0)*ffta_turn_damage_numerator(actor,target,action,0);
    ffta_integrated_barrier_candidate(actor,target,action,(unsigned)ffta_dancer_scaled(product*2u,1280000000u,actor,target,action,0));
    return (int)ffta_dancer_scaled(product,1280000000u,actor,target,action,0);
}
extern int ffta_integrated_original_exposed_preview(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned,unsigned);
/* Effect forecasts own two evaluated units. Borrow an existing authenticated
 * result-bank snapshot so their nested formula cannot overwrite IWRAM code. */
static int bank_preview(const uint8_t *actor,const uint8_t *target,unsigned action,unsigned item,unsigned index,unsigned minimum,unsigned menu){
    typedef struct { uintptr_t *token;FFTA_ActionSnapshot frame; } Storage;
    _Static_assert(sizeof(Storage)==824,"Fight query snapshot bank stride");
    extern void *ffta_battle_workspace(unsigned);
    extern unsigned ffta_additional_workspace_prepare(void);
    if(!ffta_additional_workspace_prepare())return 0;
    Storage *bank=ffta_battle_workspace(0x10u);
    if(bank)for(unsigned i=0;i<8;i++)if(!bank[i].token && !bank[i].frame.magic){
        FFTA_ActionSnapshot *snapshot=&bank[i].frame;
        uintptr_t token=(uintptr_t)snapshot;bank[i].token=&token;
        unsigned opened=ffta_snapshot_begin(snapshot,actor,target,0);
        int damage=ffta_integrated_original_exposed_preview(actor,target,action,item,index,2);
        if(action)damage=ffta_myk_shell_preview(damage,actor,target,action,item,index,2,menu);
        /* Native130072..13009A varies ordinary damage by +/-floor(n/10),
         * before expansion factors. Status-law possibility uses the lower
         * positive bound, never average damage as proof of certain death.
         * A native cap can make this conservative, which is safe for a warning. */
        if(minimum && damage>0)damage-=damage/10;
        unsigned ignored_barrier=0;
        if(!action)damage=physical(damage,actor,target,0,&ignored_barrier);
        if(opened)ffta_snapshot_end(snapshot);
        else for(unsigned j=0;j<sizeof(*snapshot);j++)((uint8_t *)snapshot)[j]=0;
        bank[i].token=0;return damage;
    }
    return 0;
}
int ffta_integrated_fight_effect_preview(const uint8_t *actor,const uint8_t *target,unsigned item,unsigned index,unsigned minimum){
    return bank_preview(actor,target,0,item,index,minimum,0);
}
int ffta_integrated_mystic_effect_preview(const uint8_t *actor,const uint8_t *target,unsigned action,unsigned item,unsigned index){
    return bank_preview(actor,target,action,item,index,0,0);
}
int ffta_integrated_magic_menu_preview(const uint8_t *actor,const uint8_t *target,unsigned action,unsigned item,unsigned index){
    return bank_preview(actor,target,action,item,index,0,1);
}
int ffta_integrated_exposed_preview(const uint8_t *actor,const uint8_t *target,unsigned action,
    unsigned item,unsigned index,unsigned mode) {
    /* Real Fight resolution can nest below native copied units too. Its old
     * 820-byte local snapshot left no room for the native audio interrupt and
     * overwrote resident renderer code. Use the same eight owned bank slots
     * as other forecasts, retaining this path's deferred barrier publication. */
    typedef struct { uintptr_t *token;FFTA_ActionSnapshot frame; } Storage;
    _Static_assert(sizeof(Storage)==824,"Result forecast bank stride");
    extern unsigned ffta_additional_workspace_prepare(void);
    if(!ffta_additional_workspace_prepare())return 0;
    Storage *bank=ffta_battle_workspace(0x10u);
    if(bank)for(unsigned i=0;i<8;i++)if(!bank[i].token && !bank[i].frame.magic){
        FFTA_ActionSnapshot *snapshot=&bank[i].frame;
        uintptr_t token=(uintptr_t)snapshot;bank[i].token=&token;
        unsigned opened=ffta_snapshot_begin(snapshot,actor,target,0);
        int damage=ffta_integrated_original_exposed_preview(actor,target,action,item,index,mode);
        if(action && mode==2)damage=ffta_myk_shell_preview(damage,actor,target,action,item,index,mode,0);
        unsigned pre_barrier=0;
        if((uint16_t)action==0)damage=physical(damage,actor,target,(uint16_t)action,&pre_barrier);
        if(opened)ffta_snapshot_end(snapshot);
        bank[i].token=0;
        /* Publish only to the enclosing real result after retiring the query. */
        if((uint16_t)action==0)ffta_integrated_barrier_candidate(actor,target,0,pre_barrier);
        return damage;
    }
    return 0;
}

extern unsigned ffta_wound_status_icon(const uint8_t *,unsigned);
extern unsigned ffta_wound_status_next_key(const uint8_t *,unsigned);
extern unsigned ffta_wound_status_visual(uint8_t *,unsigned);
extern unsigned ffta_drk_status_visual(uint8_t *,unsigned);
extern unsigned ffta_viking_status_visual(uint8_t *,unsigned);
extern unsigned ffta_chemist_status_visual(uint8_t *,unsigned);
unsigned ffta_integrated_status_icon(const uint8_t *u,unsigned key) {
    key=(uint16_t)key;
    if(key>=43 && key<=55)return ffta_myk_status_icon(u,key);
    if(key==39)return ffta_geo_updraft(u,0)||ffta_geo_updraft(u,1)?39:0;
    if(key==40)return ffta_geo_field_kind(u)?40:0;
    if(key==41)return ffta_geo_wisp(u)?41:0;
    if(key==42)return ffta_geo_steady(u)?42:0;
    if(key==28)return ffta_drk_last_resort(u)?28:0;
    if(key==29)return ffta_drk_tbn(u)?29:0;
    if(key==30)return ffta_inoculated_active(u)?30:0;
    if(key==31)return ffta_viking_war_cry(u)?31:0;
    if(key==32)return ffta_viking_challenger(u)?32:0;
    if(key==33 || key==34)return ffta_bard_buff(u,key==34)?key:0;
    if(key==36||key==37)return ffta_dancer_debuff(u,key==37)?key:0;
    if(key==38)return (ffta_dancer_flags(u)&FFTA_DNC_CHARGED)?38:0;
    if(key==35)return (ffta_bard_passive_flags(u)&FFTA_BARD_CHARGED)?35:0;
    return key<=27?ffta_wound_status_icon(u,key):0;
}
unsigned ffta_integrated_status_next_key(const uint8_t *u,unsigned previous) {
    unsigned next=(uint8_t)(previous+1);
    /* Every status list includes native keys1..24. Below that boundary no
     * status lookup can affect the next key. Preserve native signed wrap. */
    if((int8_t)next<=24)return next;
    unsigned sequence=ffta_myk_sequence(u),blade=ffta_myk_enchantment(u);
    unsigned limit=sequence==2?55:sequence==1?54:blade?42+blade:42;
    while(limit>27 && !ffta_integrated_status_icon(u,limit))--limit;
    if(limit==27)return ffta_wound_status_next_key(u,previous);
    return (int8_t)next>(int)limit?1:next;
}
unsigned ffta_integrated_status_visual(uint8_t *sprite,unsigned icon) {
    if(icon>=43 && icon<=55)return ffta_myk_status_visual(sprite,icon);
    if(icon>=39&&icon<=42)return ffta_geo_status_visual(sprite,icon);
    if(icon==28 || icon==29)return ffta_drk_status_visual(sprite,icon);
    if(icon==30)return ffta_chemist_status_visual(sprite,icon);
    if(icon==31 || icon==32)return ffta_viking_status_visual(sprite,icon);
    if(icon>=36 && icon<=38)return ffta_dancer_status_visual(sprite,icon);
    if(icon>=33 && icon<=35)return ffta_bard_status_visual(sprite,icon);
    return icon<=27?ffta_wound_status_visual(sprite,icon):0;
}

uint8_t *ffta_integrated_challenged_apply(uint8_t *context) {
    if(!context)return context;
    uint8_t *target=*(uint8_t **)(context+8);
    const uint8_t *actor=*(const uint8_t *const *)context;
    if(!actor || !target || actor==target || !half(target+0x18) || (target[0xe8]&0x40u) ||
       (((actor[0x29]>>7)^((actor[0xeb]>>5)&1u))==(target[0x29]>>7)) ||
       ((unsigned (*)(const uint8_t *))0x080cd50du)(target)==11)return context;
    if(ffta_chemist_prevent_custom(context,2))return context;
    if(!(context[0x26]&0x10u) && ffta_viking_grant_challenge(target,actor))ffta_custom_law_applied(target);
    return context;
}
void ffta_integrated_higanbana_commit(uint8_t *target,unsigned before,uint8_t *object,uint8_t *row) {
    if(!target || !object || half(object+0x10)!=FFTA_SAM_A9)return;
    int reference=0;
    if(!ffta_execution_take(object,row,target,&reference))return;
    unsigned after=half(target+0x18);
    if(before<=after)return;
    uint8_t *record=ffta_owned_wound(target);
    if(!after) { ffta_wound_record_clear(record);return; }
    if((target[0xe8]&0x40u) || ((unsigned (*)(const uint8_t *))0x080cd50du)(target)==11)return;
    /* Exact active result scope supplies the actor. Do not reconstruct it
     * from a roster identity or infer an ailment attempt from current state. */
    uint8_t context[0x34]={0};
    *(const uint8_t **)context=ffta_action_actor();
    *(uint8_t **)(context+4)=target;*(uint8_t **)(context+8)=target;
    context[12]=(uint8_t)FFTA_SAM_A9;context[13]=(uint8_t)(FFTA_SAM_A9>>8);
    if(ffta_chemist_prevent_custom(context,1))return;
    if(ffta_wound_record_replace(record,reference))ffta_custom_law_applied(target);
}
