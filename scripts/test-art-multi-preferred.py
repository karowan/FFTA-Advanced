"""Compiled twenty-slot preferred assignments: pixel conflicts and atomic fallback."""
import argparse, ast, datetime, hashlib, json, struct, subprocess, sys
from pathlib import Path
from native_art import ROOT, sha
from art_palette_build import write_pixel_banks
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007800
source=(ROOT/'scripts/test-equipment-legality.py').read_text(encoding='utf-8').replace('count=50000','count=500000').replace(
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
 'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<ARM>','exec'))
out=ROOT/'build/art/multi-preferred'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--candidate-manifest',type=Path,help='Inspect a retained compiled trial without changing production source.')
args=parser.parse_args();checks=[]
def check(ok,label):
 assert ok,label
 checks.append(label)
try:
 sources=['src/engine/art-palette-plan.c','src/engine/art-palette-scan.s']
 if args.candidate_manifest:
  meta=json.loads(args.candidate_manifest.read_text(encoding='utf-8'));rom=Path(meta['path']).read_bytes()
  check(hashlib.sha1(rom).hexdigest()==meta['romSha1'] and meta['historySlots']==20,'Retained twenty-slot candidate authenticated')
  symbols=meta['symbols'];code=rom[meta['used'][0]:meta['used'][1]]
  source_hashes={p:meta['sources'][p] for p in sources+['src/engine/art-palette-plan.h']}
 else:
  lookup,_=write_pixel_banks(out);prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-');elf=out/'plan.elf';binary=out/'plan.bin'
  sources=['src/engine/art-palette-plan.c','src/engine/art-palette-scan.s']
  command=[prefix+'gcc.exe','-mcpu=arm7tdmi','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wall','-Wextra','-Werror','-DFFTA_ART_HISTORY_SLOTS=20','-Wl,-Ttext=0x09f90000','-Wl,-e,ffta_art_palette_apply',*sources,str(lookup),'-o',str(elf)]
  result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);(out/'compile.log').write_text(result.stdout+result.stderr,encoding='utf-8');result.check_returncode()
  subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True,capture_output=True)
  symbols={v[2]:int(v[0],16) for line in subprocess.check_output([prefix+'nm.exe',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  code=binary.read_bytes();assert len(code)<0x40000
  rom=bytearray(b'\xff'*0x2000000);rom[0x1f90000:0x1f90000+len(code)]=code
  source_hashes={p:sha((ROOT/p).read_bytes()) for p in sources+['src/engine/art-palette-plan.h']}
 a=ARM(rom,bytes(0x8000))
 F,O,V,P,C,T,R,CACHE,BACKUP=0x02010000,0x02011000,0x02020000,0x02012000,0x02012400,0x02013000,0x02013100,0x02014000,0x02016000
 colors=bytes((i*7)%256 for i in range(640));palette=bytes((i*13)%256 for i in range(512))
 a.put(F,struct.pack('<8I',O,V,T,P,C,R,1,20));a.put(C,colors)
 def plan(assignments):
  slots=[255]*20;wanted=0
  for owner,bank in assignments:slots[owner]=bank;wanted|=1<<owner
  return struct.pack('<H2xI20BH2x',0x8001,wanted,*slots,0)
 def objects(assignments):
  oam=bytearray(struct.pack('<4H',0x200,0,0,0)*128);tags=bytearray([255]*128)
  struct.pack_into('<4H',oam,0,0x2000,0,0,0)
  for index,(owner,bank) in enumerate(assignments,1):
   struct.pack_into('<4H',oam,index*8,32,0x8040,0,0);tags[index]=owner
  return oam,tags
 def reapply(oam,tags,pixels,prior,residue=0):
  a.put(O,oam);a.put(T,tags);a.put(V,pixels);a.put(P,palette);a.put(R,prior)
  result=a.call(symbols['ffta_art_palette_reapply'],F,stack=STACK-residue)
  return result,a.read(O,1024),a.read(P,512),a.read(R,32)
 bank_sets=[(1,15),(3,4),(1,3,4,5),(2,6,10,14),tuple(range(1,16))]
 for banks in bank_sets:
  assignments=list(zip(range(20-len(banks),20),banks));oam,tags=objects(assignments);prior=plan(assignments)
  expected_oam=bytearray(oam);expected_palette=bytearray(palette)
  for index,(owner,bank) in enumerate(assignments,1):
   struct.pack_into('<H',expected_oam,index*8+4,bank<<12)
   expected_palette[bank*32:bank*32+32]=colors[owner*32:owner*32+32]
  # Independent oracle tests every byte value and byte lane for each set.
  for value in range(256):
   for lane in range(4):
    pixels=bytearray(32768);pixels[lane]=value
    got=reapply(oam,tags,pixels,prior,residue=4 if lane&1 else 0)
    expected=(0,bytes(oam),palette,prior) if value//16 in banks else (1,bytes(expected_oam),bytes(expected_palette),prior)
    check(got==expected,'All-byte/lane mask '+str((banks,value,lane)))
  # A disappeared owner and a newly visible owner must both invalidate reuse.
  altered=bytearray(tags);altered[len(assignments)]=255
  check(reapply(oam,altered,bytes(32768),prior)==(0,bytes(oam),palette,prior),'Missing old owner refuses '+str(banks))
  altered=bytearray(tags);altered[1]=0
  check(reapply(oam,altered,bytes(32768),prior)==(0,bytes(oam),palette,prior),'New owner refuses '+str(banks))
  for bad_bank in (0,16,255,banks[0]):
   bad=bytearray(prior);bad[8+assignments[-1][0]]=bad_bank
   check(reapply(oam,tags,bytes(32768),bad)==(0,bytes(oam),palette,bytes(bad)),'Invalid or duplicate bank refuses '+str((banks,bad_bank)))
  a.u.ctl_flush_tb()
 # High-slot pair; changed pixel forces complete replanning and native backup.
 assignments=[(4,2),(19,3)];oam,tags=objects(assignments)
 struct.pack_into('<4H',oam,0,0x2000,0xc000,0,0)
 struct.pack_into('<4H',oam,127*8,0,0,0,0)
 initial_pixels=bytes([16])*4096+bytes(32768-4096)
 for position in (0,3,63,64,511,1023,2047,2048,4095):
  a.put(O,oam);a.put(T,tags);a.put(V,initial_pixels);a.put(P,palette);a.put(R,bytes(32))
  check(a.call(symbols['ffta_art_palette_apply'],F)==1,'Initial two-owner full plan')
  prior=a.read(R,32);check((prior[12],prior[27])==(2,3),'High-slot full plan selects expected banks')
  pixels=bytearray(initial_pixels);pixels[position]=32
  check(reapply(oam,tags,pixels,prior)==(0,bytes(oam),palette,prior),'Changed pixel invalidates multi-bank reuse '+str(position))
  a.put(O,oam);a.put(P,palette);a.put(R,prior)
  result=a.call(symbols['ffta_art_palette_apply'],F)
  expected=result,a.read(O,1024),a.read(P,512),a.read(R,32)
  a.put(O,oam);a.put(P,palette);a.put(R,prior);a.put(BACKUP,b'\xc7'*512)
  result=a.call(symbols['ffta_art_palette_live_apply'],F,CACHE,BACKUP)
  check((result,a.read(O,1024),a.read(P,512),a.read(R,32))==expected,'Fallback equals complete planner '+str(position))
  saved=bytearray(b'\xc7'*512)
  for owner in (4,19):
   bank=expected[3][8+owner];saved[bank*32:bank*32+32]=palette[bank*32:bank*32+32]
  check(a.read(BACKUP,512)==saved,'Only newly assigned native banks backed up '+str(position))
 # Exact same footprint rules under clipping, flips, affine and mosaic flags.
 for x,y,hflip,vflip,flags in [(0,0,0,0,0),(-32,-32,0,0,0),(232,152,0,0,0),(232,152,1,1,0),(-64,-64,1,1,0),(240,160,0,0,0),(240,160,0,0,0x100),(240,160,0,0,0x1000)]:
  oam,tags=objects(assignments);struct.pack_into('<4H',oam,0,0x2000|flags|(y&255),0xc000|(x&511)|(hflip<<12)|(vflip<<13),0,0)
  for row in range(8):
   for col in range(8):
    pixels=bytearray(32768);pixels[row*512+col*64:row*512+col*64+64]=bytes([32])*64
    px=x+(56-col*8 if hflip else col*8);py=y+(56-row*8 if vflip else row*8)
    conflict=bool(flags or (px<240 and px+8>0 and py<160 and py+8>0))
    got=reapply(oam,tags,pixels,plan(assignments))
    check(got[0]==int(not conflict),'Independent tile visibility '+str((x,y,hflip,vflip,flags,row,col)))
    if conflict:check(got[1:3]==(bytes(oam),palette),'Clipped/affine refusal atomic')
 report=dict(status='passed',checks=checks,compiledSha256=sha(code),sources=source_hashes,candidateManifest=str(args.candidate_manifest) if args.candidate_manifest else None,scope='Compiled twenty-history multi-owner preferred palette assignment; exhaustive byte/lane bank-set membership, high slots, missing/new owners, invalid/duplicate banks, current-pixel mutation and exact full-planner fallback/backup, independent clipped/flipped/affine/mosaic footprint. Component inputs, not gameplay timing or full native lifecycle.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n',encoding='utf-8');print('Artifacts: '+str(out));raise
