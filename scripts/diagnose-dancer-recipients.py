"""Native recipient eligibility on the recorded player confirmation state."""
import pathlib,json,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'scripts/test-integrated-dancer.py';ns={'__file__':str(source),'__name__':'recipient_diagnostic'}
exec(compile(source.read_text().split('# The two separate native formula terms')[0],str(source),'exec'),ns)
m,S,meta,OUT,STACK=(ns[k] for k in ('m','S','meta','OUT','STACK'))
ram=(OUT/'dancer-choice-playback/1/0/confirmation.ram').read_bytes();samples=[]
actor=0x020005a8
for target in (0x020033e4,0x020034ec,0x02002fc4):
 for choice in range(1,5):
    m.put(0x02000000,ram);manager=m.word(0x0200f438);m.put(manager+16,struct.pack('<H',choice))
    value=m.call(0x080b4c90,actor,target,406,choice,stack=STACK)
    samples.append(dict(target=hex(target),choice=choice,nativeEligibility=value,fields=m.read(target,16).hex(),status=m.read(target+0xe8,8).hex(),context=m.read(0x0200f3f0,52).hex()))
report=dict(romSha1=meta['romSha1'],samples=samples)
(OUT/'dancer-recipients-diagnostic.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
