#include <stdint.h>
#include "chemist-items.h"
#include "chemist-menu-labels.h"
static unsigned half(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
extern unsigned ffta_native_free_count(unsigned);
extern void ffta_original_chemist_menu(uint8_t *,uint8_t *);
extern void ffta_original_chemist_restricted_menu(uint8_t *,uint8_t *);
extern const uint8_t *ffta_original_chemist_menu_name(const uint8_t *,unsigned);
static unsigned choices(unsigned a){return a==384?4:a==386?2:1;}
static unsigned ingredient(unsigned a,unsigned ordinal){
 static const uint16_t cures[4]={367,368,369,371},tonics[2]={363,364};
 return a==384 && ordinal<4?cures[ordinal]:a==386 && ordinal<2?tonics[ordinal]:0;
}
static unsigned row_action(const uint8_t *menu,unsigned row){
 const uint8_t *manager=*(const uint8_t *const *)0x0200f438;
 if(!manager || manager[4]<6 || manager[4]>8 || row>=half(menu+0x84))return 0;
 const uint8_t *const *banks=*(const uint8_t *const *const *)0x080257e8;
 if(menu[10]>=24)return 0;
 const uint32_t *rows=*(const uint32_t *const *)(menu+0x94);
 return half(banks[menu[10]]+rows[row]*8+4);
}
static unsigned row_choice(const uint8_t *menu,unsigned row,unsigned action){
    if(action!=384 && action!=386)return 0;
 const uint32_t *rows=*(const uint32_t *const *)(menu+0x94);unsigned ordinal=0;
 for(unsigned i=0;i<row;i++)if(rows[i]==rows[row])ordinal++;
 return ingredient(action,ordinal);
}
static void expand(uint8_t *menu,uint8_t *descriptor){
 unsigned count=descriptor[9],extra=0;uint32_t *rows=*(uint32_t **)(menu+0x94);uint8_t *flags=*(uint8_t **)(menu+0x98);
 const uint8_t *bank=*(const uint8_t *const *)descriptor;
 for(unsigned i=0;i<count;i++)extra+=choices(half(bank+rows[i]*8+4))-1;
 if(count+extra>22)return; /* native single-command allocation */
 unsigned end=count+extra;descriptor[9]=(uint8_t)end;
 for(unsigned i=count;i>0;i--){
  unsigned lesson=rows[i-1],action=half(bank+lesson*8+4),copies=choices(action),enabled=flags[i-1];
  for(unsigned j=copies;j>0;j--){unsigned dst=--end,item=ingredient(action,j-1);rows[dst]=lesson;flags[dst]=(uint8_t)(enabled && (item?ffta_native_free_count(item):!ffta_chemist_action(action) || ffta_chemist_stocked(action,0)));}
 }
 /* Native constructor computes the window from this pixel width. */
 for(unsigned i=0;extra && i<6;i++){
  unsigned width=((unsigned (*)(const uint8_t *))0x080161bdu)(ffta_chemist_choice_labels[i]);
  if(width>descriptor[7])descriptor[7]=(uint8_t)width;
 }
}
void ffta_chemist_menu(uint8_t *menu,uint8_t *descriptor){ffta_original_chemist_menu(menu,descriptor);expand(menu,descriptor);}
void ffta_chemist_restricted_menu(uint8_t *menu,uint8_t *descriptor){ffta_original_chemist_restricted_menu(menu,descriptor);expand(menu,descriptor);}
const uint8_t *ffta_chemist_menu_name(const uint8_t *menu,unsigned row){
 unsigned action=row_action(menu,(uint16_t)row),item=row_choice(menu,(uint16_t)row,action);
 if(item){unsigned n=action==386?4+(item==364):item==367?0:item==368?1:item==369?2:3;return ffta_chemist_choice_labels[n];}
 return ffta_original_chemist_menu_name(menu,row);
}
unsigned ffta_chemist_menu_selected(const uint8_t *menu,unsigned row,unsigned action){
 unsigned item=row_choice(menu,row,action);
 if(item){uint8_t *manager=*(uint8_t **)0x0200f438;manager[16]=(uint8_t)item;manager[17]=(uint8_t)(item>>8);}
 return action;
}
