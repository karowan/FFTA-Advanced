"""Fetch public art references and compose labeled, unchanged reference panels."""
import argparse
import hashlib
import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/art/illustrated-class-concepts-v2-2026-09-19'
REF=OUT/'references'
RACES={
 'human':['ffta-h-soldier','ffta-h-fighter','ffta-h-paladin','ffta-h-hunter'],
 'bangaa':['ffta-bangaa-defender','ffta-bangaa-dragoon','ffta-bangaa-gladiator','ffta-bangaa-whitemonk'],
 'nu-mou':['ffta-nu-mou-alchemist','ffta-nu-mou-sage','ffta-nu-mou-whitemage','ffta-nu-mou-beastmaster'],
 'moogle':['ffta-moogle-gadgeteer','ffta-moogle-gunner','ffta-moogle-animist','ffta-moogle-juggler'],
 'viera':['ffta-viera-fencer','ffta-viera-redmage','ffta-viera-elementalist','ffta-viera-summoner']}
JOBS={
 'samurai':['fft-samurai-male','fft-samurai-female'],
 'dark-knight':['ff4-cecil-harvey2','fft-wotl-dark-knight-male'],
 'viking':['ff3-luneth-viking','ff3-ingus-viking'],
 'chemist':['fft-chemist-male','fft-chemist-female'],
 'geomancer':['ff3-luneth-geomancer','fft-geomancer-male'],
 'bard':['fft-bard','ff3-luneth-bard'],
 'dancer':['fft-dancer'],
 'mystic-knight':['ff11-rune-fencer','ff11-rune-fencer-armor-design']}
EXTRA={
 'ff4-cecil-harvey2':'https://www.creativeuncut.com/gallery-07/ff4-cecil-harvey2.html',
 'ff11-rune-fencer':'https://www.creativeuncut.com/gallery-25/ff11-rune-fencer.html',
 'ff11-rune-fencer-armor-design':'https://www.creativeuncut.com/gallery-25/ff11-rune-fencer-armor-design.html'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def fetch_all():
 catalog=json.loads((REF/'catalog.json').read_text())
 pages={Path(u).stem:u for c in catalog for u in c['links']};pages.update(EXTRA)
 names=sorted({s for group in list(RACES.values())+list(JOBS.values()) for s in group})
 def fetch(name):
  page=pages[name]
  raw=urllib.request.urlopen(urllib.request.Request(page,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read().decode()
  links=re.findall(r'<img[^>]+src=["\']([^"\']+)',raw)
  candidates=[urljoin(page,u) for u in links if 'art/' in u and name in u]
  assert candidates,(name,links)
  url=candidates[0]
  path=REF/(name+Path(url).suffix)
  if not path.exists():
   path.write_bytes(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':page}),timeout=30).read())
  with Image.open(path) as im:im.verify()
  return dict(id=name,page=page,imageUrl=url,path=str(path.relative_to(ROOT)),sha256=sha(path))
 results=list(ThreadPoolExecutor(max_workers=5).map(fetch,names))
 (REF/'sources.json').write_text(json.dumps(results,indent=2)+'\n')
 print(f'Fetched and verified {len(results)} official-art reference images.')

def boards():
 sources={s['id']:s for s in json.loads((REF/'sources.json').read_text())}
 font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
 panels=[]
 for role,groups in [('ffta-race',RACES),('ff-job',JOBS)]:
  for name,ids in groups.items():
   count=len(ids);board=Image.new('RGB',(400*count,660),'white');draw=ImageDraw.Draw(board)
   for i,s in enumerate(ids):
    im=Image.open(ROOT/sources[s]['path']).convert('RGBA');im.thumbnail((380,590),Image.Resampling.LANCZOS)
    board.paste(im,(i*400+(400-im.width)//2,20+(590-im.height)//2),im)
    draw.text((i*400+200,630),s,font=font,anchor='mm',fill='#242833')
   p=REF/f'{role}-{name}.jpg';board.save(p,quality=96,subsampling=0)
   panels.append(dict(role=role,name=name,path=str(p.relative_to(ROOT)),sha256=sha(p),sources=[sources[s] for s in ids]))
 (ROOT/'src/art/race-study/illustrated-reference-sets-v2.json').write_text(json.dumps(panels,indent=2)+'\n')
 print(f'Composed {len(panels)} reference panels without changing character artwork.')

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['fetch','boards']);args=parser.parse_args()
 fetch_all() if args.action=='fetch' else boards()
