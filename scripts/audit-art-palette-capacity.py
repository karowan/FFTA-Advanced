"""Read-only demand audit before enabling all ten generated class palettes.

Uses authenticated captured native colors and existing class palette references.
No game runs or fixtures are created. This reports potential full-range effect
pretracking demand, not simultaneous visible bodies or a runtime failure.
"""
import argparse, datetime, hashlib, json, re, struct
from pathlib import Path
from native_art import ROOT, sha

classes_path=ROOT/'build/art/generated-classes/595782ba32f4a20ff2053218f8722ab5e491112d/manifest.json'
capture_path=ROOT/'build/art/live-palette/battle/20260918T101335.606659Z/observed.json'
class_bytes=classes_path.read_bytes();capture_bytes=capture_path.read_bytes()
assert sha(class_bytes)=='9c30db597818297809590dbf2c2e08b3ed060466815c4964de83fabf872368d5'
assert sha(capture_bytes)=='adc3ad125d84b9d33222b1866cd1ac26fe80b167b3f04033d345cef887c18578'
classes=json.loads(class_bytes);capture=json.loads(capture_bytes)
rom=Path(classes['path']).read_bytes()
assert hashlib.sha1(rom).hexdigest()==classes['romSha1']=='595782ba32f4a20ff2053218f8722ab5e491112d'
assert capture['romSha1']=='2908487c5de59274b03b71c59add5ab828bcba34'
assert [job['job'] for job in classes['jobs']]==list(range(116,126))

def scale(values,factor):
    return tuple(sum((((value>>shift)&31)*factor//32)<<shift for shift in (0,5,10)) for value in values)

references=[]
for owner,job in enumerate(classes['jobs']):
    offset=job['nativePaletteReference'];raw=rom[offset:offset+32]
    assert sha(raw)==job['nativePaletteSha256']
    references.append((owner,job,struct.unpack('<16H',raw)))

observations={**capture['entryPaletteTraces']['candidate'],**capture['paletteTraces']['candidate']}
rows=[]
for label,observation in observations.items():
    shadow=bytes.fromhex(observation['nativeShadow']);assert len(shadow)==1024
    pairs=[]
    for owner,job,reference in references:
        for bank in range(16):
            actual=struct.unpack_from('<16H',shadow,512+bank*32)
            for factor in (32,19):
                if scale(reference,factor)==actual:
                    pairs.append(dict(owner=owner,job=job['job'],bank=bank,scale=factor,key=owner*16+bank))
                    break
    assert len({pair['key'] for pair in pairs})==len(pairs)
    rows.append(dict(label=label,potentialHistories=len(pairs),pairs=pairs))

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--candidate-manifest',type=Path,default=ROOT/'build/art/live-palette/poc.json')
args=parser.parse_args()
current=json.loads(args.candidate_manifest.read_text())
current_rom=Path(current['path']).read_bytes()
assert hashlib.sha1(current_rom).hexdigest()==current['romSha1']
enabled=struct.unpack_from('<I',current_rom,current['symbols']['ffta_art_custom_mask']-0x08000000)[0]
maximum=max(rows,key=lambda row:row['potentialHistories'])
variant_header=ROOT/'src/engine/art-palette-variants.h'
binding_header=ROOT/'src/engine/art-palette-binding.h'
for header in (variant_header,binding_header):
    assert sha(header.read_bytes())==current['sources'][header.relative_to(ROOT).as_posix()]
limits=ROOT/'src/engine/art-palette-limits.h'
assert sha(limits.read_bytes())==current['sources'][limits.relative_to(ROOT).as_posix()]
default_capacity=int(re.search(r'#define FFTA_ART_HISTORY_SLOTS (\d+)',limits.read_text()).group(1))
capacity=current.get('historySlots',default_capacity)
assert current['bindingCounterOffset']==284*capacity
if capacity!=default_capacity:
    compiled=struct.unpack_from('<12I',current_rom,current['symbols']['ffta_art_live_layout']-0x08000000)
    assert compiled[-1]==capacity*284 and compiled[0]==current['transientStateBytes']
assert 'key[FFTA_ART_HISTORY_SLOTS]' in variant_header.read_text()
assert 'entry[FFTA_ART_HISTORY_SLOTS]' in binding_header.read_text()
report=dict(status='observed',currentHistoryCapacity=capacity,
    potentialHistoryShortfall=max(0,maximum['potentialHistories']-capacity),
    currentRomSha1=current['romSha1'],currentEnabledClassMask=enabled,
    classManifest=str(classes_path),classManifestSha256=sha(class_bytes),
    capture=str(capture_path),captureSha256=sha(capture_bytes),
    sourceHashes={name:sha((ROOT/name).read_bytes()) for name in
        ('src/engine/art-palette-variants.c','src/engine/art-palette-variants.h')},
    maximumPotentialHistories=maximum['potentialHistories'],maximumLabel=maximum['label'],
    observations=rows,
    scope='Exact normal/dim reference matches for all ten classes in retained native palette shadows. Potential history demand if a full OBJ-range effect pretracks every class; not an observed all-class runtime failure, simultaneous visible-bank demand, maximum reachable demand or capacity acceptance.')
out=ROOT/'build/art/palette-capacity-audit'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
out.mkdir(parents=True);(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status=report['status'],maximumPotentialHistories=maximum['potentialHistories'],
    maximumLabel=maximum['label'],currentHistoryCapacity=capacity,
    potentialHistoryShortfall=report['potentialHistoryShortfall'],
    currentEnabledClassMask=enabled,report=str(out/'report.json'))))
