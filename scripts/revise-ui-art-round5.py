"""Targeted model edits for native eye shape, helmet size and class identity."""
import importlib.util,json,sys
from PIL import Image,ImageDraw
from native_art import ROOT,sha

OUT=ROOT/'build/art/ui-detail-v5-2026-09-20'
PREVIOUS=ROOT/'build/art/anchor-ui-v4-2026-09-20'
PROMPTS={
 'human-samurai':'In image 1, edit only the FIFTH icon, the red Samurai. Make the helmet more compact: narrow its side guards by one logical pixel on each side and reduce its crown height slightly. Preserve the gold crescent, red armor, front-facing face and exact eye positions. The helmet should fit the same head scale as the original human jobs, rather than filling the entire cell.',
 'human-dark-knight':'In image 1, edit only the FIFTH icon, the dark helmet. Make the HELMET symmetrical and directly front-facing: centered vertical crest, equal left and right cheek plates, mirrored gold trim and brow, level visor. No diagonal side-view ridge. Its two eyes stay exactly in logical columns 7 and 10, rows 7 and 8 of its 16x14 cell. Only the blue cloth trailing behind the helmet on the right may remain asymmetric.',
 'viera-dancer':'In image 1, edit only the FIFTH icon into a clearly recognizable Viera Dancer using image 2. Emphasize her SHORT chin-length white bob with exposed neck, large bright GOLD HOOP jewelry on her ear, and a bold wine-red high collar. Simplify the hair into a compact silhouette, not long white strands. Her head must look recognizably different from a long-haired armored knight. Keep the original frontal face and exact eye positions.',
 'viera-mystic-knight':'In image 1, edit only the FIFTH icon into a clearly recognizable Viera Mystic Knight using image 2. Emphasize her LONG swept white hair and the distinctive angular dark-metal and GOLD temple ornament with a red jewel beside the ear. Give the bottom of the icon a dark armored collar with the blue cloth tucked behind it. Make the rigid angular ornament and armored silhouette readable in a few bold pixels, distinctly unlike a dancer with a short bob and hoop jewelry. Keep the original frontal face and exact eye positions.'
}

def rec(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p.read_bytes()))
def prepare():
 OUT.mkdir(exist_ok=True);assert not (OUT/'plan.json').exists()
 old=json.loads((PREVIOUS/'results.json').read_text());concepts=json.loads((ROOT/'build/art/native-ui-regeneration-v2-2026-09-20/plan.json').read_text());rows=[]
 for src in old['assets']:
  if not ((src['kind']=='icon' and src['slug'] in PROMPTS) or(src['kind']=='portrait' and src['slug']=='human-dark-knight')):continue
  a={k:v for k,v in src.items() if k not in ['raw','sampled','native','palette','tool','model','paletteError','anchorProof','conversion','worksheetBox','layoutDeviation']};slug=a['slug'];f=OUT/slug;f.mkdir(exist_ok=True)
  if a['kind']=='icon':
   row=Image.new('RGBA',(80,14));row.paste(Image.open(ROOT/a['anchors']['referenceStrip']['path']).convert('RGBA').resize((64,14),Image.Resampling.NEAREST),(0,0));row.paste(Image.open(ROOT/src['native']['path']).convert('RGBA'),(64,0))
   target=f/'edit-row.png';row.resize((1600,280),Image.Resampling.NEAREST).save(target)
   swatch=Image.new('RGB',(480,64));draw=ImageDraw.Draw(swatch)
   for n,w in enumerate(a['paletteWords']):draw.rectangle((n*30,0,n*30+29,63),fill=tuple(((w>>s)&31)*255//31 for s in (0,5,10)))
   pal=f/'native-colors.png';swatch.save(pal)
   concept=next(j['concept'] for j in concepts['jobs'] if j['slug']==slug)
   a.update(logicalSize=[80,14],crop=[64,0,80,14],references=[rec(target),concept,rec(pal)],prompt=PROMPTS[slug]+' Image 3 shows the only available colors. Keep the entire row and all other icons unchanged. Keep the coarse 16x14 pixel grid per head, with no finer details and no text. Do not move or rescale the face.')
  else:
   target=f/'portrait-edit.png';Image.open(ROOT/src['native']['path']).convert('RGBA').resize((768,896),Image.Resampling.NEAREST).save(target)
   a.update(references=[rec(target),rec(PREVIOUS/'fft-dark-knight-user-reference.png')],prompt='Correct only the two golden eyes in image 1 to match the original FFT Dark Knight in image 2: two matching, simple vertical rounded golden ovals inside black helmet darkness. Both eyes must have the SAME rounded shape, not a plus sign, rectangle or human eye. Make each oval large enough to stay rounded on the 48x56 logical pixel grid, approximately 3 pixels wide and 4 pixels tall. Keep their separation and everything else unchanged: helmet, trim, cloth, pose, silhouette, canvas. Return only the portrait, transparent background, hard pixel edges.')
  rows.append(a)
 (OUT/'plan.json').write_text(json.dumps(dict(assets=rows,contracts=old['contracts']),indent=2)+'\n');print('Prepared',len(rows),'targeted edits')

def ingest():
 spec=importlib.util.spec_from_file_location('round4',ROOT/'scripts/revise-ui-art-round4.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.OUT=OUT;m.ingest()

if __name__=='__main__':prepare() if sys.argv[1]=='prepare' else ingest()
