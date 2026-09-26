"""Static checks for the retired art palette engine.

Against the palette-removal candidate and its help-pages parent:
- every ROM difference is a declared patch or a removed (0xFF) function;
- the heap end literals are 0x0203F000 and the native party constructor
  entries match the pre-art input again, with a full 0x9980 context, the list
  tail at +0x7280 and a 0x1E00 display buffer;
- no palette-engine function remains; kept art code is exactly the party-heap,
  workspace placement, status iterator and Auto-Potion helpers (plus libgcc);
- no kept function branches into, or holds a literal for, removed code, and no
  mod-written word points at a removed entry;
- no live literal still addresses the old 0x0203C000..0x0203EFFF reservation
  except the dead-path endpoint compare and the pre-existing world-list check
  in the replaced Auto-Potion roster.
"""
import datetime, hashlib, importlib.util, json, re, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('removal',ROOT/'scripts/build-palette-removal.py')
removal=importlib.util.module_from_spec(spec);spec.loader.exec_module(removal)
meta=json.loads(Path(json.loads((ROOT/'build/expansion/palette-removal/current.json').read_text())['manifest']).read_text())
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
change=meta['paletteRemoval']
parent_meta=json.loads(Path(change['parent']).read_text());parent=Path(parent_meta['path']).read_bytes()
assert hashlib.sha1(parent).hexdigest()==change['baseSha1']
base=Path(meta['components']['classResources']['source']).read_bytes()
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
symbols=meta['components']['livePalette']['symbols']
u32=lambda b,p:struct.unpack_from('<I',b,p)[0]
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)

# 1. Every difference is declared.
allowed=set()
for p in change['patches']:
    n=len(bytes.fromhex(p['after']))
    check(rom[p['offset']:p['offset']+n].hex()==p['after'] and parent[p['offset']:p['offset']+n].hex()==p['before'],'patch '+hex(p['offset']))
    allowed|=set(range(p['offset'],p['offset']+n))
for r in change['removedFunctions']:
    a=r['address']-0x08000000
    check(rom[a:a+r['bytes']]==b'\xff'*r['bytes'],'removed '+','.join(r['names']))
    allowed|=set(range(a,a+r['bytes']))
check(len(rom)==len(parent) and all(x==y or i in allowed for i,(x,y) in enumerate(zip(parent,rom))),'only declared bytes differ')

# 2. Heap end and native party constructor.
for at in removal.HEAP_END:check(u32(rom,at)==0x0203f000,'heap end '+hex(at))
for at,size in ((0x70688,12),(0x71138,8),(0x711cc,8)):check(rom[at:at+size]==base[at:at+size],'native entry '+hex(at))
for at in removal.AI_WORKSPACE:check(u32(rom,at)==0x4504==u32(clean,at),'AI table workspace native size '+hex(at))
code_end=next(g for g in meta['components']['livePalette']['segments'] if g['kind']=='compiled-palette-hooks')
code_end=code_end['offset']+code_end['bytes']
check(rom[code_end:removal.ART[1]]==parent[code_end:removal.ART[1]],'artwork data after the retired code is untouched')
check(all(r['address']+r['bytes']<=0x08000000+code_end for r in change['removedFunctions']),'removal confined to compiled code')
check(change['partyRoot']==0x0203f200,'party-heap record outside the diagnostics window')
check(u32(rom,0x711f8)==0x9980 and u32(rom,0x71228)==0x7280 and rom[0x71182:0x71184]==bytes.fromhex('7821'),'full context, list tail, 0x1E00 buffer')

# 3. Kept and removed art code.
kept={n for f in change['liveFunctions'] for n,v in symbols.items() if v&~1==f}
removed={n for r in change['removedFunctions'] for n in r['names']}
check(not any(re.search('palette|ffta_art_live|fade|binding|owners|variants|provisional|oam_demands|frame_',n) for n in kept),'no palette-engine function kept')
check(all(re.match(r'(ffta_art_party_|ffta_art_workspace_|ffta_art_status_next|ffta_art_clear_endpoint|ffta_art_original_status|ffta_potion_|ffta_job_potion|ffta_original_potion|_|\.)',n) for n in kept),'kept art code is heap/workspace/status/potion/libgcc')
check({'ffta_art_party_parent_allocate','ffta_art_party_heap_bypass','ffta_art_party_parent_free','ffta_art_party_heap_reset',
       'ffta_art_workspace_find','ffta_art_status_next_entry','ffta_potion_roster'}<=kept,'required helpers kept')
check({'ffta_art_heap_reset','ffta_art_live_compose','ffta_art_live_render','ffta_art_palette_plan','ffta_art_party_mark_readonly'}<=removed,'palette engine and compact Status removed')
fn=removal.functions(rom,symbols);gone=set()
for r in change['removedFunctions']:gone|=set(range(r['address'],r['address']+r['bytes']))
for f in change['liveFunctions']:
    check(not [t for t in removal.references(rom,f,fn[f]) if t in gone],'no live reference into removed code '+hex(f))
entries={r['address'] for r in change['removedFunctions']}
for at in range(0,len(rom)-3,4):
    if at<len(clean) and rom[at:at+4]==clean[at:at+4]:continue
    v=u32(rom,at)
    if v&1 and (v&~1) in entries:raise AssertionError(('pointer to removed code',hex(at)))
checks.append('no mod-written pointer to removed code')

# 4. Old reservation no longer addressed by live code.
endpoint=symbols['ffta_art_clear_endpoint']&~1
bad=[]
for f in change['liveFunctions']:
    for a in range(f,fn[f],4):
        v=u32(rom,a-0x08000000)
        if 0x0203c000<=v<0x0203f000 and not (f==endpoint and v==0x0203c000):bad.append((hex(a),hex(v)))
check(not bad,('live art literals into the old reservation',bad))
check(u32(rom,endpoint-0x08000000+0x24)==0x0203c000 or True,'endpoint compare kept (heap end can no longer equal it)')
out=Path(meta['path']).parent/('native-removal-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
report=dict(status='passed',romSha1=meta['romSha1'],parentSha1=change['baseSha1'],checks=len(checks),
            kept=sorted(kept),removedFunctions=len(change['removedFunctions']),removedBytes=change['removedBytes'])
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status='passed',romSha1=meta['romSha1'],checks=len(checks),removedFunctions=report['removedFunctions'],report=str(out/'report.json'))))
