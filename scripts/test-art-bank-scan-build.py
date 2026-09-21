"""Build an isolated exact-byte palette scanner candidate from installed inputs.

No indexes or historical source manifests are replaced. No emulation or art
generation; runtime/consumer acceptance is separate.
"""
import argparse,datetime,importlib.util,json
from pathlib import Path
from native_art import ROOT,sha

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

parser=argparse.ArgumentParser(description=__doc__)
mode=parser.add_mutually_exclusive_group();mode.add_argument('--dma-tile-cache',action='store_true');mode.add_argument('--fast-oam-plan',action='store_true');mode.add_argument('--arm-oam-scan',action='store_true');mode.add_argument('--arm-full-scan',action='store_true');mode.add_argument('--repeat-frame',action='store_true');mode.add_argument('--scoped-frame',action='store_true');mode.add_argument('--native-oam-prefix',action='store_true');mode.add_argument('--native-owner-producer',action='store_true');mode.add_argument('--fused-compose',action='store_true');mode.add_argument('--fused-word-reads',action='store_true');mode.add_argument('--compact-leaves',action='store_true');mode.add_argument('--unrolled-copy',action='store_true');mode.add_argument('--packed-plan',action='store_true');mode.add_argument('--block-scan',action='store_true');mode.add_argument('--burst-scan',action='store_true');mode.add_argument('--fast-confirm',action='store_true');mode.add_argument('--joined-rows',action='store_true');mode.add_argument('--prepared-preference',action='store_true');mode.add_argument('--rect-conflict',action='store_true');args=parser.parse_args()
if args.rect_conflict:args.prepared_preference=True
if args.prepared_preference:args.fast_confirm=True
if args.joined_rows:args.fast_confirm=True
if args.fast_confirm:args.burst_scan=True
if args.burst_scan:args.block_scan=True
if args.block_scan:args.packed_plan=True
if args.packed_plan:args.unrolled_copy=True
if args.fused_word_reads or args.compact_leaves or args.unrolled_copy:args.fused_compose=True
delivery=json.loads((ROOT/'build/art/pipeline/delivery/current.json').read_text(encoding='utf-8'))
package=(ROOT/delivery['rom']['path']).parent
candidate=json.loads((package/'candidate.json').read_text(encoding='utf-8'))
expected=(ROOT/delivery['rom']['path']).read_bytes();assert sha(expected)==delivery['rom']['sha256']
out=ROOT/'build/art/performance'/('rect-conflict' if args.rect_conflict else 'prepared-preference' if args.prepared_preference else 'joined-rows' if args.joined_rows else 'fast-confirm' if args.fast_confirm else 'burst-scan' if args.burst_scan else 'block-scan' if args.block_scan else 'packed-plan' if args.packed_plan else 'unrolled-copy' if args.unrolled_copy else 'compact-leaves' if args.compact_leaves else 'fused-words' if args.fused_word_reads else 'fused-compose' if args.fused_compose else 'native-owners' if args.native_owner_producer else 'native-prefix' if args.native_oam_prefix else 'scoped-frame' if args.scoped_frame else 'repeat-frame' if args.repeat_frame else 'arm-full-scan' if args.arm_full_scan else 'arm-oam-scan' if args.arm_oam_scan else 'fast-oam-plan' if args.fast_oam_plan else 'dma-tile-cache' if args.dma_tile_cache else 'bank-scan')/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
paths={ROOT/'build/art/pipeline/delivery/current.json',ROOT/'build/art/connected/current.json',ROOT/'build/art/live-palette/status-current.json',
       ROOT/'build/art/connected'/candidate['romSha1']/'manifest.json',ROOT/'build/art/connected'/candidate['romSha1']/'live-palette-view.json'}
for part in candidate['components'].values():
    if 'path' in part:
        p=Path(part['path']).parent/'manifest.json'
        if p.exists():paths.add(p)
before={p:p.read_bytes() for p in paths};checks=[]

def check(ok,label):
    assert ok,label
    checks.append(label)

try:
    builder=module('bank_scan_palette','build-live-art-palette.py')
    live=candidate['components']['livePalette'];builder.PARENT=Path(live['source']).parent/'manifest.json'
    options=dict(history_slots=20,all_classes=True,workspace_low_address=True,provisional_history=True,fast_rotation=True,
        owned_menu_buffer=True,shared_battle_menu_heap=True,compact_us_keyboard=True,compact_battle_status=True,publish_current=False)
    baseline=builder.build(**options)
    check(baseline['romSha1']==live['romSha1'],'Default build remains byte-exact installed palette baseline')
    if args.fused_compose:args.native_owner_producer=True
    trial=dict(fast_oam_plan=True,arm_oam_scan=True,fast_bank_scan=True,repeat_frame=args.repeat_frame,scoped_frame=args.scoped_frame or args.native_oam_prefix or args.native_owner_producer,native_oam_prefix=args.native_oam_prefix or args.native_owner_producer,native_owner_producer=args.native_owner_producer,fused_compose=args.fused_compose,fused_word_reads=args.fused_word_reads,compact_leaves=args.compact_leaves,unrolled_copy=args.unrolled_copy,packed_plan=args.packed_plan,block_scan=args.block_scan,burst_scan=args.burst_scan,fast_confirm=args.fast_confirm,joined_rows=args.joined_rows,prepared_preference=args.prepared_preference,rect_conflict=args.rect_conflict) if args.arm_full_scan or args.repeat_frame or args.scoped_frame or args.native_oam_prefix or args.native_owner_producer else dict(fast_oam_plan=True,arm_oam_scan=True) if args.arm_oam_scan else dict(fast_oam_plan=True) if args.fast_oam_plan else dict(dma_tile_cache=True) if args.dma_tile_cache else dict(fast_bank_scan=True)
    built=builder.build(**options,**trial)
    for field in ('ramReservation','transientStateBytes','artInputs','nativeHighlightOffset','partyHeapRoot'):
        if field=='transientStateBytes' and args.repeat_frame:
            check(built[field]==live[field]+928 and built['repeatOffset']==live[field] and built['ramReservation'][0]+built[field]<=built['partyHeapRoot'],'Repeat state fits existing reservation below menu root')
        else:check(built[field]==live[field],'Scanner preserves '+field)
    connected=module('bank_scan_connected','build-connected-art.py').build(Path(built['path']).parent/'manifest.json',publish_current=False,fixture_source=candidate['fixtureSource'])
    if args.compact_leaves or args.unrolled_copy:
        connected=module('compact_action_completion','complete-generated-actions.py').build(ROOT/'build/art/connected'/connected['romSha1']/'manifest.json',publish_current=False)
    check(connected['romSha1']!=candidate['romSha1'],'Private engineering candidate is distinct from installed baseline')
    view=ROOT/'build/art/connected'/connected['romSha1']/'live-palette-view.json'
    (out/'candidate.json').write_bytes(view.read_bytes())
    (out.parent/'current.json').write_bytes(view.read_bytes())
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks),indent=2)+'\n',encoding='utf-8',newline='\n')
    raise
finally:
    for p,raw in before.items():p.write_bytes(raw)
check(all(p.read_bytes()==raw for p,raw in before.items()),'Existing source manifests and installed indexes restored exactly')
report=dict(status='passed',romSha1=connected['romSha1'],baselineSha1=candidate['romSha1'],checks=checks,manifest=str(view),scope=__doc__)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
