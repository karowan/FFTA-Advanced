"""Full round-six review, preserving every unaffected surface from round five."""
import importlib.util,json
from PIL import Image
import numpy as np
from native_art import ROOT

def main():
    spec=importlib.util.spec_from_file_location('builder5',ROOT/'scripts/build-art-approval-round5.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.GEN=ROOT/'build/art/ui-detail-v6-2026-09-20'
    m.OLDGEN=ROOT/'build/art/ui-detail-v5-2026-09-20'
    m.BASE=ROOT/'build/art/job-art-approval-v5-2026-09-20'
    m.OUT=ROOT/'build/art/job-art-approval-v6-2026-09-20'
    m.ROUND_NUMBER=6;m.EDIT_COUNT=2;m.OLD_RESULTS_NAME='review-results.json'
    m.INTRO='Two focused badge revisions: the Samurai’s balanced frontal face and a slightly wider Dark Knight helmet with the same eye spacing.'
    for slug in ('viera-dancer','viera-mystic-knight'):(m.GEN/slug).mkdir(exist_ok=True)
    m.main()
    sam=np.array(Image.open(m.GEN/'human-samurai/icon-native.png'))
    # Inspect the entire inner eye area, not just the sparse shared anchors.
    dark={(x,y) for y in (7,8) for x in range(6,12) if sam[y,x]==1}
    assert dark=={(7,7),(7,8),(10,7),(10,8)},dark
    knight=np.array(Image.open(m.GEN/'human-dark-knight/icon-native.png'))
    previous=np.array(Image.open(m.OLDGEN/'human-dark-knight/icon-native.png'))
    def width(idx,y):
        xs=np.flatnonzero(~np.isin(idx[y],(0,3,8,10,11)))
        return int(xs[-1]-xs[0]+1)
    widths=[width(knight,y) for y in (5,6,7,8)]
    oldwidths=[width(previous,y) for y in (5,6,7,8)]
    assert sum(widths)>sum(oldwidths),(widths,oldwidths)
    report=dict(samuraiInnerEyeDarkPixels=sorted(dark),helmetWidths=widths,previousHelmetWidths=oldwidths,rows=[5,6,7,8],scope='Palette-index silhouette estimate excluding background and blue cloth; human visual approval remains pending.')
    (m.OUT/'targeted-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    page=m.OUT/'index.html'
    page.write_text(page.read_text(encoding='utf-8').replace('<a href="anchor-verification.json">','<a href="targeted-verification.json">Face and helmet-width checks</a> · <a href="anchor-verification.json">'),encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':main()
