"""Fixed, private ablation controls for the menu/AI regression; not acceptance.

Each variant has its own ROM/hash/fixture directory. Only named function
entries are replaced, without editing the production candidate or test inputs.
"""
import hashlib,json,pathlib,struct,shutil,traceback,subprocess,sys,argparse
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
rom=pathlib.Path(meta['path']);image=rom.read_bytes();assert hashlib.sha1(image).hexdigest()==meta['romSha1']
OUT=rom.parent/'mystic-isolation';OUT.mkdir(exist_ok=True)
S=meta['symbols'];rows=[]
choices={
 'accepted-retained-fixture':{},'accepted-fresh-fixture':{},'control':{},
 'no-mystic-flags':{'ffta_additional_extension_snapshot_flags':0,'ffta_myk_action_event':0},
 'no-extension-storage':{'ffta_additional_extension_snapshot_storage':0,'ffta_additional_extension_snapshot_flags':0,'ffta_myk_action_event':0},
 'original-heap':{'ffta_additional_extension_snapshot_storage':0,'ffta_additional_extension_snapshot_flags':0,'ffta_myk_action_event':0},
 'old-snapshot':{'ffta_additional_extension_snapshot_flags':0,'ffta_myk_action_event':0},
 'old-damage-scaling':{},
}
parser=argparse.ArgumentParser();parser.add_argument('--variants',default='accepted-retained-fixture,control,old-damage-scaling');args=parser.parse_args()
selected=args.variants.split(',');assert all(k in choices for k in selected)
variants={k:choices[k] for k in selected}
(OUT/'report.json').write_text(json.dumps(dict(productionSha1=meta['romSha1'],variants=[])))
original=(ROOT/'scripts/test-dancer-choice-ai.py').read_text()
for name,patches in variants.items():
 folder=OUT/name;folder.mkdir(exist_ok=True);data=bytearray(image);changes=[]
 variant_meta=meta
 if name.startswith('accepted-'):
  old_manifest=ROOT/'build/expansion/probes/integrated-jobs/473cf0f4546cabb55ce614abe84f8536a947847a/15715d35dbe3c61b2ac95564df12cf012dcf97ec/manifest.json'
  variant_meta=json.loads(old_manifest.read_text());data=bytearray(pathlib.Path(variant_meta['path']).read_bytes())
  assert hashlib.sha1(data).hexdigest()==variant_meta['romSha1']
 for symbol,value in patches.items():
  address=S[symbol]&~1;offset=address-0x08000000
  old=data[offset:offset+4].hex();data[offset:offset+4]=struct.pack('<HH',0x2000|value,0x4770)
  changes.append(dict(symbol=symbol,address=address,old=old,new=data[offset:offset+4].hex()))
 if name in ('old-snapshot','old-damage-scaling'):
  from arm_literal_relocations import ELFData
  prefix=str(ROOT/'tools/arm-gnu/bin/arm-none-eabi-')
  source=folder/'snapshot.c';baseline_file='action-snapshot.c' if name=='old-snapshot' else 'dancer.c'
  source.write_bytes(subprocess.check_output(['git','show','8547a9c:src/engine/'+baseline_file],cwd=ROOT))
  obj=folder/'snapshot.o';elf=folder/'snapshot.elf';binary=folder/'snapshot.bin'
  flags=['-mcpu=arm7tdmi','-mthumb','-Os','-std=c11','-ffreestanding','-fno-builtin','-I',str(ROOT/'src/engine'),'-I',str(ROOT/'build/expansion')]
  subprocess.run([prefix+'gcc.exe',*flags,'-c',str(source),'-o',str(obj)],check=True)
  bindings='.syntax unified\n.cpu arm7tdmi\n.thumb\n.text\n'
  for line in subprocess.check_output([prefix+'nm.exe','-g',str(obj)],text=True).splitlines():
   parts=line.split()
   if len(parts)==2 and parts[0] in ('U','w') and not parts[1].startswith('__aeabi_'):
    symbol=parts[1];address=S.get(symbol)
    if address is None:assert parts[0]=='w';continue
    bindings+=f'.align 2\n.global {symbol}\n.thumb_func\n{symbol}:\n push {{r3}}\n ldr r3,={address|1}\n mov ip,r3\n pop {{r3}}\n bx ip\n.ltorg\n'
  (folder/'bindings.s').write_text(bindings)
  entry='ffta_snapshot_begin' if name=='old-snapshot' else 'ffta_dancer_scaled'
  subprocess.run([prefix+'gcc.exe',*flags,'-nostdlib','-Wl,-Ttext=0x09310000,-e,'+entry,str(obj),str(folder/'bindings.s'),'-lgcc','-o',str(elf)],check=True)
  subprocess.run([prefix+'objcopy.exe','-O','binary',str(elf),str(binary)],check=True)
  code=binary.read_bytes();assert len(code)<0x10000 and data[0x1310000:0x1310000+len(code)]==b'\xff'*len(code)
  data[0x1310000:0x1310000+len(code)]=code
  exports={p[2]:int(p[0],16) for line in subprocess.check_output([prefix+'nm.exe','-g',str(obj)],text=True).splitlines() if len(p:=line.split())==3 and p[1]=='T'}
  if name=='old-damage-scaling':exports={entry:exports[entry]}
  linked={p[2]:int(p[0],16) for line in subprocess.check_output([prefix+'nm.exe','-n',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
  remap={S[k]&~1:linked[k]&~1 for k in exports};remap.update({meta['priorSymbols'][k]&~1:linked[k]&~1 for k in exports if k in meta['priorSymbols']})
  samurai=json.loads((ROOT/'build/expansion/probes/samurai/current.json').read_text())
  regions=[(0x1100000,0x1100000+(ROOT/'build/expansion/engine.bin').stat().st_size,ROOT/'build/expansion/engine.elf'),
   (0x11c0000,0x11d0000,pathlib.Path(samurai['path']).parent.parent/'samurai.elf'),
   (0x11d0000,0x11e0000,ROOT/'build/expansion/probes/job-state'/meta['upstream']['baseSha1']/'state.elf')]
  for key in ('integration','geomancerAI','mysticKnight'):
   start,end=meta['regions'][key];regions.append((start,end,rom.parent.parent/'integrated.elf'))
  for job,(start,end) in meta['regions']['jobs'].items():
   path=ROOT/'build/expansion/probes/viking-code/viking.elf' if job=='viking' else pathlib.Path(meta['jobViews'][job]['path']).parent.parent/(job+'.elf')
   regions.append((start,end,path))
  count=0
  for start,end,path in regions:
   classification=ELFData(path,prefix)
   for offset in range(start,end-3,2):
    if classification.contains_word(0x08000000+offset):continue
    a,b=struct.unpack_from('<HH',data,offset)
    if a&0xf800!=0xf000 or b&0xf800!=0xf800:continue
    delta=((a&2047)<<12)|((b&2047)<<1)
    if delta&0x400000:delta-=0x800000
    target=0x08000000+offset+4+delta
    if target not in remap:continue
    delta=remap[target]-(0x08000000+offset+4);assert -0x400000<=delta<0x400000
    struct.pack_into('<HH',data,offset,0xf000|((delta>>12)&2047),0xf800|((delta>>1)&2047));count+=1
   for offset in range(start,end-3,4):
    value=struct.unpack_from('<I',data,offset)[0]
    if value&1 and value&~1 in remap and classification.contains_word(0x08000000+offset):
     struct.pack_into('<I',data,offset,remap[value&~1]|1);count+=1
  changes.append(dict(baselineSnapshotRebindings=count))
 heap=variant_meta['heapEnd']
 if name=='original-heap':
  heap=0x0203ce40
  for change in meta['changes']:
   if change['kind']=='heap limit':
    offset=change['offset'];old=struct.unpack_from('<I',data,offset)[0]
    struct.pack_into('<I',data,offset,heap);changes.append(dict(offset=offset,old=old,new=heap))
 target=folder/'integrated.gba';target.write_bytes(data)
 fixture=folder/'fixture';fixture.mkdir(exist_ok=True)
 if name=='accepted-retained-fixture':
  shutil.copyfile(pathlib.Path(variant_meta['path']).parent/'fixture/battle-ready.state',fixture/'battle-ready.state');(fixture/'frozen.gba').write_bytes(data)
 else:subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',str(target),'--out',str(fixture),'--heap-end',hex(heap)],check=True)
 m={**variant_meta,'path':str(target),'romSha1':hashlib.sha1(data).hexdigest(),'heapEnd':heap}
 manifest=folder/'candidate.json';manifest.write_text(json.dumps(m,indent=2))
 # The existing deterministic AI script composes this shared source before
 # executing it. Replace only its candidate manifest, retaining fixed inputs.
 before="meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())"
 after='meta=json.loads(pathlib.Path('+repr(str(manifest))+').read_text())'
 nested='support=support.replace('+repr(before)+','+repr(after)+')\nassert '+repr(after)+' in support\nexec(compile(support,'
 injection='preparation=preparation.replace('+repr('exec(compile(support,')+','+repr(nested)+')\n'
 source=original.replace("exec(compile(preparation,'<fixed native AI formation>','exec'))",injection+"exec(compile(preparation,'<fixed native AI formation>','exec'))")
 ns={'__file__':str(ROOT/'scripts/test-dancer-choice-ai.py'),'__name__':'__main__'}
 row=dict(variant=name,romSha1=m['romSha1'],changes=changes)
 try:
  exec(compile(source,'<declared AI isolation>','exec'),ns);row['passed']=True
 except Exception as exc:
  row.update(passed=False,error=repr(exc));traceback.print_exc()
 assert ns['meta']['romSha1']==m['romSha1'],('wrong comparison build',name,ns['meta']['romSha1'],m['romSha1'])
 row['loadedSha1']=ns['meta']['romSha1']
 row['outcomes']=ns.get('outcomes',[])
 rows.append(row);(OUT/'report.json').write_text(json.dumps(dict(productionSha1=meta['romSha1'],variants=rows),indent=2))
print(json.dumps(rows,indent=2))
