"""A/B one declared stalled native playback case with the old graphics pool."""
import pathlib,json,hashlib,runpy,os
ROOT=pathlib.Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'build/expansion/probes/integrated-jobs/current.json').read_text())
OUT=pathlib.Path(meta['path']).parent/'pool-diagnostic';OUT.mkdir(exist_ok=True)
image=bytearray(pathlib.Path(meta['path']).read_bytes());assert image[0x97098]==0xfa
image[0x97098]=0xf8;ROM=OUT/'pool-f8.gba';ROM.write_bytes(image)
candidate=dict(meta,path=str(ROM),romSha1=hashlib.sha1(image).hexdigest());manifest=OUT/'candidate.json';manifest.write_text(json.dumps(candidate,indent=2))
os.environ['FFTA_TEST_CANDIDATE']=str(manifest)
runpy.run_path(str(ROOT/'scripts/jobs/viking/prepare-battle.py'),run_name='__main__')
source=ROOT/'scripts/test-integrated-reaction-playback.py';code=source.read_text()
code=code.replace("ROOT/'build/expansion/probes/integrated-jobs/current.json'",repr(str(manifest)))
# Read_text still needs a Path after the exact manifest substitution.
code=code.replace('('+repr(str(manifest))+').read_text()', 'pathlib.Path('+repr(str(manifest))+').read_text()')
code=code.replace("[('SAM-R2',116,1,377,435),('VIK-R1',118,2,399,436),('DRK-R2',117,1,384,434)]", "[('SAM-R2',116,1,377,435)]")
code=code.replace('for enabled in (False,True):','for enabled in (False,):')
code=code.replace("((0,1,3,7,15,18) if lesson=='SAM-R2' else (0,3,18))",'(1,)')
code=code[:code.index("    check('nonvacuous-playback-")]
exec(compile(code,str(source),'exec'),{'__file__':str(source),'__name__':'pool_diagnostic'})
print(json.dumps(dict(passed=True,scope='Only SAM-R2 disabled, seed1 playback on diagnostic poolF8',romSha1=candidate['romSha1'])))
