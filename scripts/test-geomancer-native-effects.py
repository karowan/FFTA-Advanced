"""Native backdrop DMA coexistence and actual fixed-view sky raster controls.

Native mode calls original gradient load/register/change/pump consumers beside
the field renderer. Raster mode loads the existing successful player casts and
changes only the display update entry in its control ROM. No live result,
gradient table, field record or pixel is supplied by raster mode.
"""
import collections,ctypes as C,hashlib,importlib.util,json,pathlib,runpy,struct,sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
ROM=pathlib.Path(meta['path']);image=ROM.read_bytes();LAB=ROM.parent
OUT=LAB/'geomancer-native-effects';OUT.mkdir(exist_ok=True)
assert hashlib.sha1(image).hexdigest()==meta['romSha1']
word=lambda b,p:struct.unpack_from('<I',b,p)[0]
half=lambda b,p:struct.unpack_from('<H',b,p)[0]
checks=collections.Counter();rows=[];case=None
mode=sys.argv[1] if len(sys.argv)>1 else '--native'
assert mode in ('--native','--raster')

def check(label,value):
 checks[label]+=1
 assert value,(case,label)

def native():
 global case
 spec=importlib.util.spec_from_file_location('renderer_harness',ROOT/'scripts/test-geomancer-renderer.py')
 h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
 # These are the two original map backdrop selectors; retain the whole
 # inventory and verify their original consumer's base/literal ABI below.
 # 0801DB98 uses record+0x54/0x55 (hexadecimal), not decimal54/55.
 # Authenticate those selector instructions and the original map-table base.
 check('native-map-selector-operands',h.clean[0x1dbe0:0x1dbe2]==bytes.fromhex('5430') and h.clean[0x1dbf2:0x1dbf4]==bytes.fromhex('5530') and word(h.clean,0x1dbe8)==0x08569104)
 selectors=sorted({v for i in range(162) for v in h.maps.record(i)[0x54:0x56] if v!=255})
 table=word(h.clean,0x1d9bc);busy=word(h.clean,0xd88);descriptors=word(h.clean,0xd8c)
 check('native-gradient-table-base',table==0x08425104)
 check('native-DMA-descriptor-layout',busy==0x03002bc0 and descriptors==0x03002bd0)
 def bios_copy(u,pc,size,data):
  # Model only the CpuSet firmware primitive, as other native consumers do.
  # The game's producer, flags, copy arguments and registration stay native.
  source,target,control=[u.reg_read(reg) for reg in (h.UC_ARM_REG_R0,h.UC_ARM_REG_R1,h.UC_ARM_REG_R2)]
  width=4 if control&0x04000000 else 2;count=control&0x1fffff
  assert source%width==target%width==0 and 0<count<=161
  block=bytes(u.mem_read(source,width if control&0x01000000 else width*count))
  u.mem_write(target,block*count if control&0x01000000 else block)
  u.reg_write(h.UC_ARM_REG_PC,(pc+2)|1)
 for selector in selectors:
  for kind in (1,2):
   case=('native-backdrop',selector,kind)
   field=h.Machine().setup(70);control=h.Machine().setup(70)
   for m in (field,control):
    m.u.hook_add(h.UC_HOOK_CODE,bios_copy,begin=0x0814186c,end=0x0814186c)
    # Deterministic producer inputs: enable the original map-gradient state
    # and release channel2's registration slot before the real constructor.
    m.h(0x02007f22,selector);m.put(0x02007f20,b'\0');m.h(busy+4,0)
    m.call(0x0801db2c,selector);m.call(0x0801db3c)
   field.fields(kind);field.update();field.pump();control.pump()
   check('field-published-alongside-native-gradient',bool(field.owner()) and field.word(field.owner()+20)==1)
   records=[]
   for selected in (selector,selectors[(selectors.index(selector)+1)%len(selectors)]):
    for m in (field,control):m.call(0x0801dc24,selected)
    # Deferred source publication goes through the real render pump.
    check('native-gradient-change-is-deferred',field.read(0x02007f26,1)==b'\1')
    field.update();field.pump();control.pump()
    offset=half(h.clean,table-0x08000000+2*selected)
    source=table+offset+6
    expected=field.read(source,320)+field.read(source,2)
    actual=field.read(0x02008390,322)
    check('native-gradient-table-exact',actual==control.read(0x02008390,322)==expected)
    check('deferred-publication-cleared',field.read(0x02007f26,1)==b'\0')
    check('native-backdrop-shadow-exact',field.read(0x03003860,2)==actual[:2]==control.read(0x03003860,2))
    descriptor=field.read(descriptors+32,16)
    check('native-HBlank-registration-preserved',descriptor==control.read(descriptors+32,16))
    check('HBlank-writes-backdrop-palette',struct.unpack_from('<3I',descriptor)==(0x02008392,0x05000000,0xa2400001))
    check('native-gradient-state-preserved',field.read(0x02007f20,24)==control.read(0x02007f20,24))
    records.append(dict(selector=selected,source=hex(source),tableSha1=hashlib.sha1(actual).hexdigest(),colors=len(set(struct.unpack('<161H',actual)))))
   before=field.read(0x02008390,322);descriptor=field.read(descriptors+32,16)
   field.call('ffta_geo_renderer_retire')
   check('field-retirement-preserves-native-gradient',field.read(0x02008390,322)==before and field.read(descriptors+32,16)==descriptor)
   rows.append(dict(selector=selector,kind=kind,records=records))
 return dict(selectors=selectors,mapsScanned=162,mapRecordOffsets=['0x54','0x55'],selectorConsumerSha1=hashlib.sha1(h.clean[0x1db98:0x1dc04]).hexdigest(),scope='Original map backdrop palette DMA; not every unrelated HBlank effect')

def sky(e):
 raw,w,h,pitch,pixel=e.frame;size=4 if pixel==1 else 2
 assert (w,h)==(240,160)
 # Fixed Giza next-turn inputs show clear sky here, above terrain, actors,
 # turn label and menus. Never select a crop based on whether equality passes.
 return b''.join(raw[y*pitch:y*pitch+32*size] for y in range(72)),size

def raster():
 global case
 from geomancer_render_observation import observe
 E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
 play=LAB/'geomancer-playback';manifest=json.loads((play/'report.json').read_text())
 test=play/'playback.gba';original=test.read_bytes()
 check('actual-cast-inputs-current',manifest['passed'] and manifest['romSha1']==meta['romSha1'] and hashlib.sha1(original).hexdigest()==manifest['instrumentedSha1'])
 disabled=bytearray(original);offset=(meta['symbols']['ffta_geo_renderer_update']&~1)-0x08000000
 patch=(bytes.fromhex('c046') if offset&3 else b'')+bytes.fromhex('004b1847')+struct.pack('<I',meta['symbols']['ffta_geo_renderer_retire']|1)
 disabled[offset:offset+len(patch)]=patch;control=OUT/'display-disabled.gba';control.write_bytes(disabled)
 for action in (380,382):
  source=play/str(action)/'0/occupied/0/next-turn.state';results=[]
  for variant,rom in (('control',control),('display',test)):
   case=('rendered-gradient',action,variant);e=E(rom);folder=OUT/f'{action}-{variant}';folder.mkdir(exist_ok=True)
   try:
    e.load(source);e.run(240)
    observe(e,variant=='display')
    frames=[];before=e.memory()
    check('actual-map-gradient-enabled',half(before,0x7f10)==70 and before[0x7f20]==1 and half(before,0x7f22)!=255)
    for index in range(8):
     e.run(1);ram=e.memory();iw=C.string_at(*e.maps[0x03000000]);pixels,size=sky(e)
     colors={pixels[i:i+size] for i in range(0,len(pixels),size)}
     check('visible-positive-gradient',len(colors)>=8)
     check('native-render-code-intact',iw[0x6170:0x6d68]==image[0xa38d24:0xa3991c])
     descriptor=iw[0x2bf0:0x2c00]
     check('live-HBlank-palette-channel',struct.unpack_from('<3I',descriptor)==(0x02008392,0x05000000,0xa2400001))
     frames.append(dict(pixelsSha1=hashlib.sha1(pixels).hexdigest(),colors=len(colors),tableSha1=hashlib.sha1(ram[0x8390:0x84d2]).hexdigest(),descriptor=descriptor.hex()))
    e.screenshot(folder/'sky.png');e.save(folder/'after.state')
    check('observation-preserves-fields',e.memory()[0x3f410:0x3f728]==before[0x3f410:0x3f728])
    results.append(frames)
   finally:e.close()
  check('actual-scanline-gradient-matches-native-control',results[0]==results[1])
  rows.append(dict(action=action,sourceSha1=hashlib.sha1(source.read_bytes()).hexdigest(),results=results))
 return dict(controlSha1=hashlib.sha1(disabled).hexdigest(),controlPatch=dict(offset=hex(offset),original=original[offset:offset+len(patch)].hex(),replacement=patch.hex()),crop=[0,0,32,72],scope='Actual Giza sky in two retained player casts; no claim about other HBlank consumers')

try:
 inputs=native() if mode=='--native' else raster()
 report=dict(passed=True,romSha1=meta['romSha1'],mode=mode,checks=dict(checks),rows=rows,inputs=inputs)
except BaseException as error:
 report=dict(passed=False,romSha1=meta['romSha1'],mode=mode,checks=dict(checks),rows=rows,case=case,error=repr(error))
 raise
finally:
 (OUT/(mode[2:]+'-report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
 print(json.dumps(report,indent=2))
