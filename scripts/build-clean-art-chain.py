"""Rebuild all existing generated transports from a verified fresh source base.

Temporary imagegen pixels are authenticated inputs, not regenerated artwork.
No current component pointer, shipping build, launcher or player save changes.
"""
import datetime,hashlib,importlib,json
from pathlib import Path
from native_art import ROOT,sha

REBUILD=ROOT/'build/reproducibility/20260917T225624.978478Z/report.json'
EXPECTED='37afe0a7be1b80355d395d3d10685a9034b123d1'

def build():
    root=ROOT/'build/art/clean-chain';out=root/'runs'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    checks=[];components={}
    def check(ok,label):
        assert ok,label
        checks.append(label)
    pointers=[ROOT/'build/art'/name/'current.json' for name in ('class-resources','generated-classes','generated-portraits','generated-actions','generated-status','generated-equipment')]
    pointers.append(ROOT/'build/expansion/probes/integrated-jobs/current.json')
    originals={str(p):p.read_bytes() for p in pointers}
    try:
        rebuild=json.loads(REBUILD.read_text());check(rebuild['passed'] and len(rebuild['steps'])==8,'Verified fresh eight-stage build')
        original_manifest=Path(rebuild['result']['manifest']);base=json.loads(original_manifest.read_text());rom=Path(base['path']).read_bytes()
        check(sha(original_manifest.read_bytes())==rebuild['result']['manifestSha256'],'Authenticated clean-base manifest')
        check(hashlib.sha1(rom).hexdigest()==base['romSha1']==rebuild['result']['romSha1']=='5065a9eaadd5de1094a38c8724d3d9d308e1194f','Authenticated fresh base bytes')
        # A durable private input survives normal pruning of full toolchain
        # workspaces. This copies a verified build, never a player save.
        parent=root/'input'/base['romSha1'];parent.mkdir(parents=True,exist_ok=True)
        basepath=parent/'integrated.gba';basepath.write_bytes(rom);base['path']=str(basepath)
        base['sourceRebuild']=dict(report=str(REBUILD),sha256=sha(REBUILD.read_bytes()))
        manifest=parent/'manifest.json';manifest.write_text(json.dumps(base,indent=2)+'\n')
        from equipment_preview import remove_owned,START,END,HOOKS
        prior=dict(next(c for c in base['changes'] if c['kind']=='Paged native equipment preview'))
        prior['binarySha256']=sha(rom[START:START+prior['bytes']])
        for label,position in [('module byte',START+32),('hook byte',HOOKS[0][0]),('unowned tail',END-1)]:
            bad=bytearray(rom);bad[position]^=1;unchanged=bytes(bad)
            try:remove_owned(bad,prior)
            except AssertionError:pass
            else:raise AssertionError('Accepted conflicting '+label)
            check(bytes(bad)==unchanged,label+' conflict rejected before mutation')
        modules=[('classResources','native_class_resources'),('classes','generated_class_transport'),('portraits','generated_portrait_transport'),
                 ('actions','generated_action_transport'),('status','generated_status_transport'),('equipment','generated_equipment_transport')]
        for name,module in modules:
            print('Building explicit clean-base art stage: '+name,flush=True)
            component=importlib.import_module(module).build(manifest,publish_current=False)
            check(hashlib.sha1(Path(component['path']).read_bytes()).hexdigest()==component['romSha1'],name+' source stage authenticated')
            components[name]=component;manifest=Path(component['path']).parent/'manifest.json'
        result=Path(components['equipment']['path']).read_bytes()
        repaired=json.loads((ROOT/'build/art/native-repair-complete/current.json').read_text())
        reference=Path(repaired['path']).read_bytes()
        check(repaired['romSha1']==EXPECTED and hashlib.sha1(reference).hexdigest()==EXPECTED,'Authenticated independently repaired reference')
        # The all17-axe dispatcher deliberately extends the former8-item
        # dispatcher. All other clean-derived bytes must remain exact.
        check(len(reference)==len(result) and reference[:0xcb984]==result[:0xcb984]
            and reference[0xcb988:0x1f80000]==result[0xcb988:0x1f80000]
            and reference[0x1f84000:]==result[0x1f84000:],'Six clean-derived stages match repaired reference outside declared equipment module/hook')
        check(all(Path(p).read_bytes()==raw for p,raw in originals.items()),'Historical component/current release pointers unchanged')
        components['preview']=components['classes']['preview']
        digest=hashlib.sha1(result).hexdigest()
        report=dict(schema=1,status='passed',path=components['equipment']['path'],romSha1=digest,romSha256=sha(result),checks=checks,
            source=str(basepath),baseRomSha1=base['romSha1'],components=components,sourceRebuild=base['sourceRebuild'],
            fixtureSource=repaired['releaseSource'],
            scope='Six explicit imagegen transport stages build from fresh source-assembled corrected base; authenticated owned-preview replacement. Exact repaired-reference equality outside declared all17-axe dispatcher/module. Original source images/conversion inputs reused, not regenerated. Final artwork, remaining native consumers and full playable-package acceptance stay open.')
        for p in (out/'report.json',root/'current.json'):p.write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(dict(status='passed',checks=len(checks),romSha1=digest,report=str(out/'report.json'))));return report
    except Exception as error:
        (out/'failed.json').write_text(json.dumps(dict(status='failed',error=str(error),checks=checks,components=components),indent=2)+'\n')
        print('Artifacts: '+str(out));raise

if __name__=='__main__':build()
