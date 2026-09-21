"""Build a private, self-contained gallery of existing imagegen drafts.

Embeds original files without editing artwork. Never reads player saves.
"""
import base64, hashlib, html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / 'src/art/imagegen/catalog.json').read_text())
out = ROOT / 'build/art/gallery'
out.mkdir(parents=True, exist_ok=True)

def embed(path):
    return 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode()

reviews = {
    116: 'Samurai idle has reached a private battle. Other animations and graphics remain unfinished.',
    117: 'The native conversion loses the visor and some armor detail.',
    118: 'Costume, face detail and idle motion still need refinement.',
    119: 'The native conversion loses the bright eye and facial outline.',
    120: 'Face detail and idle motion still need refinement.',
    121: 'The native conversion loses some outlines and staff detail.',
    122: 'The current conversion shifts pale colors green and needs correction.',
    123: 'The native conversion loses facial outlines and lute detail.',
    124: 'The native conversion loses facial detail; proportions need refinement.',
    125: 'The native conversion is too narrow and loses face and armor detail.',
}
cards = []
for i, job in enumerate(catalog['jobs']):
    source = ROOT / job['privateSource']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == job['sourceSha256']
    native = ROOT / job['technicalConversion']
    meta = json.loads(native.read_text())
    sheet = native.parent / 'native-sheet.png'
    name = html.escape(job['name'])
    position = f'Row {i//2+1} · Column {i%2+1}'
    cards.append(f'''<article id="job-{job['job']}">
      <header><div><small>{position}</small><h2>{name}</h2></div><span class="badge">Design draft</span></header>
      <button class="art" data-title="{name}" aria-label="Enlarge {name}"><img src="{embed(source)}" alt="{name} generated design sheet" loading="lazy"></button>
      <details><summary>Compare the current game-size conversion</summary>
      <div class="comparison"><figure><img class="native" src="{embed(sheet)}" alt="{name} at native pixel size"><figcaption>Actual pixels</figcaption></figure>
      <figure><img class="zoom" style="width:{meta.get('columns',4)*32*3}px;max-width:100%" src="{embed(sheet)}" alt="{name} conversion enlarged three times"><figcaption>3× enlargement · unfinished</figcaption></figure></div>
      <p class="review">{reviews[job['job']]}</p></details>
    </article>''')

page = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FFTA · New class artwork</title><style>
:root{color-scheme:dark;font-family:Segoe UI,system-ui,sans-serif;background:#111719;color:#f1f3ed}*{box-sizing:border-box}body{margin:0}main{max-width:1340px;margin:auto;padding:42px 24px 70px}.intro small{color:#c5b57e;letter-spacing:.14em;text-transform:uppercase;font-weight:600}h1{font-size:clamp(30px,4vw,46px);font-weight:650;letter-spacing:-.04em;margin:10px 0}p{color:#bbc5c4;line-height:1.6;margin:8px 0}.toolbar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:24px 0}.toolbar button,dialog button{border:1px solid #4a5557;border-radius:7px;background:#222f31;color:#edf2eb;padding:10px 15px;cursor:pointer;font:inherit}a{color:#c5d8ce}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}article{background:#1a2426;border:1px solid #344244;border-radius:12px;overflow:hidden;scroll-margin-top:20px}article header{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:18px 20px}h2{font-size:22px;margin:5px 0 0}small{color:#95aaa6}.badge{font-size:11px;color:#d9cda3;border:1px solid #6c6244;border-radius:20px;padding:5px 9px;white-space:nowrap}.art{display:block;cursor:zoom-in;padding:0;width:100%;border:0;background:#273235;background-image:linear-gradient(45deg,#2b373a 25%,transparent 25%),linear-gradient(-45deg,#2b373a 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#2b373a 75%),linear-gradient(-45deg,transparent 75%,#2b373a 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0}.art img{width:100%;height:auto;aspect-ratio:1;object-fit:contain;display:block}details{padding:15px 20px}summary{cursor:pointer;font-size:14px;color:#c5d8ce}.comparison{display:flex;align-items:center;justify-content:space-around;gap:15px;margin:20px 0;background:#263335;border-radius:6px;padding:14px;min-height:230px}.native,.zoom{image-rendering:pixelated;display:block;margin:auto}figure{margin:0;text-align:center}figcaption{font-size:12px;color:#a4b6b2;margin-top:16px}.review{font-size:13px}dialog{border:1px solid #52615d;border-radius:12px;background:#202b2d;color:#f1f3ed;padding:16px;max-width:min(94vw,1050px);max-height:94vh}dialog::backdrop{background:#000b}dialog header{display:flex;align-items:center;justify-content:space-between;gap:30px;margin-bottom:12px}dialog h2{margin:0}dialog img{display:block;max-width:100%;max-height:78vh;object-fit:contain;margin:auto;background:#293538}button:focus-visible,summary:focus-visible{outline:3px solid #edd395;outline-offset:3px}@media(max-width:700px){main{padding:25px 14px}.grid{grid-template-columns:1fr}article header{padding:14px}.badge{font-size:10px}h2{font-size:20px}.comparison{flex-wrap:wrap}}
</style></head><body><main><section class="intro"><small>FFTA expansion · Artwork review</small><h1>Ten new class designs</h1><p>Original imagegen drafts. Click any sheet to enlarge it.</p><p>These are not finished in-game sprites. The current game-size conversions still need work.</p></section>
<div class="toolbar"><button id="compare">Show all game-size comparisons</button><span>Refer to a class name or its row and column when giving feedback.</span></div>
<section class="grid">''' + ''.join(cards) + '''</section></main>
<dialog><header><h2 id="modal-title"></h2><button id="close" aria-label="Close enlarged sheet">Close ×</button></header><img id="modal-img" alt=""></dialog>
<script>const modal=document.querySelector('dialog');document.querySelectorAll('.art').forEach(b=>b.addEventListener('click',()=>{document.querySelector('#modal-title').textContent=b.dataset.title;const img=document.querySelector('#modal-img');img.src=b.querySelector('img').src;img.alt=b.dataset.title+' full design sheet';modal.showModal()}));document.querySelector('#close').onclick=()=>modal.close();modal.addEventListener('click',e=>{if(e.target===modal)modal.close()});document.querySelector('#compare').onclick=e=>{const show=[...document.querySelectorAll('details')].some(d=>!d.open);document.querySelectorAll('details').forEach(d=>d.open=show);e.target.textContent=show?'Hide game-size comparisons':'Show all game-size comparisons'};</script></body></html>'''
path = out / 'index.html'
path.write_text(page, encoding='utf-8')
print(json.dumps(dict(path=str(path),classes=len(cards),bytes=path.stat().st_size)))
