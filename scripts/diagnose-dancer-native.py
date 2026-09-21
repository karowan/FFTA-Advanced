"""Fixed original-action differential isolating the Dancer scalar hooks."""
import pathlib,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
path=ROOT/'scripts/test-integrated-native.py'
source=path.read_text().replace("exec(compile(source,__file__,'exec'))", "exec(compile(source.split('for action in list(range(347))')[0],__file__,'exec'))")
ns={'__file__':str(path)}
exec(compile(source,str(path),'exec'),ns)
results=[]
for label,restore in [('candidate',()),('attack-restored',((0x12fdc4,0x12fdd0),)),('power-restored',((0x12ff64,0x12ff70),)),('both-restored',((0x12fdc4,0x12fdd0),(0x12ff64,0x12ff70)))]:
 image=bytearray(ns['rom'])
 for start,end in restore:image[start:end]=ns['base'][start:end]
 m=ns['ARM'](image,ns['iw']);events=[]
 points={0x0812fdc4,0x0812fdd0,0x0812ff64,0x0812ff70,0x0812f690,0x0812f5e0,0x081300e2}
 points.update(ns['symbols'][name]&~1 for name in ('ffta_dancer_attack','ffta_dancer_power','ffta_dancer_scaled'))
 def trace(u,address,size,data):
  if address in points:
   events.append(dict(pc=hex(address),registers=[hex(u.reg_read(ns['UC_ARM_REG_R0']+i)) for i in range(8)]))
 m.u.hook_add(ns['UC_HOOK_CODE'],trace)
 expected=ns['original'](ns['native'],15);actual=ns['original'](m,15)
 actual=ns['normalize_native_context'](actual,ns['rom'],ns['base']);expected=ns['normalize_native_context'](expected,ns['rom'],ns['base'])
 differences=[dict(address=hex(0x02000000+i),actual=a,expected=b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
 results.append(dict(label=label,differences=differences,events=events))
out=ns['OUT']/'dancer-original-diagnostic.json';out.write_text(json.dumps(results,indent=2))
print(json.dumps(dict(path=str(out),cases=[dict(label=r['label'],differences=len(r['differences'])) for r in results]),indent=2))
