"""Combined asset rebuild and direct native consumers on the final ROM.

Reuse prior isolated transport evidence; check the new composition boundaries.
This does not prove battle timing, natural effect playback or final artwork.
"""
import ast,datetime,hashlib,json,runpy,struct,sys
from pathlib import Path
from native_art import ROOT,sha
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
UNIT,EQUIPMENT,RETURN,STACK=0x02000080,0x02002000,0x08000100,0x03007000
source=(ROOT/'scripts/test-equipment-legality.py').read_text().replace(
    'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)',
    'self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)\n        self.u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)')
tree=ast.parse(source)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<connected ARM>','exec'))
out=ROOT/'build/art/connected/native'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
checks=[];m=json.loads((ROOT/'build/art/connected/current.json').read_text())
def check(ok,label):
    assert ok,label
    checks.append(label)
try:
    rom=Path(m['path']).read_bytes();live=m['components']['livePalette'];base=Path(live['path']).read_bytes()
    check(hashlib.sha1(rom).hexdigest()==m['romSha1'] and hashlib.sha1(base).hexdigest()==live['romSha1'],'Final and palette-parent ROMs authenticated')
    assert sha(Path(m['sourcePaletteManifest']).read_bytes())==m['sourcePaletteManifestSha256']
    rebuild=runpy.run_path(str(ROOT/'scripts/build-connected-art.py'))['build']
    new=rebuild(m['sourcePaletteManifest'],publish_current=False,fixture_source=m['fixtureSource'])
    check(Path(new['path']).read_bytes()==rom,'All four added asset stages reproduce exact final ROM')
    iw=(Path(m['fixtureSource']).parent/'fixture/battle-ready.iwram').read_bytes()
    a,b=ARM(rom,iw),ARM(base,iw);weapon=m['components']['weapon'];effect=m['components']['effect']
    for resource in range(276):
        check(a.call(0x08021054,resource)==b.call(0x08021054,resource),'Existing native resource allocation '+str(resource))
    check(a.call(0x08021054,276)==b.call(0x08021054,128)==16,'Appended held axe native allocation')
    for item in range(461):
        for selector in (0,9):
            expected=276 if item in weapon['items'] and selector==9 else b.call(0x080ca7a4,item,selector)
            check(a.call(0x080ca7a4,item,selector)==expected,'Final native item identity/resource '+str((item,selector)))
    regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,
          UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12)
    for stack in (0x03007000,0x03006ffc):
        for action in (*range(461),65535):
            values=[0x66000000+i for i in range(13)];values[4]=0x02021000
            for reg,value in zip(regs,values):a.u.reg_write(reg,value)
            a.put(values[4]+16,struct.pack('<H',action));a.put(stack-16,b'\xa5'*40)
            a.u.reg_write(UC_ARM_REG_SP,stack);a.u.reg_write(UC_ARM_REG_LR,RETURN|1)
            stop=0x08000000+effect['hook']+8
            a.u.emu_start(0x08000001+effect['hook'],stop,count=100)
            label=str((stack,action))
            check(a.u.reg_read(UC_ARM_REG_PC)==stop and a.u.reg_read(UC_ARM_REG_R1)==0x08000000+(effect['table'] if action==425 else effect['originalTable']),label+' scoped effect selector/continuation')
            check(all(a.u.reg_read(r)==v for r,v in zip(regs[2:],values[2:])),label+' live registers preserved')
            check(a.u.reg_read(UC_ARM_REG_SP)==stack and a.read(stack,8)==struct.pack('<2I',values[3],values[10]) and a.read(stack-16,16)==b'\xa5'*16 and a.read(stack+8,16)==b'\xa5'*16,label+' original stack stores/fences')
    for name in ('status','equipment','weapon','effect'):
        component=m['components'][name];own=Path(component['path']).read_bytes()
        ranges=[(component['offset'],component['offset']+component['bytes'])] if name=='status' else [component['used']]
        for lo,hi in ranges:check(rom[lo:hi]==own[lo:hi],name+' final payload/module exact')
        check(sha((ROOT/component['sourceArt']).read_bytes())==component['sourceArtSha256'],name+' authenticated existing imagegen source')
    report=dict(status='passed',romSha1=m['romSha1'],checks=checks,
        scope='Final connected ROM exact asset-stage rebuild, all276 prior allocation getters plus appended axe,461 item identity/resource selectors, all461 action IDs andFFFF at two stack residues through effect hook with ABI/canaries, final payloads/source art authenticated. No natural effect/battle timing or final-art acceptance.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(out/'report.json'))))
except Exception as error:
    (out/'failed.json').write_text(json.dumps(dict(status='failed',romSha1=m['romSha1'],error=str(error),checks=checks),indent=2)+'\n',encoding='utf-8')
    print('Artifacts: '+str(out));raise
