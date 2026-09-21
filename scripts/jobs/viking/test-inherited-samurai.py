"""Retain the established complete native executor/Iaido contract on Viking."""
import pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]))
source=(pathlib.Path(__file__).resolve().parents[2]/'test-samurai-native.py').read_text()
source=source.replace('parents[1]','parents[3]').replace("P/'samurai/current.json'","P/'viking/current.json'")
source=source.replace("P/'samurai-state'/meta['baseSha1']","pathlib.Path(meta['path']).parent/'executor'")
checker="""def check(kind,a,b):
 counts[kind]+=1
 if isinstance(a,bytes) and isinstance(b,bytes) and len(a)==0x40000:
  old=struct.unpack_from('<I',b,0xf420)[0];new=struct.unpack_from('<I',a,0xf420)[0]
  if old!=new and 0x08553e70<=old<0x08553e70+209*4 and (old-0x08553e70)%4==0:
   expected=0x09260000+old-0x08553e70
   assert new==expected,('relocated-descriptor-address',new,expected)
   assert rom[new-0x08000000:new-0x08000000+4]==base[old-0x08000000:old-0x08000000+4],('relocated-descriptor-content',old,new)
   canonical=bytearray(a);struct.pack_into('<I',canonical,0xf420,old);a=bytes(canonical)
   counts['exact-native-descriptor-relocation']+=1
 if a!=b and isinstance(a,bytes) and isinstance(b,bytes):
  differences=[dict(address=hex(0x02000000+i),expanded=x,base=y) for i,(x,y) in enumerate(zip(a,b)) if x!=y]
  (OUT/'inherited-difference.json').write_text(json.dumps(dict(action=globals().get('action'),kind=kind,differences=differences),indent=2))
  raise AssertionError((kind,globals().get('action'),len(differences),differences[:30]))
 assert a==b,(kind,a,b)
"""
source=source[:source.index("def check(")]+checker+source[source.index("from native_battle_wrappers"): ]
exec(compile(source,__file__,'exec'))
