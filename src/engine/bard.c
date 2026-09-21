#include "native-unit.h"
#include "bard.h"
#include "registry.h"
#include "job-state.h"
#include "action-snapshot.h"
#include "turn-supports.h"
#include "dancer.h"
#include "geomancer.h"
#include "mystic-knight.h"
#include "unit-query.h"
extern unsigned ffta_recuperation_numerator(const uint8_t *,const uint8_t *);
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static unsigned alive(const uint8_t *u){return u && half(u+0x18) && !(u[0xe8]&0x40u);}
static unsigned hostile(const uint8_t *a,const uint8_t *t){return ((a[0x29]>>7)^((a[0xeb]>>5)&1u))!=(t[0x29]>>7);}
/* Owned byte10 has two separate three-bit T2 timers, each with application
 * turn skip4. No actor identity or native spare status bit is inferred. */
unsigned ffta_bard_buff(const uint8_t *u,unsigned magic){
    uint8_t *s=ffta_job_state((uint8_t *)u);unsigned v=s?(s[10]>>(magic?3:0))&7u:0;
    return alive(u) && (v&3u) && (v&3u)<=2;
}
unsigned ffta_bard_snapshot_flags(const uint8_t *u){return (ffta_bard_buff(u,0)?FFTA_BARD_MARCH:0)|(ffta_bard_buff(u,1)?FFTA_BARD_INSPIRED:0);}
void ffta_bard_event(uint8_t *u,unsigned event){
    uint8_t *s=ffta_job_state(u);if(s && ((event>=2 && event<=5)||event==7))s[10]=0;
}
static unsigned tick(unsigned v){return (v&3u)>2?0:(v&4u)?v&3u:v?v-1:0;}
void ffta_bard_turn_end(uint8_t *u){
    uint8_t *s=ffta_job_state(u);if(s)s[10]=(uint8_t)(tick(s[10]&7u)|(tick((s[10]>>3)&7u)<<3));
}
unsigned ffta_bard_eligibility(const uint8_t *c){
    const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+4);unsigned id=half(c+12);
    if(!alive(a)||!alive(t)||(a[0xeb]&0x10u))return 0;
    if(id==FFTA_BRD_A6)return ffta_query_same_unit(c,a,t);
    if(a[0xeb]&8u)return 0; /* Native Silence27. */
    if(id==FFTA_BRD_A4)return hostile(a,t) && ffta_native_undead(t);
    if(hostile(a,t))return 0;
    if((id==FFTA_BRD_A1 || id==FFTA_BRD_A5) && ffta_native_undead(t))return 0;
    if(id==FFTA_BRD_A7 && a==t)return 0;
    return 1;
}
int ffta_bard_healing(const uint8_t *c){
    const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+4);unsigned id=half(c+12);
    if(!a||!alive(t)||ffta_native_undead(t))return 0;
    unsigned base=half(t+0x1a)*(id==FFTA_BRD_A1?40u:20u),cap=id==FFTA_BRD_A1?16000u:8000u;
    if(base>cap)base=cap;
    unsigned amount=base*ffta_recuperation_numerator(a,t)*ffta_bard_magick_numerator(a,id)/2000u;
    unsigned missing=half(t+0x1a)>half(t+0x18)?half(t+0x1a)-half(t+0x18):0;
    return (int)(amount<missing?amount:missing);
}
int ffta_bard_mp(const uint8_t *c){
    const uint8_t *a=*(const uint8_t *const *)c,*t=*(const uint8_t *const *)(c+4);
    if(!a||!alive(t)||a==t)return 0;
    unsigned mp=half(t+0x1c),maximum=half(t+0x1e),missing=maximum>mp?maximum-mp:0;
    return (int)(missing<20?missing:20);
}
uint8_t *ffta_bard_buff_apply(uint8_t *c){
    const uint8_t *a=*(const uint8_t *const *)c;uint8_t *t=*(uint8_t **)(c+8);
    if(!a||!alive(t)||hostile(a,t))return c;
    uint8_t *s=ffta_job_state(t);unsigned token=ffta_job_origin(t);
    if(!s||!token)return c;
    /* Prediction may write its explicit independent evaluated recipient.
     * A native preview that supplies the original source remains read-only. */
    uintptr_t original=token<=24?0x02000080u+(token-1)*264u:0x02002fc4u+(token-25)*264u;
    if((c[0x26]&0x10u) && (uintptr_t)t==original)return c;
    unsigned shift=half(c+12)==FFTA_BRD_A3?3:0;
    unsigned value=2u|(token==ffta_job_origin(a)?4u:0u);
    s[10]=(uint8_t)((s[10]&~(7u<<shift))|(value<<shift));
    return c;
}
unsigned ffta_bard_outgoing(const uint8_t *a,const uint8_t *t,unsigned action,unsigned physical){
    if(!a||!t||ffta_action_origin()==FFTA_ACTION_NATIVE_REACTION||ffta_action_origin()==FFTA_ACTION_EXPLICIT_COMBO)return 50;
    unsigned tf=ffta_action_unit_flags(t);
    /* Match the established HP-versus-MP interception contract. */
    if((tf&24u)==24u)return 50;
    if(!(tf&8u) && a!=t && action!=265 && ((unsigned (*)(const uint8_t *))0x0812e6a5u)(t)==13 &&
       ((unsigned (*)(const uint8_t *,unsigned))0x080c7ea5u)(t,0x15) &&
       (!action || !((unsigned (*)(unsigned,unsigned))0x080ccd51u)(action,17)))return 50;
    unsigned base=ffta_action_unit_extra_flags(a)&(physical?FFTA_BARD_MARCH:FFTA_BARD_INSPIRED)?6:5;
    return base*(physical?10:ffta_bard_magick_numerator(a,action));
}

/* A native status row assigns value even to an already present effect; its
 * multi-recipient scorer can also return positive100 for a beneficial song.
 * Give both consumers the same recipient-signed marginal benefit. These
 * modest planning weights do not change strength, targeting, cost or laws.
 * Requiem retains the native elemental damage/absorption forecast. */
static unsigned status(const uint8_t *u,unsigned bit){return (u[0xe8+bit/8]>>(bit%8))&1u;}
int ffta_bard_ai_value(int native,const uint8_t *a,const uint8_t *t,unsigned action){
    if(action<FFTA_BRD_A1 || action>FFTA_BRD_A8 || action==FFTA_BRD_A4)return native;
    /* Both callers already ran native admission. Do not allocate a second
     * pair of evaluated units inside the native placement search. Its
     * IWRAM stack is shared with the renderer's resident code. */
    if(!native || !alive(a)||!alive(t))return 0;
    int benefit=0;
    if(action==FFTA_BRD_A1 || action==FFTA_BRD_A5){
        /* Reuse execution's restorative magnitude, including missing HP,
         * Recuperation and Magick Boost, without a second full forecast. */
        uintptr_t c[4]={(uintptr_t)a,(uintptr_t)t,(uintptr_t)t,action};
        benefit=2*ffta_bard_healing((const uint8_t *)c);
    }
    if(action==FFTA_BRD_A1){
        static const uint8_t cures[4]={9,10,27,28};
        for(unsigned i=0;i<4;i++)if(status(t,cures[i]))benefit+=20;
    }
    if(action==FFTA_BRD_A2 || action==FFTA_BRD_A8)benefit+=status(t,25)?0:20;
    if(action==FFTA_BRD_A3 || action==FFTA_BRD_A8)benefit+=status(t,24)?0:20;
    if(action==FFTA_BRD_A5 || action==FFTA_BRD_A8)benefit+=status(t,3)?0:20;
    if(action==FFTA_BRD_A2)benefit+=ffta_bard_buff(t,0)?0:20;
    if(action==FFTA_BRD_A3)benefit+=ffta_bard_buff(t,1)?0:20;
    if(action==FFTA_BRD_A6)benefit+=status(t,12)?0:20;
    if(action==FFTA_BRD_A7){
        unsigned current=half(t+0x1c),maximum=half(t+0x1e);
        unsigned missing=maximum>current?maximum-current:0;
        benefit=(int)(missing<20?missing:20);
    }
    return -benefit;
}
void ffta_bard_ai_row(uint8_t *row,const uint8_t *a,const uint8_t *t,unsigned action){
    if(action<FFTA_BRD_A1 || action>FFTA_BRD_A8 || action==FFTA_BRD_A4 || !half(row+10))return;
    int value=ffta_bard_ai_value((int16_t)half(row+12),a,t,action);
    if(!value){for(unsigned i=4;i<20;i++)row[i]=0;return;}
    row[12]=(uint8_t)value;row[13]=(uint8_t)(value>>8);
    row[14]=row[12];row[15]=row[13];
}
extern void ffta_centered_event(uint8_t *,unsigned);
extern void ffta_centered_turn_end(uint8_t *);
#include "passing-step.h"
void ffta_bard_lifecycle_event(uint8_t *u,unsigned e){ffta_centered_event(u,e);ffta_bard_event(u,e);ffta_bard_passive_event(u,e);ffta_turn_event(u,e);ffta_dancer_event(u,e);ffta_passing_lifecycle(u,e);ffta_geo_event(u,e);ffta_myk_event(u,e);}
void ffta_bard_lifecycle_turn_end(uint8_t *u){ffta_centered_turn_end(u);ffta_bard_turn_end(u);ffta_bard_passive_turn_end(u);ffta_turn_end(u);ffta_dancer_turn_end(u);ffta_passing_turn_end(u);ffta_geo_turn_end(u);}
