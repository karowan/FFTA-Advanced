"""Freeze either the accepted private overlay or a matching installed build."""
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load_input(current=False):
 p=ROOT/'build/expansion/probes'
 if not current:
  meta=json.loads((p/'dark-sword/current.json').read_text());out=pathlib.Path(meta['path']).parent
  rom=pathlib.Path(meta['path']).read_bytes();base=(out/'input.gba').read_bytes()
 else:
  meta=json.loads((p/'combat.json').read_text());rom=(p/'combat.gba').read_bytes()
  assert {357,358}.issubset(meta['actions']),'Dark sword arts are not installed'
  engine=(ROOT/'build/expansion/engine.bin').read_bytes()
  assert hashlib.sha1(engine).hexdigest()==meta['engineSha1'] and rom[0x1100000:0x1100000+len(engine)]==engine
  meta['symbols']={s[2]:int(s[0],16) for l in (ROOT/'build/expansion/engine.symbols').read_text().splitlines() if len(s:=l.split())==3}
  out=p/'dark-sword/installed'/meta['romSha1'];out.mkdir(parents=True,exist_ok=True)
  meta['path']=str(out/'dark-sword.gba');pathlib.Path(meta['path']).write_bytes(rom)
  clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();base=bytearray(rom)
  for start,end in ((0x12f8a4,0x12f8b0),(0xa315a,0xa3166),(0x13467a,0x134686)):base[start:end]=clean[start:end]
  base=bytes(base);(out/'input.gba').write_bytes(base)
 assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
 return meta,out,rom,base
