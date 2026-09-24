"""Apply compact skill names and revised Weapon Attack to the teaching-row build.

Data-only bounded patch. Each compact name is rewritten in place inside its
existing string (the only pointer to it is its Other-text entry) and must be
no wider than the longest original learned-ability name, eleven tiles. Weapon
Attack comes from notes/equipment-acquisition.json; every replaced value must
equal the recorded previous value. No code, pointer or other record changes.
"""
import datetime, hashlib, json, re, struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/expansion/equipment-revision'
OTHERS_LITERAL,ITEMS_LITERAL=0x2c08c,0x2b2a0
PUNCTUATION={' ':(0x40,0x73),'-':(0x81,0x0b),"'":(0x80,0xf4),'.':(0x80,0xe4),',':(0x80,0xec),':':(0x80,0xee),'/':(0x80,0xf1)}
def sha(raw):return hashlib.sha256(raw).hexdigest()

def encode(text):
    raw=[]
    for c in text:
        n=ord(c)
        if 65<=n<=90:raw+=[0x80,0xb0+n-65]
        elif 97<=n<=122:raw+=[0x80,0xca+n-97]
        elif 48<=n<=57:raw+=[0x80,0xa6+n-48]
        else:raw+=PUNCTUATION[c]
    return bytes(raw+[0])

def compact_names():
    source=(ROOT/'src/ability-display-names.mjs').read_text()
    pairs=re.findall(r"\['([A-Z0-9-]+)','([^']+)'\]",source)
    assert pairs and len({p[0] for p in pairs})==len(pairs)
    return dict(pairs),sha(source.encode())

def string_at(rom,offset):
    end=offset
    while rom[end]:end+=2
    return rom[offset:end+1]

def main():
    parent=Path(json.loads((ROOT/'build/expansion/teaching-rows/current.json').read_text())['manifest'])
    meta=json.loads(parent.read_text());original=Path(meta['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==meta['romSha1']
    registry=json.loads((ROOT/'build/expansion/registry.json').read_text())
    design=json.loads((ROOT/'notes/equipment-acquisition.json').read_text())
    compact,compact_sha=compact_names()
    lessons={l['id']:l for l in registry['lessons']}
    rom=bytearray(original);allowed=set();names=[];attacks=[]
    others=struct.unpack_from('<I',original,OTHERS_LITERAL)[0]-0x08000000
    for lesson_id,name in sorted(compact.items()):
        lesson=lessons[lesson_id];entry=others+lesson['nameId']*4
        address=struct.unpack_from('<I',original,entry)[0];offset=address-0x08000000
        before=string_at(original,offset);after=encode(name)
        if before==after:
            names.append(dict(lesson=lesson_id,name=name,offset=offset,status='already compact'));continue
        assert before==encode(lesson['name']),f'{lesson_id} installed name differs from design'
        assert len(after)<=len(before),f'{lesson_id} compact name longer than its string'
        references=[o for o in range(0,len(original)-3,4) if struct.unpack_from('<I',original,o)[0]==address]
        # Earlier build stages left superseded copies of the Other-text table;
        # a stale entry is acceptable only when nothing points at its table.
        stale=[r for r in references if r!=entry]
        assert entry in references and all(not any(struct.unpack_from('<I',original,o)[0]==r-lesson['nameId']*4+0x08000000
            for o in range(0,len(original)-3,4)) for r in stale),f'{lesson_id} string is shared: {references}'
        rom[offset:offset+len(before)]=after+bytes(len(before)-len(after))
        allowed|=set(range(offset,offset+len(before)))
        names.append(dict(lesson=lesson_id,full=lesson['name'],name=name,offset=offset,before=before.hex(),after=after.hex()))
    items=struct.unpack_from('<I',original,ITEMS_LITERAL)[0]-0x08000000
    by_name={i['name']:i for i in registry['items']}
    for item in design['items']:
        rom_id=by_name[item['name']]['romItemId'];record=items+rom_id*32
        previous=item.get('previousWeaponAttack',item['weaponAttack'])
        assert original[record+16]==previous and original[record+18]==item['magicPowerBonus'],item['name']
        if item['weaponAttack']!=previous:
            rom[record+16]=item['weaponAttack'];allowed.add(record+16)
            attacks.append(dict(item=rom_id,name=item['name'],offset=record+16,before=previous,after=item['weaponAttack']))
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    out=OUT/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    target=out/'FFTA_Reviewed_All_Classes.gba';target.write_bytes(rom)
    meta.update(path=str(target),romSha1=hashlib.sha1(rom).hexdigest(),romSha256=sha(rom))
    meta['equipmentRevision']=dict(parent=str(parent),baseSha1=hashlib.sha1(original).hexdigest(),names=names,attacks=attacks,
        compactNamesSha256=compact_sha,designSha256=sha((ROOT/'notes/equipment-acquisition.json').read_bytes()),
        othersTable=others+0x08000000,itemTable=items+0x08000000,changedBytes=len(allowed))
    manifest=out/'candidate.json';manifest.write_text(json.dumps(meta,indent=2)+'\n')
    (OUT/'current.json').write_text(json.dumps(dict(manifest=str(manifest)))+'\n')
    print(json.dumps(dict(status='passed',manifest=str(manifest),romSha1=meta['romSha1'],names=len(names),attacks=len(attacks))))

if __name__=='__main__':main()
