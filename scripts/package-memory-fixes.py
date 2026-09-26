"""Authenticate the 0.7.3 acceptance run (palette engine retired, RAM audit
fixes), then publish the generic BPS release.

The run must be exactly scripts/memory-fixes-test-plan.json. The released game
is the item-icons candidate built in that run on its own memory-fixes,
palette-removal, help-pages, enchant-weapons, equipment-revision and
teaching-row parents.
"""
import argparse, hashlib, json
from pathlib import Path
from mod_release import publish
ROOT=Path(__file__).resolve().parents[1]
STEPS=('build-teaching-rows','build-equipment-revision','test-equipment-revision',
       'build-enchant-weapons','test-enchant-weapons','test-enchant-weapons-ui',
       'build-help-pages','test-help-pages','test-help-pages-ui','build-palette-removal',
       'test-palette-removal','test-palette-removal-teaching-rows','test-palette-removal-teaching-rows-ui',
       'test-palette-removal-ui','build-memory-fixes','test-memory-fixes','build-item-icons','test-item-icons',
       'test-item-icons-ui','test-memory-fixes-ui','test-memory-fixes-removal-ui','test-memory-fixes-enchant-ui',
       'test-action-sweep','test-game-pass','test-game-pass-reactions-a1','test-game-pass-reactions-a2',
       'test-game-pass-reactions-b1','test-game-pass-reactions-b2')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def last(log):return json.loads(Path(log).read_text().splitlines()[-1])
def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--config',type=Path,default=ROOT/'scripts/mod-release.json');a=p.parse_args()
    run=json.loads(a.run.read_text());assert run['status']=='passed' and run['inputsUnchanged']
    assert tuple(s['id'] for s in run['steps'])==STEPS and all(s['status']=='passed' for s in run['steps'])
    steps={s['id']:s for s in run['steps']}
    rows=last(steps['build-teaching-rows']['log']);revision=last(steps['build-equipment-revision']['log'])
    enchant=last(steps['build-enchant-weapons']['log']);pages=last(steps['build-help-pages']['log'])
    removal=last(steps['build-palette-removal']['log']);fixes=last(steps['build-memory-fixes']['log'])
    built=last(steps['build-item-icons']['log'])
    path=Path(built['manifest']);meta=json.loads(path.read_text())
    rom=Path(meta['path']).read_bytes();digest=hashlib.sha1(rom).hexdigest()
    assert digest==meta['romSha1']==built['romSha1']
    # Parent chain produced in this run: rows -> revision -> enchant -> help pages -> removal -> fixes.
    assert Path(meta['itemIcons']['parent'])==Path(fixes['manifest']) and meta['itemIcons']['baseSha1']==fixes['romSha1']
    fixes_meta=json.loads(Path(fixes['manifest']).read_text())
    assert Path(fixes_meta['memoryFixes']['parent'])==Path(removal['manifest']) and fixes_meta['memoryFixes']['baseSha1']==removal['romSha1']
    removal_meta=json.loads(Path(removal['manifest']).read_text())
    assert Path(removal_meta['paletteRemoval']['parent'])==Path(pages['manifest']) and removal_meta['paletteRemoval']['baseSha1']==pages['romSha1']
    pages_meta=json.loads(Path(pages['manifest']).read_text())
    assert Path(pages_meta['helpPages']['parent'])==Path(enchant['manifest']) and pages_meta['helpPages']['baseSha1']==enchant['romSha1']
    enchant_meta=json.loads(Path(enchant['manifest']).read_text())
    assert Path(enchant_meta['enchantWeapons']['parent'])==Path(revision['manifest'])
    assert enchant_meta['enchantWeapons']['baseSha1']==revision['romSha1']
    revision_meta=json.loads(Path(revision['manifest']).read_text())
    assert Path(revision_meta['equipmentRevision']['parent'])==Path(rows['manifest'])
    assert revision_meta['equipmentRevision']['baseSha1']==rows['romSha1']
    rows_meta=json.loads(Path(rows['manifest']).read_text())
    for source,expected in {**rows_meta['teachingRows']['sourceSha256'],**enchant_meta['enchantWeapons']['sourceSha256'],
                            **meta['memoryFixes']['sourceSha256'],**meta['itemIcons']['sourceSha256']}.items():
        assert sha(ROOT/source)==expected,source
    assert sha(ROOT/'src/ability-display-names.mjs')==revision_meta['equipmentRevision']['compactNamesSha256']
    assert sha(ROOT/'notes/equipment-acquisition.json')==revision_meta['equipmentRevision']['designSha256']
    stage_rom={'build-teaching-rows':rows['romSha1'],'build-equipment-revision':revision['romSha1'],
               'test-equipment-revision':revision['romSha1'],'build-enchant-weapons':enchant['romSha1'],
               'test-enchant-weapons':enchant['romSha1'],'test-enchant-weapons-ui':enchant['romSha1'],
               'build-help-pages':pages['romSha1'],'test-help-pages':pages['romSha1'],'test-help-pages-ui':pages['romSha1'],
               **{k:removal['romSha1'] for k in ('build-palette-removal','test-palette-removal','test-palette-removal-teaching-rows',
                                                   'test-palette-removal-teaching-rows-ui','test-palette-removal-ui')},
               'build-memory-fixes':fixes['romSha1'],'test-memory-fixes':fixes['romSha1']}
    assert sha(ROOT/'src/art/imagegen/new-item-icons-approved.json')==meta['itemIcons']['receiptSha256']
    evidence=[]
    for step in run['steps']:
        entry=last(step['log']);assert entry['status']=='passed',step['id']
        assert entry['romSha1']==stage_rom.get(step['id'],digest),step['id']
        report=Path(entry.get('report',entry.get('manifest')))
        if 'report' in entry:
            proof=json.loads(report.read_text());assert proof['status']=='passed' and proof['romSha1']==entry['romSha1'],step['id']
        evidence.append(dict(id=step['id'],path=str(report),sha256=sha(report),log=str(step['log']),logSha256=sha(Path(step['log']))))
    protected={str(f):sha(f) for base in (ROOT/'saves/native-art-final-2026-09-20',ROOT/'roms/play',ROOT/'build/releases/approved-first-pass',ROOT/'build/releases/native-art-final')
               if base.exists() for f in base.rglob('*') if f.is_file()}
    package=publish(meta,a.run,evidence,a.config)
    for f,d in protected.items():assert sha(Path(f))==d,f
    package.update(run=str(a.run.resolve()),runSha256=sha(a.run),reports=evidence,protectedFiles=protected)
    receipt=Path(package['archive']).parent/'local-build-receipt.json'
    receipt.write_text(json.dumps(package,indent=2)+'\n')
    print(json.dumps(dict(status='passed',romSha1=digest,protectedFiles=len(protected),archive=package['archive'],archiveBytes=package['archiveBytes'],patchBytes=package['patchBytes'],report=str(receipt))))
if __name__=='__main__':main()
