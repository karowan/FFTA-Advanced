#include "mystic-knight.h"
#include "job-state.h"
#include "samurai-state.h"
#include "dark-knight-state.h"
#include "viking-state.h"
#include "chemist-state.h"
#include "bard.h"
#include "dancer.h"
#include "geomancer.h"

static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static unsigned alive(const uint8_t *u){return u && half(u+0x18) && !(u[0xe8]&64u);}
/* This is the intersection of persistent beneficial native statuses and the
 * real Dispel removal mask, not every bit that Dispel happens to remove.
 * Stable IDs travel with the action; an expired choice never selects another.
 * Custom choices own individual fields, never the broad Dispel lifecycle. */
static const uint8_t native_statuses[8]={2,3,4,5,12,21,24,25};
unsigned ffta_myk_dispel_native(unsigned choice){
 return choice>=1 && choice<=8?native_statuses[choice-1]:255;
}
unsigned ffta_myk_dispellable(const uint8_t *u,unsigned choice){
 if(!alive(u))return 0;
 if(choice>=1 && choice<=8){
  unsigned bit=native_statuses[choice-1];
  return !!(u[0xe8+bit/8]&(1u<<(bit%8))) &&
   ((unsigned (*)(unsigned,unsigned,unsigned))0x081339a9u)(53,bit,1);
 }
 switch(choice){
 case 9:return ffta_centered_active(u);
 case 10:return ffta_drk_last_resort(u);
 case 11:return ffta_drk_tbn(u);
 case 12:return ffta_viking_war_cry(u);
 case 13:return ffta_inoculated_active(u);
 case 14:return ffta_bard_buff(u,0);
 case 15:return ffta_bard_buff(u,1);
 case 16:return !!(ffta_bard_passive_flags(u)&FFTA_BARD_CHARGED);
 case 17:return !!(ffta_dancer_flags(u)&FFTA_DNC_CHARGED);
 case 18:return ffta_geo_updraft(u,0);
 case 19:return ffta_geo_updraft(u,1);
 case 20:return ffta_geo_steady(u);
 case 21:return !!ffta_myk_enchantment(u);
 default:return 0;
 }
}
unsigned ffta_myk_dispel(uint8_t *u,unsigned choice){
 if(!ffta_myk_dispellable(u,choice))return 0;
 if(choice<=8){
  ((void (*)(uint8_t *,unsigned,unsigned))0x080cd885u)(u,native_statuses[choice-1],0);
  ((void (*)(uint8_t *))0x08131c59u)(u);
  ((void (*)(uint8_t *))0x080ca2e9u)(u);
  return 1;
 }
 if(choice==9){ffta_centered_clear(u);return 1;}
 if(choice==21){ffta_myk_clear(u);return 1;}
 uint8_t *s=ffta_job_state(u);if(!s)return 0;
 switch(choice){
 case 10:s[0]=0;break;
 case 11:s[1]=s[2]=0;break;
 case 12:s[4]=0;break;
 case 13:ffta_chemist_event(u,7);break;
 case 14:s[10]&=248u;break;
 case 15:s[10]&=199u;break;
 case 16:s[11]&=252u;break;
 case 17:s[FFTA_JOB_DNC_FLAGS]&=63u;break;
 case 18:s[FFTA_JOB_GEO_TRAVERSAL]&=241u;ffta_geo_mobility(u);break;
 case 19:s[FFTA_JOB_GEO_TRAVERSAL]&=143u;ffta_geo_mobility(u);break;
 case 20:s[FFTA_JOB_GEO_STEADY]&=248u;break;
 default:return 0;
 }
 return 1;
}
/* Spellbreak removes one random buff the target actually has. The native RNG
 * (2804) is drawn only when a hit resolves, never by previews or admission. */
unsigned ffta_myk_dispel_random(uint8_t *u){
 uint8_t present[FFTA_MYK_DISPEL_CHOICES];unsigned count=0;
 for(unsigned choice=1;choice<=FFTA_MYK_DISPEL_CHOICES;choice++)
  if(ffta_myk_dispellable(u,choice))present[count++]=(uint8_t)choice;
 if(!count)return 0;
 /* 2804 returns bits16..30 of its state: 0..32767. */
 unsigned roll=((unsigned (*)(void))0x08002805u)()&0x7fffu;
 unsigned choice=present[(roll*count)>>15];
 return ffta_myk_dispel(u,choice)?choice:0;
}
/* Choice admission is read-only and uses only the supplied owner's complete
 * cohort. A copied forecast must never inspect or mutate live opponents. */
unsigned ffta_myk_dispel_available(const uint8_t *a,unsigned choice){
 if(!alive(a)||choice>FFTA_MYK_DISPEL_CHOICES)return 0;
 uint8_t *peers[FFTA_JOB_UNIT_COUNT];
 unsigned count=ffta_job_peers((uint8_t *)a,peers,FFTA_JOB_UNIT_COUNT);
 for(unsigned i=0;i<count;i++){
  const uint8_t *t=peers[i];
  if(t==a || (((a[0x29]>>7)^((a[0xeb]>>5)&1u))==(t[0x29]>>7)))continue;
  if(choice){if(ffta_myk_dispellable(t,choice))return 1;}
  else for(unsigned j=1;j<=FFTA_MYK_DISPEL_CHOICES;j++)if(ffta_myk_dispellable(t,j))return 1;
 }
 return 0;
}
