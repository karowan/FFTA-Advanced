"""Native Mystic help, exact status ownership and isolated graphics reservation."""
import pathlib,json,struct,itertools,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-mystic-knight-commands.py';ns={'__file__':str(source),'__name__':'mystic_ui_fixture'}
exec(compile(source.read_text().split('# Native casts cover')[0],str(source),'exec'),ns)
m,S,meta,OUT,A,T,STACK,call,fixture,equip,record=(ns[x] for x in ('m','S','meta','OUT','A','T','STACK','call','fixture','equip','record'))
checks=collections.Counter();case=None
def check(k,a,b):checks[k]+=1;assert a==b,(k,case,a,b)
m.u.mem_map(0x06000000,0x18000)
sprite=0x02028000
for kind,sequence in itertools.product(range(12),range(3)):
 case=('display',kind,sequence);fixture(410);equip(A,'MYK-S1')
 if kind:call('ffta_myk_grant',A,kind)
 p=record(A);value=int.from_bytes(m.read(p+20,2),'little')|(sequence<<13);m.put(p+20,struct.pack('<H',value))
 before=m.read(A,264)+m.read(p,22)
 expected=([42+kind] if kind else [])+([54 if sequence==1 else 55] if sequence else [])
 actual=[key for key in range(43,56) if call('ffta_integrated_status_icon',A,key)]
 check('exact-enchantment-and-next-category',actual,expected)
 for key in expected:
  m.put(0x06000000,b'\xd7'*0x18000);m.put(sprite,b'\xa5'*64)
  check('reserved-native-tile',call('ffta_integrated_status_visual',sprite,key),0x204+2*(key-43))
  offset=0x14080+64*(key-43);vram=m.read(0x06000000,0x18000)
  check('other-VRAM-unchanged',vram[:offset]+vram[offset+64:],b'\xd7'*(0x18000-64))
  check('visible-two-glyph-tiles',any(vram[offset:offset+32]) and any(vram[offset+32:offset+64]),True)
  check('palette-compatible-pixels',set(n for b in vram[offset:offset+64] for n in (b&15,b>>4))<={0,1,6},True)
  check('sprite-only-shape-changed',m.read(sprite,40)+m.read(sprite+44,20),b'\xa5'*60)
 check('UI-read-only',m.read(A,264)+m.read(p,22),before)
 for previous in (0,42,53,54,55,255):
  limit=max(expected) if expected else 24
  next=(previous+1)&255
  check('native-cycle-wrap',call('ffta_integrated_status_next_key',A,previous),1 if next>limit and next<128 else next)
 m.put(A+0x18,bytes(2))
 check('KO-hides-all-Mystic-icons',[call('ffta_myk_status_icon',A,k) for k in range(43,56)],[0]*13)
check('dynamic-pool-reserves-all-Mystic-tiles',pathlib.Path(meta['path']).read_bytes()[0x97098:0x9709c],bytes.fromhex('88239b00'))

# Decode through the native text loader and compare every prior help entry.
help_source=(ROOT/'scripts/test-samurai-help.py').read_text()
help_source=help_source.replace("P/'samurai/current.json'","P/'integrated-jobs/current.json'")
help_source=help_source.replace("help=meta['help']","help=meta['help']['mystic-knight']")
help_source=help_source.replace("ROM.parent/'input.gba'","ROM.parent.parent/'mystic-knight-help-input.gba'")
help_source=help_source.replace("ROM.parent/'help-tests.json'","ROM.parent/'mystic-knight-help-tests.json'")
exec(compile(help_source,'<native Mystic help>','exec'),{'__file__':__file__,'__name__':'mystic_help'})
check('all19-lessons-have-help',len(meta['help']['mystic-knight']['lessons']),19)
report=dict(passed=True,romSha1=meta['romSha1'],checks=dict(checks),total=sum(checks.values()))
(OUT/'mystic-knight-ui.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
