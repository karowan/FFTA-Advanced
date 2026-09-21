"""Add sharp sprite enlargement to generated local artwork review pages."""
from pathlib import Path
import re,sys

ROOT=Path(__file__).resolve().parent

def add_zoom(html):
    if 'id="sprite-zoom"' in html:return html
    css=(ROOT/'art-review-zoom.css.txt').read_text(encoding='utf-8')
    js=(ROOT/'art-review-zoom.js.txt').read_text(encoding='utf-8')
    control='<label>Sprite size <select id="sprite-zoom"><option value="128">Small</option><option value="192" selected>Medium</option><option value="256">Large</option><option value="384">Extra large</option></select></label>'
    dialog='''<dialog id="sprite-detail" aria-labelledby="sprite-detail-title">
<div class="detail-controls"><h2 id="sprite-detail-title">Frame close-up</h2><label>Zoom <select id="detail-zoom"><option value="4">4×</option><option value="6">6×</option><option value="8" selected>8×</option><option value="12">12×</option><option value="16">16×</option></select></label><button id="detail-close" type="button">Close</button></div>
<p id="sprite-detail-caption"></p><p class="muted">This frame stays still for review. Press Escape or Close to return.</p>
<div class="detail-scroll"><img id="sprite-detail-image" class="pixel" alt=""></div></dialog>'''
    assert '<span class="status">' in html and 'function tick(now)' in html
    html=html.replace('</style>',css+'\n</style>',1)
    html=html.replace('<span class="status">',control+'<span class="status">',1)
    html=html.replace('<script>',dialog+'\n<script>',1)
    html=html.replace('function tick(now)',js+'\nfunction tick(now)',1)
    html=html.replace("im.dataset.enemy=pose.images.enemy;return im}","im.dataset.enemy=pose.images.enemy;im.tabIndex=0;im.setAttribute('role','button');im.title='Click to enlarge this frame';im.setAttribute('aria-label',alt+' — enlarge');return im}")
    html=html.replace('Use Pause animations before annotating a moving image.','Use Sprite size to enlarge all frames, or click a frame for a sharp, still close-up. Use Pause animations before annotating a moving image.')
    return html

if __name__=='__main__':
    path=Path(sys.argv[1]);html=add_zoom(path.read_text(encoding='utf-8'));path.write_text(html,encoding='utf-8')
    (path.parent/'page-script.js').write_text(re.search('<script>(.*?)</script>',html,re.S)[1],encoding='utf-8')
    print('Added sprite size controls and click-to-enlarge:',path)
