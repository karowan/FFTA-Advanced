"""Real-core battle help paging: Holy Ench. help shows its third line.

Creates a disposable Giza battle fixture on the help-pages candidate with
scripts/fixtures/enchant-sniper-profile.json (Viera Sniper, secondary
Spellblade, all fourteen actions learned). Fixed inputs: other units Wait; the
Sniper opens Spellblade, moves to Holy Ench. and presses Select for help. The
native help window shows page one (the same two lines as the parent ROM) and
waits; A shows page two (the former third line) and A again closes help, as
with original multi-page help, without leaving the list. On the parent ROM the
first A closed help, so the third line was never visible. Pixels are compared
inside the help window.
"""
import datetime, hashlib, json, runpy, struct, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from native_battle_wrappers import fixed_giza_formation
meta=json.loads(Path(json.loads((ROOT/'build/expansion/help-pages/current.json').read_text())['manifest']).read_text())
parent=json.loads(Path(meta['helpPages']['parent']).read_text())
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
observe=runpy.run_path(str(ROOT/'scripts/battle-menu-observation.py'))
ACTOR=0x5a8;DOWN,A,SELECT=32,256,4
HOLY_ROW=10;WINDOW=(8,4,232,52)   # native help window, GBA pixels
word=lambda r,p:struct.unpack_from('<I',r,p)[0]
checks=[];inputs=[]
def check(ok,label):
    assert ok,label
    checks.append(label)

def window(e):
    raw,w,h,pitch,pixel=e.frame;x0,y0,x1,y1=WINDOW
    return hashlib.sha1(b''.join(bytes(raw[y*pitch+x0*(4 if pixel==1 else 2):y*pitch+x1*(4 if pixel==1 else 2)]) for y in range(y0,y1))).hexdigest()

def observe_help(rom_meta,label,out):
    rom_path=Path(rom_meta['path']);rom=rom_path.read_bytes();assert hashlib.sha1(rom).hexdigest()==rom_meta['romSha1']
    fix=out/f'{label}-fixture'
    subprocess.run([sys.executable,str(ROOT/'scripts/create-battle-fixture.py'),'--rom',str(rom_path),'--out',str(fix),
        '--party-profile',str(ROOT/'scripts/fixtures/enchant-sniper-profile.json'),'--confirm-pub-exit','--heap-end','0x0203c000'],
        check=True,capture_output=True)
    e=E(fix/'frozen.gba')
    def active():
        r=e.memory();p=word(r,0xf438)-0x02000000
        return word(r,p+24) if 0<=p<len(r)-28 else 0
    def tap(key,wait=180,name=None):
        e.run(8,key);e.run(wait);inputs.append([label,key,wait,name])
        if name:e.screenshot(out/f'{label}-{name}.png')
    try:
        e.load(fix/'battle-ready.state');e.run(1);observe['wait_for_menu'](e);fixed_giza_formation(rom,e)
        for _ in range(12):
            if active()==0x02000000+ACTOR:break
            previous=active()
            for key in (DOWN,DOWN,A,A):tap(key)
            for _ in range(0,6300,30):
                if active()!=previous and observe['menu_visible'](e):break
                e.run(30)
        check(active()==0x02000000+ACTOR,f'{label}: Sniper owns the native turn')
        tap(DOWN,120);tap(A,180);tap(DOWN,90);tap(DOWN,90);tap(A,180,'abilities')
        for _ in range(HOLY_ROW):tap(DOWN,60)
        tap(SELECT,60,'help-open');first=window(e)
        state=lambda:((r:=e.memory())[word(r,0xf438)-0x02000000+4],struct.unpack_from('<H',r,0xf3fc)[0])
        listing=state()
        for _ in range(0,600,15):
            e.run(15);check(window(e)==first,f'{label}: help page waits for input')
        tap(A,90,'help-A');second=window(e);afterA=state()
        tap(A,90,'help-AA');third=window(e)
        check(afterA==listing,f'{label}: help input keeps the ability list and selection')
        return dict(first=first,second=second,third=third,listing=listing,afterSecondA=state())
    finally:e.close()

out=Path(meta['path']).parent/('ui-help-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
paged=observe_help(meta,'paged',out);old=observe_help(parent,'parent',out)
check(paged['first']==old['first'],'page one shows the same first two lines')
check(old['second']!=old['first'],'parent: A closes the one-page help; the third line was never shown')
check(paged['second'] not in (paged['first'],old['second']),'A shows page two')
check(paged['third']==old['second'] and paged['afterSecondA']==paged['listing'],'A on the last page closes help, still in the list')
report=dict(status='passed',romSha1=meta['romSha1'],parentSha1=parent['romSha1'],checks=checks,paged=paged,parent=old,inputs=inputs)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status='passed',romSha1=meta['romSha1'],checks=len(checks),report=str(out/'report.json'))))
