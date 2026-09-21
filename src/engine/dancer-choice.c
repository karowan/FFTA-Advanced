#include <stdint.h>
#include "registry.h"
#include "geomancer.h"
#include "mystic-knight.h"
#include "medicine-ai.h"
#include "dancer-choice-labels.h"

extern void ffta_chemist_menu(uint8_t *,uint8_t *);
extern void ffta_chemist_restricted_menu(uint8_t *,uint8_t *);
extern const uint8_t *ffta_chemist_menu_name(const uint8_t *,unsigned);
extern unsigned ffta_chemist_menu_selected(const uint8_t *,unsigned,unsigned);
extern void ffta_chemist_context(uint8_t *,unsigned,unsigned,unsigned);
extern unsigned ffta_ai_preview_choice(const uint8_t *,unsigned);
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}

/* The extra halfword is an explicit cast choice, never persistent unit state.
 * Zero/unknown choices remain inert; neither preview nor a target rerolls it. */
static const uint8_t vectors[5][4]={
    {1,1,1,1},{87,1,1,1},{111,1,1,1},{125,1,1,1},{95,1,1,1}
};
unsigned ffta_dancer_preview_choice(const uint8_t *actor,unsigned action,unsigned primary){
    if(action==FFTA_CHM_A2 || action==FFTA_CHM_A4){
        unsigned ai=ffta_ai_preview_choice(actor,action);if(ai)return ai;
        /* Ordinary item forecasts already carry their explicit operand. */
        if(ffta_medicine_choice_valid(action,primary))return primary;
        const uint8_t *m=*(const uint8_t *const *)0x0200f438u;
        if(m && m[4]>=6 && m[4]<=11 && *(const uint8_t *const *)(m+24)==actor &&
           *(const uint32_t *)(m+20)==action && ffta_medicine_choice_valid(action,half(m+16)))return half(m+16);
        return 0;
    }
    if((uint16_t)action!=FFTA_DNC_A6 && action!=FFTA_GEO_A3 && action!=FFTA_GEO_A8 && action!=FFTA_MYK_A12)return primary;
    unsigned ai=ffta_ai_preview_choice(actor,action);if(ai)return ai;
    const uint8_t *manager=*(const uint8_t *const *)0x0200f438u;
    /* B4CF0 validates a native target using the weapon operand. Only the
     * exact active player-selection owner may supply this omitted value.
     * Copied/AI queries must obtain their own explicit choice transport. */
    if(!manager || manager[4]<6 || manager[4]>11 ||
       *(const uint8_t *const *)(manager+24)!=actor ||
       *(const uint32_t *)(manager+20)!=action)return action==FFTA_DNC_A6 || action==FFTA_MYK_A12?0:primary;
    unsigned choice=half(manager+16);
    if(action==FFTA_MYK_A12)return choice>=1 && choice<=FFTA_MYK_DISPEL_CHOICES?choice:0;
    return action==FFTA_GEO_A8?(ffta_geo_element(actor,action,choice)?choice:0):choice>=1 && choice<=4?choice:0;
}
void ffta_dancer_context(uint8_t *context,unsigned action,unsigned selected,unsigned flags){
    ffta_chemist_context(context,action,selected,flags);
    if((uint16_t)action!=FFTA_DNC_A6)return;
    unsigned choice=(uint16_t)selected;
    const uint8_t *vector=vectors[choice<=4?choice:0];
    *(const uint8_t **)(context+0x2c)=vector;
    /* Constructor initializes both fields. A vector-only replacement leaves
     * its first descriptor stale for consumers before the next stage call. */
    const uint8_t *descriptors=*(const uint8_t *const *)0x0812f2a0u;
    *(const uint8_t **)(context+0x30)=descriptors+4*vector[0];
}
static const uint8_t *actor(void){
 const uint8_t *m=*(const uint8_t *const *)0x0200f438u;
 return m?*(const uint8_t *const *)(m+24):0;
}
static unsigned options(unsigned action,uint8_t *out){
 if(action==FFTA_MYK_A12){for(unsigned i=0;i<FFTA_MYK_DISPEL_CHOICES;i++)out[i]=(uint8_t)(i+1);return FFTA_MYK_DISPEL_CHOICES;}
 if(action==FFTA_DNC_A6){for(unsigned i=0;i<4;i++)out[i]=(uint8_t)(i+1);return 4;}
 return ffta_geo_choices(actor(),action,out);
}
static const uint8_t *label(unsigned action,unsigned choice){
 if(action==FFTA_MYK_A12 && choice>=1 && choice<=FFTA_MYK_DISPEL_CHOICES)return ffta_mystic_choice_labels[choice-1];
 if(action==FFTA_DNC_A6 && choice>=1 && choice<=4)return ffta_dancer_choice_labels[choice-1];
 if(action==FFTA_GEO_A3 && choice>=1 && choice<=4)return ffta_geomancer_choice_labels[choice-1];
 if(action==FFTA_GEO_A8 && choice>=1 && choice<=5)return ffta_geomancer_choice_labels[choice+3];
 return 0;
}
static unsigned choice_row(const uint8_t *menu,unsigned row,unsigned *action){
 const uint8_t *manager=*(const uint8_t *const *)0x0200f438u;
 if(!manager || manager[4]<6 || manager[4]>8 || menu[10]>=24 || row>=half(menu+0x84))return 0;
 const uint8_t *const *banks=*(const uint8_t *const *const *)0x080257e8u;
 const uint32_t *rows=*(const uint32_t *const *)(menu+0x94);
 *action=half(banks[menu[10]]+rows[row]*8+4);
 uint8_t values[FFTA_MYK_DISPEL_CHOICES];unsigned count=options(*action,values),ordinal=0;
 if(!count)return 0;
 for(unsigned i=0;i<row;i++)if(rows[i]==rows[row])ordinal++;
 return ordinal<count?values[ordinal]:0;
}
static void expand(uint8_t *menu,uint8_t *descriptor){
 unsigned count=descriptor[9],extra=0;uint8_t values[FFTA_MYK_DISPEL_CHOICES];
 uint32_t *rows=*(uint32_t **)(menu+0x94);uint8_t *flags=*(uint8_t **)(menu+0x98);
 const uint8_t *bank=*(const uint8_t *const *)descriptor;
 for(unsigned i=0;i<count;i++){unsigned n=options(half(bank+rows[i]*8+4),values);if(n)extra+=n-1;}
 /* Native command descriptor3 allocates42 rows before either constructor.
  * Its exact allocation and cleanup remain native; no pointer replacement. */
 if(count+extra>42)return;
 unsigned end=count+extra;descriptor[9]=(uint8_t)end;
 for(unsigned i=count;i>0;i--){
  unsigned lesson=rows[i-1],enabled=flags[i-1],action=half(bank+lesson*8+4),copies=options(action,values);
  for(unsigned j=0;j<copies;j++){
   unsigned width=((unsigned (*)(const uint8_t *))0x080161bdu)(label(action,values[j]));
   if(width>descriptor[7])descriptor[7]=(uint8_t)width;
  }
  if(!copies)copies=1;
  while(copies--){unsigned dst=--end;rows[dst]=lesson;flags[dst]=(uint8_t)(enabled &&
   (action!=FFTA_MYK_A12 || ffta_myk_dispel_available(actor(),copies+1)));}
 }
}
void ffta_dancer_menu(uint8_t *menu,uint8_t *descriptor){ffta_chemist_menu(menu,descriptor);expand(menu,descriptor);}
void ffta_dancer_restricted_menu(uint8_t *menu,uint8_t *descriptor){ffta_chemist_restricted_menu(menu,descriptor);expand(menu,descriptor);}
const uint8_t *ffta_dancer_menu_name(const uint8_t *menu,unsigned row){
 unsigned action=0,choice=choice_row(menu,(uint16_t)row,&action);
 return choice?label(action,choice):ffta_chemist_menu_name(menu,row);
}
unsigned ffta_dancer_menu_selected(const uint8_t *menu,unsigned row,unsigned action){
 unsigned result=ffta_chemist_menu_selected(menu,row,action),selected_action=0;
 unsigned choice=choice_row(menu,row,&selected_action);
 if(choice && selected_action==action){
  uint8_t *manager=*(uint8_t **)0x0200f438u;
  if(manager){manager[16]=(uint8_t)choice;manager[17]=0;}
 }
 return result;
}
