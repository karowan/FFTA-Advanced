#include "dark-knight-state.h"
#include "action-snapshot.h"
/* Owned bytes0..2 only: LastResort remaining2 + application-turn skip4;
 * TBN source exact owner token1..36; TBNactive0/1; byte3 belongs to Dancer in schema2. */
static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }
static unsigned alive(const uint8_t *p) { return p && half(p+0x18) && !(p[0xe8]&0x40u); }
static unsigned hostile(const uint8_t *a,const uint8_t *t) {
    return a && t && a!=t && (((a[0x29]>>7)^((a[0xeb]>>5)&1u))!=(t[0x29]>>7));
}
unsigned ffta_drk_last_resort(const uint8_t *unit) {
    uint8_t *s=ffta_job_state((uint8_t *)unit);
    return s && s[0]<=6 && (s[0]&3u) && (s[0]&3u)<=2;
}
unsigned ffta_drk_tbn(const uint8_t *unit) {
    uint8_t *s=ffta_job_state((uint8_t *)unit);
    return s && s[2]==1 && s[1]>=1 && s[1]<=36;
}
unsigned ffta_drk_beneficial(const uint8_t *unit) { return ffta_drk_last_resort(unit)||ffta_drk_tbn(unit); }
void ffta_drk_grant_last_resort(uint8_t *unit,unsigned own_turn) {
    uint8_t *s=ffta_job_state(unit);
    if(s && alive(unit))s[0]=(uint8_t)(2u|(own_turn?4u:0u));
}
unsigned ffta_drk_grant_tbn(uint8_t *unit,const uint8_t *source) {
    uint8_t *s=ffta_job_state(unit);unsigned token=ffta_job_origin(source);
    if(!s || !alive(unit) || !alive(source) || !token || token>36 || hostile(source,unit))return 0;
    s[1]=(uint8_t)token;s[2]=1;return 1;
}
extern void ffta_drk_previous_centered_event(uint8_t *,unsigned);
extern void ffta_drk_previous_centered_turn_end(uint8_t *);
void ffta_drk_lifecycle_event(uint8_t *unit,unsigned event) {
    ffta_drk_previous_centered_event(unit,event);
    uint8_t *s=ffta_job_state(unit);if(!s)return;
    if((event>=2 && event<=5)||event==7) { s[0]=0;s[1]=0;s[2]=0; }
    /* Source turn start1 or either unit's KO/Petrify/job/battle lifecycle.
     * Missing peers in singleton queries are not evidence of expiration. */
    if(event>=1 && event<=5) {
        unsigned token=ffta_job_origin(unit);uint8_t *peers[36];
        unsigned count=ffta_job_peers(unit,peers,36);
        for(unsigned i=0;i<count;++i) {
            uint8_t *other=ffta_job_state(peers[i]);
            if(other && token && other[1]==token) { other[1]=0;other[2]=0; }
        }
    }
}
void ffta_drk_lifecycle_turn_end(uint8_t *unit) {
    ffta_drk_previous_centered_turn_end(unit);
    uint8_t *s=ffta_job_state(unit);if(!s)return;
    unsigned value=s[0];
    if(value>6 || (value&3u)>2)s[0]=0;
    else if(value&4u)s[0]=(uint8_t)(value&3u);
    else if(value)s[0]=(uint8_t)(value-1);
}
uint8_t *ffta_drk_last_resort_apply(uint8_t *context) {
    if(context && !(context[0x26]&0x10u))ffta_drk_grant_last_resort(*(uint8_t **)context,1);
    return context;
}
uint8_t *ffta_drk_tbn_apply(uint8_t *context) {
    if(context && !(context[0x26]&0x10u))
        ffta_drk_grant_tbn(*(uint8_t **)(context+8),*(const uint8_t *const *)context);
    return context;
}
