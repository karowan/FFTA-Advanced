"""Cold native US keyboard: bounded pages, both tabs, editing and confirmation."""
import ast,ctypes as C,datetime,hashlib,json,runpy,struct,sys
from pathlib import Path
from native_art import ROOT,sha
m=json.loads((ROOT/'build/art/connected/current.json').read_text());rom=Path(m['path']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==m['romSha1'] and m['components']['livePalette']['compactUsKeyboard']
old=json.loads((ROOT/'build/art/connected/7b966543796975a6dea474d0a360495b57d8e6a3/manifest.json').read_text())
previous=Path(old['path']).read_bytes()
assert hashlib.sha1(previous).hexdigest()==old['romSha1']
assert [i for i,(a,b) in enumerate(zip(previous,rom)) if a!=b]==[0x12a15e]
assert previous[0x12a15e:0x12a162]==bytes.fromhex('c6200002') and rom[0x12a15e:0x12a162]==bytes.fromhex('42200002')
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
tree=ast.parse((ROOT/'scripts/probe-ap-copy-heap.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='heap'],type_ignores=[]),'<native heap inspection>','exec'))
out=ROOT/'build/art/keyboard'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
# Authenticated pre-live-palette parent has the original six-page keyboard
# and its original F000 heap limit. It is the native UI reference. Increasing
# the connected ROM's heap would overlap active palette state and is invalid.
controlpath=Path(m['components']['livePalette']['source']);control=controlpath.read_bytes()
assert hashlib.sha1(control).hexdigest()=='0fa7d1707e2d85fb2a8602f061b5eb4479ff3211'
assert control[0x12a15e:0x12a162]==bytes.fromhex('c6200002')
checks=[];runs={};active=None

def check(ok,label):
 assert ok,label
 checks.append(label)
def word(r,p):return struct.unpack_from('<I',r,p)[0]
def context(r,size):
 h=heap(r);blocks={b['address']+12:b['payloadBytes'] for b in h['allocationBlocks'] if b['marker']=='la'}
 matches=[]
 for p,n in blocks.items():
  if n!=size:continue
  needle=struct.pack('<I',p)
  for at in range(0,len(r)-0x10,4):
   if r[at:at+4]!=needle or at<0x2fc:continue
   ctx=at-0x2fc
   if blocks.get(word(r,ctx+0x300))==0x480 and blocks.get(word(r,ctx+0x304))==0xf0:matches.append(ctx)
 assert len(matches)==1,('Unique actual keyboard context',size,matches)
 return matches[0],h

def run(label,path,size):
 global active
 e=E(path);active=e;records={};runs[label]=records;inputs=[]
 def advance(n,key=0):inputs.append([n,key]);e.run(n,key)
 def tap(key):advance(8,key);advance(120)
 def capture(name,keyboard=True):
  r=e.memory();e.screenshot(out/(label+'-'+name+'.png'));e.save(out/(label+'-'+name+'.state'))
  for ext,data in [('ram',r),('iwram',C.string_at(*e.maps[0x03000000])),('vram',C.string_at(*e.maps[0x06000000])),('palette',C.string_at(*e.maps[0x05000000]))]:(out/(label+'-'+name+'.'+ext)).write_bytes(data)
  info=dict(heap=heap(r),frameSha256=sha(e.frame[0]))
  if keyboard:
   ctx,h=context(r,size);p=word(r,ctx+0x2fc)-0x02000000
   check(h['end']==(0x0203c000 if label=='candidate' else 0x0203f000),label+' heap boundary '+name)
   info.update(context=0x02000000+ctx,page=r[ctx+0x2f6],builtPages=r[ctx+0x2f7],name=r[ctx+0x312:ctx+0x324].hex(),nameLength=r[ctx+0x326],glyphsSha256=sha(r[p:p+0x4200]),glyphPointer=0x02000000+p)
   check(info['page'] in (0,1) and info['builtPages']==2,label+' native two-page bounds '+name)
  records[name]=info
 e.set_memory(0,b'\xff'*len(e.memory(0)),0)
 advance(3600);tap(8);advance(60);advance(8,256);advance(1800)
 records['openingTrace']=[]
 for step in range(96):
  advance(8,256);advance(360);raw=e.memory();h=heap(raw)
  records['openingTrace'].append(dict(step=step,heap=h))
  if any(b['marker']=='la' and b['payloadBytes']==size for b in h['allocationBlocks']):
   advance(180);break
 else:raise AssertionError('Native keyboard allocation absent after 96 dialogue presses')
 advance(180);capture('alphabet');keyboard_input_start=len(inputs)
 # Empty the inherited default name, then enter a native letter and digit.
 for _ in range(8):tap(1)
 capture('empty');tap(256);capture('letter');tap(2048);capture('numbers');tap(256);capture('letter-digit')
 tap(2048);capture('right-wrap');tap(1024);capture('left-wrap');tap(1024);capture('alphabet-again')
 for name,page in [('alphabet',0),('numbers',1),('right-wrap',0),('left-wrap',1),('alphabet-again',0)]:check(records[name]['page']==page,label+' selected page '+name)
 check(records['empty']['nameLength']==0 and records['letter']['nameLength']==1 and records['letter-digit']['nameLength']==2,label+' native letter/digit editing')
 tap(8);capture('confirm-dialog',False);tap(64);tap(256);advance(360);capture('confirmed',False)
 # The glyph allocation must have been released by the native task teardown.
 check(all(b['marker']!='la' or b['payloadBytes']!=size for b in records['confirmed']['heap']['allocationBlocks']),label+' keyboard allocation released after confirmation')
 records['inputs']=inputs;records['keyboardInputs']=inputs[keyboard_input_start:];e.close();active=None;return records
try:
 if '--reconcile' in sys.argv:
  evidence=ROOT/sys.argv[sys.argv.index('--reconcile')+1];pins=json.loads(evidence.read_text())
  check(pins['romSha1']==m['romSha1'],'Reconciled exact candidate')
  for entry in pins['files']:
   check(sha((ROOT/entry['path']).read_bytes())==entry['sha256'],'Authenticated retained '+entry['path'])
  retained=json.loads((ROOT/pins['source']).read_text())
  check(retained['error']=='Rendered native glyph grid identical alphabet','Only first cropped pixel comparison failed')
  check(retained['romSha1']==m['romSha1'],'Retained runtime exact candidate')
  checks.extend(retained['checks']);runs=retained['runs'];capture_root=(ROOT/pins['source']).parent
 else:
  for label,path,size in [('control',controlpath,0xc600),('candidate',Path(m['path']),0x4200)]:runs[label]=run(label,path,size)
  capture_root=out
 for label,size in [('control',0xc600),('candidate',0x4200)]:
  for name,info in runs[label].items():
   if name in ('inputs','keyboardInputs','openingTrace'):continue
   raw=(capture_root/(label+'-'+name+'.ram')).read_bytes()
   check(heap(raw)==info['heap'],'Retained native heap agrees '+label+' '+name)
   if 'page' in info:
    ctx,_=context(raw,size);p=word(raw,ctx+0x2fc)-0x02000000
    check(sha(raw[p:p+0x4200])==info['glyphsSha256'],'Both real page buffers agree '+label+' '+name)
  raw=(capture_root/(label+'-confirmed.ram')).read_bytes()
  entered=bytes.fromhex(runs[label]['letter-digit']['name'])[:4]
  check(raw[0x1f1c:0x1f22]==entered+b'\x00\x00','Edited name actually committed to native story name '+label)

 for name in runs['candidate']:
  if name in ('inputs','keyboardInputs','openingTrace'):continue
  a,b=runs['candidate'][name],runs['control'][name]
  for field in ('page','builtPages','name','nameLength','glyphsSha256'):
   if field in a:check(a[field]==b[field],'Native control equality '+name+' '+field)
  # Pixel comparison of the character grid includes original native lettering.
  if 'page' in a:
   from PIL import Image
   c=Image.open(capture_root/('candidate-'+name+'.png'));v=Image.open(capture_root/('control-'+name+'.png'))
   check(c.crop((51,99,528,378)).tobytes()==v.crop((51,99,528,378)).tobytes(),'Rendered native glyph grid identical '+name)
 check(runs['candidate']['keyboardInputs']==runs['control']['keyboardInputs'],'Identical fixed keyboard interaction inputs')
 report=dict(status='passed',captureRoot=str(capture_root),reconciled='--reconcile' in sys.argv,romSha1=m['romSha1'],checks=checks,runs=runs,controlSha1=hashlib.sha1(control).hexdigest(),scope='Actual cold start, US two keyboard pages, both shoulder-key wrap directions, native lettering and letter/digit editing, confirmation and allocation teardown. One-byte production delta. Authenticated pre-live-palette parent retains original six-page allocation with original F000 capacity. Not battle capacity, Japanese keyboard or full campaign acceptance.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
 if active:
  if active.frame is not None:active.screenshot(out/'failed.png')
  (out/'failed.ram').write_bytes(active.memory());active.save(out/'failed.state');active.close()
 (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=m['romSha1'],checks=checks,runs=runs,error=str(error)),indent=2)+'\n');print('Artifacts: '+str(out));raise
