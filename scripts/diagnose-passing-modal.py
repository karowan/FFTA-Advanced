"""Fixed native cursor/path prototype at the attack-confirmation handoff.

The isolated image intercepts an already accepted Forbidden Dance confirmation
to investigate Passing Step's modal integration. It does not implement or enable
Passing Step or inject attack outcomes. The selected route is replayed only in
this prototype to investigate native post-attack movement. Production is unchanged.
"""
import ctypes as C,hashlib,json,pathlib,runpy,struct,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
ROM=pathlib.Path(meta['path']);image=ROM.read_bytes();LAB=ROM.parent
assert hashlib.sha1(image).hexdigest()==meta['romSha1']
seed=LAB/'dancer-choice-playback'
assert json.loads((seed/'report.json').read_text())['romSha1']==meta['romSha1']
OUT=LAB/'passing-modal';OUT.mkdir(exist_ok=True)
source=r'''
#include <stdint.h>
static unsigned h(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static void sh(uint8_t *p,unsigned v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
typedef struct {
 unsigned magic,phase,owner,wrapper,budget,cost,count,polls,pressed,repeat;
 unsigned old38,originX,originY;
 uint8_t cursor[36],route[128];
 unsigned samples[32];
 unsigned handoffMP,handoffPhase,completedX,completedY;
} Modal;
_Static_assert(sizeof(Modal)<=480,"private diagnostic reservation");
static Modal *const s=(Modal *)0x0203f220u;
static uint8_t *const battle=(uint8_t *)0x0200f4e8u;
static uint8_t *const cursor=(uint8_t *)0x0200f3acu;
extern void original_confirm(void);
static void copy(uint8_t *to,const uint8_t *from,unsigned n){while(n--)*to++=*from++;}
static uint8_t *grid(void){return *(uint8_t **)(s->wrapper+0x3c);}
static void show(unsigned yes){
 ((void (*)(void *,unsigned,void *))0x0809a5e1u)(*(void **)battle,yes,(void *)s->wrapper);
 ((void (*)(void *,unsigned))0x0809a5c1u)(*(void **)battle,yes);
}
void modal_begin(uint8_t *owner){
 const uint8_t *m=*(const uint8_t *const *)0x0200f438u;
 uint8_t *w=*(uint8_t **)(battle+4);
 if(!m || *(unsigned *)(m+20)!=406 || *(void **)(battle+0x60)!=owner ||
    !w || *(void **)w!=*(void **)(m+24)){original_confirm();return;}
 for(unsigned i=0;i<sizeof(*s)/4;i++)((unsigned *)s)[i]=0;
 s->magic=0x53544550;s->phase=1;s->owner=(unsigned)owner;s->wrapper=(unsigned)w;
 s->budget=((unsigned (*)(const void *))REMAINDERu)(*(void **)w);
 s->originX=h(w+8)>>5;s->originY=h(w+12)>>5;s->old38=h(w+0x38);
 copy(s->cursor,cursor,sizeof(s->cursor));
 sh(w+0x38,0x30);
 ((void (*)(void *))0x08099ea1u)(w);
 uint8_t *g=grid();
 ((void (*)(void *,int,int,unsigned,unsigned,unsigned))0x08149231u)
  (g,(int8_t)g[0x981],(int8_t)g[0x982],s->budget,s->originX,s->originY);
 ((void (*)(void *))0x08099f01u)(w);
}
static void finish(void){
 show(0);((void (*)(void))0x080231adu)();
 sh((uint8_t *)s->wrapper+0x38,s->old38);
 copy(cursor,s->cursor,sizeof(s->cursor));
 ((void (*)(void *,unsigned))0x08024abdu)(cursor,s->cursor[4]);
 original_confirm();s->phase=3;
}
int modal_poll(uint8_t *owner,unsigned pressed,unsigned repeat){
 if(s->magic!=0x53544550 || s->owner!=(unsigned)owner || s->phase>=3){
  int r=((int (*)(void))0x08025465u)();
  if(s->magic==0x53544550 && s->owner==(unsigned)owner && s->phase==3 && r){
   if(r>0 && ((unsigned (*)(void))0x080254a1u)()==0x12)s->phase=4;
   else {s->count=0;s->phase=6;}
  }
  return r;
 }
 s->polls++;s->pressed=pressed;s->repeat=repeat;
 if(pressed)s->samples[(s->polls/8)%32]=pressed|(h(cursor+12)<<8)|(h(cursor+16)<<16)|(s->phase<<24);
 show(1);
 if(s->phase==1){
  if(!((unsigned (*)(void *))0x08149369u)(grid()))return 0;
  ((void (*)(void *))0x0809a625u)((void *)s->wrapper);
  sh((uint8_t *)s->wrapper+0x38,s->old38);
  sh(cursor+12,s->originX);sh(cursor+14,h((uint8_t *)s->wrapper+10)>>4);sh(cursor+16,s->originY);
  copy(cursor+20,cursor+12,8);
  ((void (*)(void *,unsigned))0x08024abdu)(cursor,1);
  s->phase=2;return 0;
 }
 ((unsigned (*)(void *))0x08098a89u)((void *)s->wrapper);
 if(pressed&2u){s->count=0;finish();return 0;}
 if(!(pressed&1u))return 0;
 unsigned x=h(cursor+12),y=h(cursor+16);
 if(x==s->originX && y==s->originY){s->count=0;finish();return 0;}
 if(x>15 || y>15 || !s->budget)return 0;
 if(!((unsigned (*)(const void *,unsigned,unsigned))0x08149385u)(grid(),x,y))return 0;
 unsigned cost=((unsigned (*)(const void *,unsigned,unsigned))0x081493adu)(grid(),x,y);
 if(!cost || cost>s->budget)return 0;
 int n=((int (*)(void *,unsigned,unsigned,unsigned,void *))0x0809a605u)((void *)s->wrapper,x,y,s->budget,s->route);
 if(n<2 || n>32 || s->route[4*(n-1)]!=x || s->route[4*(n-1)+1]!=y)return 0;
 if(s->route[0]!=s->originX || s->route[1]!=s->originY)return 0;
 s->count=(unsigned)n;s->cost=cost;finish();return 0;
}
unsigned modal_after_action(void){
 if(s->magic!=0x53544550 || (s->phase!=4 && s->phase!=5))return 0;
 uint8_t *w=*(uint8_t **)(battle+4);
 if((unsigned)w!=s->wrapper){s->phase=6;return 0;}
 if(s->phase==5){
  s->completedX=h(w+8)>>5;s->completedY=h(w+12)>>5;
  /* Native A4438..A444C commits the wrapper before an action, so the
   * earlier attack has already committed the approach tile. There is no
   * second action here. Commit the actual completed native movement once. */
  uint8_t *u=*(uint8_t **)w;
  u[0xf6]=(uint8_t)s->completedX;u[0xf7]=(uint8_t)s->completedY;
  s->phase=6;return 0;
 }
 s->handoffPhase=h(battle+0xdc);s->handoffMP=h(*(uint8_t **)w+0x1c);
 if(s->count<2 || !((unsigned (*)(unsigned))0x080c9541u)(3) ||
    (h(w+8)>>5)!=s->originX || (h(w+12)>>5)!=s->originY){s->phase=6;return 0;}
 /* Fixed diagnostic has no retaliatory or displacement scenario yet.
  * Production must revalidate the exact route after reactions before here. */
 copy(battle+0x124,s->route,s->count*4);*(unsigned *)(battle+0x1a4)=s->count;
 *(uint8_t **)(battle+8)=w;
 unsigned depth=h(battle+0xde);
 if(depth>=32){s->phase=6;return 0;}
 sh(battle+0xe0+2*depth,19);sh(battle+0xde,depth+1);sh(battle+0xdc,40);
 s->phase=5;return 1;
}
'''.replace('REMAINDER',str(meta['symbols']['ffta_turn_step_remaining']|1))
(OUT/'modal.c').write_text(source)
(OUT/'modal.s').write_text('''.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global modal_begin_entry
.thumb_func
modal_begin_entry:
 pop {r3}
 mov r0,r8
 b modal_begin
.global original_confirm
.thumb_func
original_confirm:
 push {lr}
 sub sp,#32
 ldr r1,=0x0200f438
 ldr r0,[r1]
 movs r3,#0
 strb r3,[r0,#3]
 ldr r2,=0x0802572d
 bx r2
.align 2
.global modal_poll_entry
.thumb_func
modal_poll_entry:
 pop {r3}
 mov r0,r8
 ldr r1,[sp,#0x28]
 ldr r2,[sp,#0x2c]
 bl modal_poll
 lsls r0,r0,#16
 asrs r1,r0,#16
 movs r0,#1
 rsbs r0,r0,#0
 ldr r3,=0x080b6551
 bx r3
.align 2
.global modal_after_entry
.thumb_func
modal_after_entry:
 pop {r3}
 push {r0-r3}
 bl modal_after_action
 cmp r0,#0
 pop {r0-r3}
 bne modal_tick_end
 mov r3,r9
 ldr r0,[r3]
 movs r1,#0x40
 orrs r0,r1
 str r0,[r3]
 mov r4,r8
 ldr r3,=0x08093c6b
 bx r3
modal_tick_end:
 ldr r3,=0x08096b15
 bx r3
.ltorg
''')
(OUT/'modal.ld').write_text('SECTIONS { . = 0x093f0000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.comment) *(.ARM.attributes) } }')
prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
subprocess.run([prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-Os','-ffreestanding','-fno-builtin','-nostdlib','-Wall','-Wextra','-Werror',
 '-Wl,-T,'+str(OUT/'modal.ld'),str(OUT/'modal.s'),str(OUT/'modal.c'),'-o',str(OUT/'modal.elf')],check=True)
subprocess.run([prefix+'objcopy.exe','-O','binary',str(OUT/'modal.elf'),str(OUT/'modal.bin')],check=True)
symbols={p[2]:int(p[0],16) for l in subprocess.check_output([prefix+'nm.exe','-n',str(OUT/'modal.elf')],text=True).splitlines() if len(p:=l.split())==3}
code=(OUT/'modal.bin').read_bytes();patched=bytearray(image)
assert patched[0x13f0000:0x13f0000+len(code)]==b'\xff'*len(code)
patched[0x13f0000:0x13f0000+len(code)]=code
def hook(a,b,name):
 jump=(a+5)&~3;patched[a:b]=bytes.fromhex('c046')*((b-a)//2)
 struct.pack_into('<H',patched,a,0xb408);struct.pack_into('<HHI',patched,jump,0x4b00,0x4718,symbols[name]|1)
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
for a,b,name in [(0x25720,0x2572c,'modal_begin_entry'),(0xb6544,0xb6550,'modal_poll_entry'),(0x93c5e,0x93c6a,'modal_after_entry')]:
 assert patched[a:b]==clean[a:b],('unexpected existing hook',hex(a));hook(a,b,name)
TEST=OUT/'modal.gba';TEST.write_bytes(patched)
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
samples=[];inputs=[];checks=0
def tap(e,key):inputs.append(key);e.run(8,key);e.run(180)
def capture(e,label,folder):
 global checks
 r=e.memory();e.save(folder/(label+'.state'));e.screenshot(folder/(label+'.png'));(folder/(label+'.ram')).write_bytes(r)
 (folder/(label+'.iwram')).write_bytes(C.string_at(*e.maps[0x03000000]))
 words=list(struct.unpack_from('<13I',r,0x3f220));m=struct.unpack_from('<I',r,0xf438)[0]-0x02000000
 s=dict(label=label,words=words,route=r[0x3f278:0x3f2f8].hex(),cursor=r[0xf3ac:0xf3d0].hex(),mode=r[m+4],selectedAction=struct.unpack_from('<I',r,m+20)[0],handoff=list(struct.unpack_from('<4I',r,0x3f378)))
 samples.append(s);(OUT/'partial.json').write_text(json.dumps(samples,indent=2));checks+=1;return r,s
for choice,keys in [('retreat',(16,16,256)),('decline',(1,)),('decline-origin',(256,)),
                    ('unreachable',(16,16,16,256)),('cancel-attack',(16,16,256))]:
 folder=OUT/choice;folder.mkdir(exist_ok=True);e=E(TEST)
 try:
  e.load(seed/'start.state');e.set_memory(0x3f220,bytes(480));e.run(1)
  for key in (256,16,256,256,32,256,256,128,256,256):tap(e,key)
  before,s=capture(e,'modal',folder)
  assert s['words'][0]==0x53544550 and s['words'][1]==2,(choice,'modal admission',s)
  assert before[0x8168:0x816a]==bytes((1,3)),(choice,'native movement overlay')
  actor=struct.unpack_from('<I',before,s['words'][3]-0x02000000)[0]-0x02000000
  initial_mp=struct.unpack_from('<H',before,actor+0x1c)[0]
  w=s['words'][3]-0x02000000;origin=before[w+8:w+14]
  for key in keys:tap(e,key)
  if choice=='unreachable':
   rejected,s=capture(e,'rejected',folder)
   assert s['words'][1]==2 and s['words'][6]==0,(choice,'reject route beyond remaining allowance',s)
   assert rejected[w+8:w+14]==origin,(choice,'rejected route moved actor')
   tap(e,1)
  selected,s=capture(e,'selected',folder)
  assert s['words'][1]==3 and s['mode']==11,(choice,'return to confirmation',s)
  assert s['words'][6]==(3 if choice in ('retreat','cancel-attack') else 0),(choice,'native route count',s)
  assert selected[w+8:w+14]==origin,(choice,'premature movement')
  if choice=='cancel-attack':
   tap(e,1);e.run(600);cancelled,s=capture(e,'cancelled',folder)
   assert s['words'][1]==6 and s['words'][6]==0,(choice,'cancel retires route',s)
   assert struct.unpack_from('<H',cancelled,actor+0x1c)[0]==initial_mp,(choice,'cancelled attack paid MP')
   assert cancelled[w+8:w+14]==origin,(choice,'cancelled attack moved actor')
   assert struct.unpack_from('<I',cancelled,0xf4ec)[0]==w+0x02000000,(choice,'cancel retains native player turn')
   continue
  tap(e,256);e.run(1800);after,s=capture(e,'after',folder)
  assert s['words'][1]==6,(choice,'action and deferred movement completed',s)
  assert initial_mp-struct.unpack_from('<H',after,actor+0x1c)[0]==14,(choice,'native attack payment')
  expected_xy=(0,11) if choice=='retreat' else (0,13)
  xy=tuple(struct.unpack_from('<H',after,w+p)[0]//32 for p in (8,12))
  assert xy==expected_xy,(choice,'native movement endpoint',xy,s)
  assert s['handoff'][:2]==[initial_mp-14,19],(choice,'movement follows paid action',s)
  assert struct.unpack_from('<H',after,0xf4e8+0xdc)[0]==47,(choice,'native facing prompt')
  tap(e,256);e.run(1800);retreated,s=capture(e,'post-action-move',folder)
  assert s['words'][1]==6,(choice,'post-action handoff',s)
  assert tuple(retreated[actor+0xf6:actor+0xf8])==expected_xy,(choice,'native turn-end coordinate commit')
  assert struct.unpack_from('<H',retreated,actor+0x1c)[0]>=initial_mp-14,(choice,'movement repeated action payment')
  iwram=C.string_at(*e.maps[0x03000000])
  assert iwram[0x6170:0x6d68]==image[0xa38d24:0xa3991c],(choice,'native IWRAM code integrity')
 finally:e.close()
report=dict(passed=True,romSha1=meta['romSha1'],instrumentedSha1=hashlib.sha1(patched).hexdigest(),fixtureSha1=hashlib.sha1((seed/'start.state').read_bytes()).hexdigest(),inputs=inputs,captureCount=checks,samples=samples,scope=__doc__)
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
