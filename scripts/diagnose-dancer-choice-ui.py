"""Private trace of the caller supplying an empty player forecast choice."""
import pathlib,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
probe=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
preview_trace_code='''
void preview_trace(unsigned action,unsigned extra,unsigned flags,unsigned caller){
 volatile unsigned *log=(volatile unsigned *)0x0203ff50u;
 if(action==406){
  log[34]=caller;log[35]=action|(extra<<16);log[36]++;
  volatile unsigned *calls=(volatile unsigned *)0x0203f240u;
  for(unsigned i=0;i<16;i++)if(!calls[i*3] || (calls[i*3]==caller && calls[i*3+1]==extra)){
   calls[i*3]=caller;calls[i*3+1]=extra;calls[i*3+2]++;break;
  }
 }
 ((void (*)(void *,unsigned,unsigned,unsigned))CONTEXTu)((void *)0x0200f3f0u,(uint16_t)action,(uint16_t)extra,(uint8_t)flags);
}
'''.replace('CONTEXT',str(probe['symbols']['ffta_dancer_context']|1))
owner=(ROOT/'src/engine/dancer-choice.c').read_text().split('unsigned ffta_dancer_preview_choice')[1].split('void ffta_dancer_context')[0]
owner='unsigned preview_owner'+owner
owner=owner.replace('FFTA_DNC_A6','406').replace('half(manager+16)','h(manager+16)')
owner=owner.replace('    if((uint16_t)action', '''    volatile unsigned *trace=(volatile unsigned *)0x0203f220u;
    const uint8_t *m=*(const uint8_t *const *)0x0200f438u;
    trace[0]=(unsigned)actor;trace[1]=action;trace[2]=primary;trace[3]=(unsigned)m;
    if(m){trace[4]=*(const unsigned *)(m+24);trace[5]=*(const unsigned *)(m+20);trace[6]=m[4];trace[7]=h(m+16);}
    if((uint16_t)action''',1)
preview_trace_code+=owner
script=(ROOT/'scripts/test-dancer-choice-playback.py').read_text().split('# Actual selected player casts')[0]
script=script.replace("exec(compile(support,'<shared deterministic playback>','exec'))","""support=support.replace("(OUT/'logger.c').write_text(source)","source += preview_trace_code\\n(OUT/'logger.c').write_text(source)")
support=support.replace(".ltorg\\n''')", ".ltorg\\n.global preview_trace_entry\\n.thumb_func\\npreview_trace_entry:\\n mov r3,lr\\n b preview_trace\\n''')")
support=support.replace(" b preview_trace\\n''')", " b preview_trace\\n.global preview_owner_entry\\n.thumb_func\\npreview_owner_entry:\\n pop {{r3}}\\n b preview_owner\\n''')")
support=support.replace("TEST_ROM.write_bytes(instrumented)","symbols={v[2]:int(v[0],16) for line in subprocess.check_output([prefix+'nm.exe','-n',str(OUT/'logger.elf')],text=True).splitlines() if len(v:=line.split())==3}\\nstruct.pack_into('<HHI',instrumented,0x12f2a4,0x4b00,0x4718,symbols['preview_trace_entry']|1)\\nTEST_ROM.write_bytes(instrumented)")
support=support.replace("TEST_ROM.write_bytes(instrumented)","entry=meta['symbols']['ffta_dancer_preview_choice']-0x08000000\\njump=(entry+5)&~3\\ninstrumented[entry:entry+12]=bytes.fromhex('c046')*6\\nstruct.pack_into('<H',instrumented,entry,0xb408)\\nstruct.pack_into('<HHI',instrumented,jump,0x4b00,0x4718,symbols['preview_owner_entry']|1)\\nTEST_ROM.write_bytes(instrumented)")
support=support.replace("OUT=LAB/'dancer-choice-playback'","OUT=LAB/'dancer-choice-ui-trace'")
exec(compile(support,'<private choice caller trace>','exec'))""")
exec(compile(script,'<fixed choice preparation>','exec'))
e=E(TEST_ROM)
try:
    e.load(OUT/'start.state');e.run(1);e.set_memory(0x3f240,bytes(192))
    # Match the declared player fixture: native Move, Act, first Dance choice,
    # chosen center and recipient preview. Leave the final cast uncommitted.
    for key in (256,16,256,256,32,256,256,128,256):tap(e,key)
    r=checkpoint(e,'trace',OUT)
    report=dict(romSha1=meta['romSha1'],caller=hex(word(r,LOG+136)),actionExtra=hex(word(r,LOG+140)),calls=word(r,LOG+144),context=r[0xf3f0:0xf424].hex(),owner=[hex(word(r,0x3f220+i*4)) for i in range(8)])
    report['constructors']=[dict(caller=hex(word(r,0x3f240+i*12)),extra=word(r,0x3f244+i*12),count=word(r,0x3f248+i*12)) for i in range(16) if word(r,0x3f240+i*12)]
    (OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
finally:e.close()
