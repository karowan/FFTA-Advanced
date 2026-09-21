"""Generate private immutable terrain sources for the live ring renderer.

Emit no patched game. Installation must separately check the entire declared
ROM reservation. Animation prefixes and genuinely visible unloaded tiles are
captured by the live owner before it replaces video memory.
"""
import hashlib,json,pathlib,struct,sys
from ffta_maps import Maps,COUNT,CLEAN_SHA1
from ffta_geo_assets import static_tiles,graphics_animations,tile_variants
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE,LIMIT=0x09400000,0x09a00000

def flipped(tile,flip):
 pixels=[n for byte in tile for n in (byte&15,byte>>4)]
 values=[pixels[(7-y if flip&2 else y)*8+(7-x if flip&1 else x)] for y in range(8) for x in range(8)]
 return bytes(values[i]|(values[i+1]<<4) for i in range(0,64,2))

def bucket(tile):
 value=2166136261
 for word in struct.unpack('<8I',tile):value=((value^word)*16777619)&0xffffffff
 value^=value>>16;value=value*0x7feb352d&0xffffffff
 value^=value>>15;value=value*0x846ca68b&0xffffffff;value^=value>>16
 return value&1023
def generate(destination):
 clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();assert hashlib.sha1(clean).hexdigest()==CLEAN_SHA1
 maps=Maps(clean);blob=bytearray(COUNT*24);interned={};records=[]
 def append(data):
  if not data:return 0
  if data not in interned:
   blob.extend(bytes((-len(blob))%4));interned[data]=BASE+len(blob);blob.extend(data)
  return interned[data]
 for index in range(COUNT):
  graphics=static_tiles(maps,index);palette=maps.palette(index).data[:256].ljust(256,b'\0')
  animations=graphics_animations(maps,index);variants=tile_variants(maps,index)
  opaque=[all(b&15 and b>>4 for t in values for b in t) for values in variants]
  arrangement=struct.unpack('<8192H',maps.planar(index));retained=set()
  for cell in range(4096):
   upper=arrangement[cell]&1023;lower=arrangement[cell+4096]&1023
   if upper>=len(variants):retained.add(upper)
   if (upper>=len(variants) or not opaque[upper]) and lower>=len(variants):retained.add(lower)
  retained=sorted(retained);assert len(retained)<=8 and all(i<640 for i in retained)
  prefix=max((a.destination+a.length for a in animations),default=0)//32
  gp,pp,ip=append(graphics),append(palette),append(struct.pack('<'+'H'*len(retained),*retained))
  prepared=bytearray()
  for flip in range(4):
   for offset in range(0,len(graphics),32):
    pixels=flipped(graphics[offset:offset+32],flip)
    prepared.extend(struct.pack('<IHH',append(pixels),bucket(pixels),int(all(b&15 and b>>4 for b in pixels))))
  sp=append(bytes(prepared))
  struct.pack_into('<II4HII',blob,index*24,gp,pp,len(graphics)//32,prefix,len(retained),0,ip,sp)
  records.append(dict(map=index,graphics=gp,graphicsBytes=len(graphics),graphicsSha1=hashlib.sha1(graphics).hexdigest(),
   palette=pp,paletteSha1=hashlib.sha1(palette).hexdigest(),prefixTiles=prefix,retainedIds=retained,retainedPointer=ip,
   preparedPointer=sp,preparedBytes=len(prepared),preparedSha1=hashlib.sha1(prepared).hexdigest(),
   streams=[dict(control=a.control,source=a.source,destination=a.destination,length=a.length,frames=len(a.frames)) for a in animations]))
 assert BASE+len(blob)<=LIMIT,('Geomancer asset reservation overflow',len(blob))
 # Authenticate all emitted pointers/bytes after final deduplication and layout.
 for r in records:
  gp,pp,tiles,prefix,n,reserved,ip,sp=struct.unpack_from('<II4HII',blob,r['map']*24)
  assert (tiles*32,prefix,n,reserved)==(r['graphicsBytes'],r['prefixTiles'],len(r['retainedIds']),0)
  assert hashlib.sha1(blob[gp-BASE:gp-BASE+tiles*32]).hexdigest()==r['graphicsSha1']
  assert hashlib.sha1(blob[pp-BASE:pp-BASE+256]).hexdigest()==r['paletteSha1']
  assert (list(struct.unpack_from('<'+'H'*n,blob,ip-BASE)) if n else [])==r['retainedIds']
  prepared=blob[sp-BASE:sp-BASE+4*tiles*8]
  assert len(prepared)==r['preparedBytes'] and hashlib.sha1(prepared).hexdigest()==r['preparedSha1']
  original=blob[gp-BASE:gp-BASE+tiles*32]
  for index,(pointer,hashed,solid) in enumerate(struct.iter_unpack('<IHH',prepared)):
   assert BASE<=pointer<=BASE+len(blob)-32 and pointer%4==0
   pixels=bytes(blob[pointer-BASE:pointer-BASE+32])
   assert pixels==flipped(original[(index%tiles)*32:(index%tiles+1)*32],index//tiles)
   assert (hashed,solid)==(bucket(pixels),int(all(b&15 and b>>4 for b in pixels)))
 destination.mkdir(parents=True,exist_ok=True)
 binary=destination/'geomancer-assets.bin';binary.write_bytes(blob)
 report=dict(cleanRomSha1=CLEAN_SHA1,base=BASE,limit=LIMIT,bytes=len(blob),sha1=hashlib.sha1(blob).hexdigest(),
  maps=records,sourceSha1=hashlib.sha1((ROOT/'scripts/ffta_geo_assets.py').read_bytes()).hexdigest())
 (destination/'geomancer-assets.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 return report
if __name__=='__main__':
 output=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build/expansion/probes/geomancer-assets'
 report=generate(output)
 print(json.dumps({k:v for k,v in report.items() if k!='maps'},indent=2))
