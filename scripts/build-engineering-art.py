"""Build the complete native-art chain inside a fresh source-build workspace.

Inputs are a freshly source-built gameplay ROM, original PNGs and pinned
conversion specifications. Re-extract native resources from that ROM and
reconvert the PNGs; no old component ROM, state or generated tile is an input.
"""
import argparse, hashlib, importlib, importlib.util, json, struct
from pathlib import Path
from native_art import ROOT, sha, extract_actor, palette

def load_module(name,filename):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/filename)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--base-manifest',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    recipe=json.loads((ROOT/'notes/native-art-build-inputs.json').read_text());checks=[];parts={}
    out=args.output.resolve();assert out.is_relative_to((ROOT/'build/engineering-art').resolve());out.mkdir(parents=True)
    def check(ok,label):
        assert ok,label
        checks.append(label)
    def accept(name,part):
        check(part['romSha1']==recipe['components'][name] and hashlib.sha1(Path(part['path']).read_bytes()).hexdigest()==part['romSha1'],'Exact rebuilt '+name)
        parts[name]=part;print('Built '+name+': '+part['romSha1'],flush=True);return Path(part['path']).parent/'manifest.json'
    try:
        for row in recipe['inputs']:check(sha((ROOT/row['path']).read_bytes())==row['sha256'],'Original art/spec input '+row['path'])
        converter=load_module('release_sprite_conversion','convert-generated-sprites.py').convert
        for name,source in recipe['conversions'].items():
            p=ROOT/name;old=json.loads(p.read_text());frames=old['frames']
            columns=max(f['cell'][0] for f in frames)+1;rows=max(f['cell'][1] for f in frames)+1
            cuts=[frames[r*columns]['box'][1] for r in range(1,rows)]
            height=round(old['scale']*max(f['bounds'][3]-f['bounds'][1] for f in frames))
            converter(ROOT/source,p.parent,columns,rows,height,row_cuts=cuts,quantizer=old.get('quantizer','coverage'),resampling=old.get('resampling','nearest'))
            new=json.loads(p.read_text());check(new['paletteSha256']==old['paletteSha256'] and [f['tileSha256'] for f in new['frames']]==[f['tileSha256'] for f in frames],'Exact PNG reconversion '+name)
        base=json.loads(args.base_manifest.read_text());rom=Path(base['path']).read_bytes()
        check(hashlib.sha1(rom).hexdigest()==base['romSha1']==recipe['gameplayBaseSha1'],'Fresh source-built gameplay base')
        jobs=struct.unpack_from('<I',rom,0xc8598)[0]-0x08000000
        donors=sorted({struct.unpack_from('<H',rom,jobs+52*j+f)[0] for j in range(116,126) for f in (7,9)})
        for donor in donors:extract_actor(rom,donor,ROOT/f'build/art/native-reference/actor-{donor:03}',palette(rom,0x41a860)[1])
        check(len(donors)==20,'Twenty native donor references freshly extracted')
        parent=args.base_manifest
        for name,module in [('classResources','native_class_resources'),('classes','generated_class_transport'),('portraits','generated_portrait_transport')]:
            parent=accept(name,importlib.import_module(module).build(parent,publish_current=False))
        parent=accept('actions',importlib.import_module('generated_action_transport').build(parent,publish_current=False,animation_plan=ROOT/'src/art/imagegen/samurai-refined-transport.json'))
        live=load_module('release_live_palette','build-live-art-palette.py');live.PARENT=parent
        parent=accept('livePalette',live.build(history_slots=20,all_classes=True,workspace_low_address=True,provisional_history=True,fast_rotation=True,
            owned_menu_buffer=True,shared_battle_menu_heap=True,compact_us_keyboard=True,compact_battle_status=True,publish_current=False,
            fast_bank_scan=True,fast_oam_plan=True,arm_oam_scan=True,scoped_frame=True,native_oam_prefix=True,native_owner_producer=True,fused_compose=True,native_reference_from_rom=True))
        connected=load_module('release_connect','build-connected-art.py').build(parent,publish_current=False,build_only=True)
        for name in ('status','equipment','weapon','effect'):accept(name,connected['components'][name])
        parent=ROOT/'build/art/connected'/connected['romSha1']/'manifest.json'
        complete=load_module('release_complete_actions','complete-generated-actions.py').build(parent,publish_current=False)
        accept('actionCompletion',complete['components']['actionCompletion']);parent=ROOT/'build/art/connected'/complete['romSha1']/'manifest.json'
        final=importlib.import_module('native_palette_transport').build(parent,publish_current=False)
        accept('nativePaletteTransport',final['components']['nativePaletteTransport'])
        check(final['romSha1']==recipe['candidateSha1'],'Complete rebuilt ROM matches accepted engineering candidate')
        report=dict(status='passed',checks=checks,recipeSha256=sha((ROOT/'notes/native-art-build-inputs.json').read_bytes()),romSha1=final['romSha1'],path=final['path'],manifest=str(ROOT/'build/art/connected'/final['romSha1']/'manifest.json'),scope=__doc__)
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report),flush=True)
    except Exception as error:
        (out/'failed.json').write_text(json.dumps(dict(status='failed',checks=checks,error=str(error),completedComponents=list(parts)),indent=2)+'\n',encoding='utf-8');raise

if __name__=='__main__':main()
