"""Render the production compositor against an authenticated native field scene.

This is a detached terrain-only comparison, not gameplay, sprite or timing
acceptance. Reuse the already recorded two-caster battle; never invent terrain
or manufacture a new gameplay fixture to review an outline's pixel contrast.
"""
import hashlib,json,pathlib,struct,sys
from PIL import Image,ImageDraw
ROOT=pathlib.Path(__file__).resolve().parents[1]
fixture=ROOT/'scripts/test-geomancer-compositor.py'
ns={'__file__':str(fixture),'__name__':'readability_fixture'}
exec(compile(fixture.read_text(encoding='utf-8').split('for kind,camera in ')[0],str(fixture),'exec'),ns)
u,call,OUT=(ns[k] for k in ('u','call','OUT'))
prior_sha='55f231768cfffdbfc2383191f8648716d452375d'
prior=ROOT/'build/expansion/probes/integrated-jobs/b26778520203359c3b129bcc025b92dd0e4c01f1'/prior_sha
rom=(prior/'integrated.gba').read_bytes()
ram=(prior/'geomancer-overlap/first-1/second-2-3/after-cast.ram').read_bytes()
assert hashlib.sha1(rom).hexdigest()==prior_sha
ram_sha=hashlib.sha1(ram).hexdigest()
assert ram_sha=='f22c785b38ec5c2d014be328a4981407940da3c4'
assert json.loads((prior/'geomancer-overlap/report.json').read_text())['passed']
owners=[i for i in range(12,len(ram)-18332,4) if ram[i:i+4]==b'FGR1'
 and struct.unpack_from('<I',ram,i+4)[0]==0x02000000+i and ram[i-8:i-6]==b'la']
assert len(owners)==1
owner=0x02000000+owners[0];scene=owner+2652;frame=owner+6884
u.mem_write(0x08000000,rom);u.mem_write(0x02000000,ram)
u.mem_write(0x09e00000,ns['code'])
fields=struct.unpack('<7I2i5I',bytes(u.mem_read(scene,56)))
board=bytes(u.mem_read(fields[5],256));assert 1 in board and 2 in board
palette=struct.unpack('<128H',bytes(u.mem_read(fields[3],256)))
colors=[((v&31)*255//31,((v>>5)&31)*255//31,((v>>10)&31)*255//31) for v in palette]
cx,cy=fields[7:9]
def render():
 count,ready=struct.unpack('<HH',bytes(u.mem_read(frame,4)));assert ready and count<=672
 pointer=struct.unpack('<I',bytes(u.mem_read(frame+4100,4)))[0]
 assert 0x02000000<=pointer<=0x02040000-672*32
 cache=bytes(u.mem_read(pointer,672*32))
 planes=[struct.unpack('<1024H',bytes(u.mem_read(frame+4+p*2048,2048))) for p in range(2)]
 pixels=[]
 for y in range(160):
  for x in range(240):
   wx,wy=cx+x,cy+y;color=(48,64,80)
   if 0<=wx<512 and 0<=wy<512:
    pos=((wy//8)&31)*32+((wx//8)&31)
    for plane in (1,0):
     word=planes[plane][pos];physical=word&1023
     slot=physical if physical<640 else physical-192
     assert 0<=slot<count
     pixel=(cache[slot*32+(wy%8)*4+(wx%8)//2]>>(4*(wx%2)))&15
     if pixel:color=colors[((word>>12)&7)*16+pixel]
   pixels.append(color)
 image=Image.new('RGB',(240,160));image.putdata(pixels)
 return image,count
old,old_count=render()
assert call('ffta_geo_compose',scene,frame,0)==1
new,new_count=render()
u.mem_write(fields[5],bytes(256))
assert call('ffta_geo_compose',scene,frame,0)==1
native,native_count=render()
old_pixels,new_pixels=old.tobytes(),new.tobytes()
changed=sum(old_pixels[i:i+3]!=new_pixels[i:i+3] for i in range(0,len(old_pixels),3));assert changed>0
canvas=Image.new('RGB',(720,180),(24,28,36));draw=ImageDraw.Draw(canvas)
for i,(label,picture) in enumerate((('Native terrain',native),('Previous thin edges',old),('Bounded shadow + light core',new))):
 canvas.paste(picture,(240*i,20));draw.text((240*i+5,4),label,fill='white')
canvas.save(OUT/'readability.png')
report=dict(passed=True,sourceSha1=ns['digest'],captureRomSha1=prior_sha,
 captureRamSha1=ram_sha,map=struct.unpack_from('<I',ram,owners[0]+16)[0],camera=[cx,cy],
 fieldCells=sum(bool(v) for v in board),changedVisiblePixels=changed,
 tiles=dict(native=native_count,previous=old_count,revised=new_count),
 image=str(OUT/'readability.png'),limits=['Detached terrain only; no sprites, live publication, frame timing or final release acceptance'])
(OUT/'readability.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

if '--installed-cycle' in sys.argv:
 meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
 installed=pathlib.Path(meta['path']);image=installed.read_bytes()
 assert hashlib.sha1(image).hexdigest()==meta['romSha1']
 folder=installed.parent/'geomancer-cycle-budget'
 proof=json.loads((folder/'report.json').read_text())
 assert proof['passed'] and proof['romSha1']==meta['romSha1']
 grid=Image.new('RGB',(720,180*len(proof['rows'])),(24,28,36));draw=ImageDraw.Draw(grid)
 cases=[]
 for row_index,row in enumerate(proof['rows']):
  memory=(folder/f"map-{row['map']}-3-output.ram").read_bytes()
  expected=next(r['outputSha1'] for r in row['results'] if r['mode']==3)
  assert hashlib.sha1(memory).hexdigest()==expected
  owners=[i for i in range(12,len(memory)-18332,4) if memory[i:i+4]==b'FGR1'
   and struct.unpack_from('<I',memory,i+4)[0]==0x02000000+i and memory[i-8:i-6]==b'la']
  assert len(owners)==1
  owner=0x02000000+owners[0];scene=owner+2652;frame=owner+6884
  u.mem_write(0x08000000,image);u.mem_write(0x02000000,memory);u.mem_write(0x09e00000,ns['code'])
  fields=struct.unpack('<7I2i5I',bytes(u.mem_read(scene,56)));cx,cy=fields[7:9]
  field_board=bytes(u.mem_read(fields[5],256));assert any(field_board)
  projections=list(struct.iter_unpack('<hh4B',bytes(u.mem_read(fields[4],2048))))
  positions=[(projections[i][0]+16,projections[i][1]+8) for i,v in enumerate(field_board) if v]
  # The timing capture follows animated graphics, which may leave the field
  # offscreen. Center this detached review explicitly on the existing field.
  cx=sum(x for x,y in positions)//len(positions)-120
  cy=sum(y for x,y in positions)//len(positions)-80
  u.mem_write(scene+28,struct.pack('<2i',cx,cy))
  palette=struct.unpack('<128H',bytes(u.mem_read(fields[3],256)))
  colors=[((v&31)*255//31,((v>>5)&31)*255//31,((v>>10)&31)*255//31) for v in palette]
  counts=[];visible=[];base_pixels=None
  for kind,label in enumerate(('Native terrain','Rime dashed','Refuge continuous')):
   # Same native-derived positions; changing field kind is a declared detached
   # graphics input, not a claim that these were player-cast campaign fields.
   u.mem_write(fields[5],bytes(kind if v else 0 for v in field_board))
   assert call('ffta_geo_compose',scene,frame,0)==1
   picture,count=render();counts.append(count)
   pixels=picture.tobytes()
   if base_pixels is None:base_pixels=pixels
   else:
    changed=sum(base_pixels[i:i+3]!=pixels[i:i+3] for i in range(0,len(pixels),3))
    assert changed>=12,('Field not visibly represented',row['map'],kind,changed)
    visible.append(changed)
   grid.paste(picture,(240*kind,180*row_index+20))
   draw.text((240*kind+4,180*row_index+4),f"Map {row['map']}: {label}",fill='white')
  cases.append(dict(map=row['map'],captureSha1=expected,camera=[cx,cy],tiles=counts,visibleFieldPixels=visible))
 grid.save(OUT/'terrain-readability.png')
 result=dict(passed=True,sourceSha1=ns['digest'],romSha1=meta['romSha1'],cases=cases,
  image=str(OUT/'terrain-readability.png'),limits=['Detached native-derived terrain inputs; no campaign or sprite visibility claim'])
 (OUT/'terrain-readability.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps(result,indent=2))
