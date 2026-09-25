"""Page long expansion help into the native two-line help window.

Also refreshes the 85 expansion weapon descriptions ("X. Teaches A, B.") to
the skill names shown in menus (src/ability-display-names.mjs), keeping the
full name where the menu name only abbreviates it (Counter Rhy.).

Bounded patch on the enchant-weapons build. The native help window shows two
lines; original descriptions with more text continue on another page after the
native page break 40 70 40 63 (e.g. Phoenix Down: "...KO'd unit." / "Deals
damage to zombies."). Expansion help was encoded as up to three lines on one
page, so the third line was never shown. Every uncompressed expansion entry in
help bank 19 whose page has more than two lines is rewritten with the same
lines, two per page, in blank ROM 0x1FF4000..0x1FFBFFF, and its table pointer is
repointed. Header, terminator, wrapping and (except refreshed skill names) words
are unchanged.
"""
import ast, datetime, hashlib, json, struct, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
OUT=ROOT/'build/expansion/help-pages'
START,END=0x1ff4000,0x1ffc000
BANK,BANKS=19,0x36d678
HEADER,NEWLINE,PAGE,TERMINATOR=b'\x28\x18',b'\x40\x6e',b'\x40\x70\x40\x63',b'\x40\x61\x40\x63\x00'
def u16(b,p):return struct.unpack_from('<H',b,p)[0]
def u32(b,p):return struct.unpack_from('<I',b,p)[0]
tree=ast.parse((ROOT/'scripts/test-content-data.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native help reader>','exec'))

def tokens(raw):
    """Two-byte text tokens of an uncompressed expansion entry, header excluded."""
    assert raw[:2]==HEADER
    out=[];i=2
    while raw[i:i+5]!=TERMINATOR:
        token=raw[i:i+2];assert len(token)==2 and token[0] in (0x40,0x80,0x81) and token!=PAGE[:2],raw[:i+2].hex()
        out.append(token);i+=2
    return out,i+5

def pages(raw):
    """Lines per page of a native help body (decoded or raw, header excluded)."""
    result=[1];i=0
    while True:
        token=raw[i:i+2]
        if token==b'\x40\x61' or token[:1]==b'\x00':return result
        if token==NEWLINE:result[-1]+=1
        if token==b'\x40\x70':result.append(1);i+=2
        i+=2

def repage(raw):
    body,size=tokens(raw);lines=[[]]
    for token in body:
        if token==NEWLINE:lines.append([])
        else:lines[-1].append(token)
    groups=[lines[i:i+2] for i in range(0,len(lines),2)]
    text=PAGE.join(NEWLINE.join(b''.join(line) for line in group) for group in groups)
    return HEADER+text+TERMINATOR,size

def encode_help(texts):
    """encodeHelp (27-character lines, one page) for each text, via Node."""
    script=("import('./src/rom-builder.mjs').then(m=>{const t=JSON.parse(require('fs').readFileSync(0,'utf8'));"
            "process.stdout.write(JSON.stringify(t.map(x=>m.encodeHelp(x).toString('hex'))))})")
    return [bytes.fromhex(h) for h in json.loads(subprocess.run(['node','-e',script],cwd=ROOT,input=json.dumps(texts),
            capture_output=True,text=True,check=True).stdout)]

def teaching_texts():
    """Installed and refreshed weapon descriptions by help ID."""
    script="import('./src/ability-display-names.mjs').then(m=>process.stdout.write(JSON.stringify([...m.abilityDisplayNames])))"
    shown=dict(json.loads(subprocess.check_output(['node','-e',script],cwd=ROOT,text=True)))
    registry=json.loads((ROOT/'build/expansion/registry.json').read_text());items={i['romItemId']:i for i in registry['items']}
    profiles=json.loads((ROOT/'build/expansion/probes/content-data.json').read_text())['itemProfiles'];texts={}
    for profile in profiles:
        item=items[profile['id']];names=[]
        for lesson in item['lessons']:
            name=shown.get(lesson['id'],lesson['name'])
            if name.endswith('.') and lesson['name'].startswith(name[:-1]):name=lesson['name']   # abbreviation only
            names.append(name)
        assert profile['helpText']==item['name']+'. Teaches '+', '.join(l['name'] for l in item['lessons'])+'.',profile['id']
        refreshed=item['name']+'. Teaches '+', '.join(names)
        texts[profile['helpId']]=(profile['helpText'],refreshed if refreshed.endswith('.') else refreshed+'.')
    return texts

def help_routes(m,limit=0x1000):
    routes={}
    for help_id in range(limit):
        bank,index=m.map_help(help_id)
        if bank==BANK:routes[help_id]=index
    return routes

def main():
    parent=Path(json.loads((ROOT/'build/expansion/enchant-weapons/current.json').read_text())['manifest'])
    meta=json.loads(parent.read_text());original=Path(meta['path']).read_bytes()
    assert hashlib.sha1(original).hexdigest()==meta['romSha1']
    assert original[START:END]==b'\xff'*(END-START),'Help-page reservation occupied'
    m=ARM(original);table=u32(original,BANKS+BANK*4)-0x08000000
    rom=bytearray(original);cursor=START;moved={};entries=[];allowed=set()
    teaching=teaching_texts();ids=sorted(teaching)
    encoded=dict(zip(ids,zip(encode_help([teaching[i][0] for i in ids]),encode_help([teaching[i][1] for i in ids]))))
    for help_id,index in sorted(help_routes(m).items()):
        slot=table+4*index;address=u32(original,slot)
        if address>>25!=4:continue
        at=address-0x08000000
        if original[at:at+2]!=HEADER:continue
        _,decoded,flags=m.decode_help(BANK,index)
        body,size=tokens(original[at:])
        assert decoded[:size-2]==original[at+2:at+size],help_id   # native reader yields these bytes
        installed=original[at:at+size];text=None
        if help_id in encoded:
            before,after=encoded[help_id];assert installed==before,('Installed weapon help differs',help_id)
            if after!=before:installed=after;text=teaching[help_id][1]
        if text is None and max(pages(installed[2:]))<=2:continue
        assert address not in moved or text is None,'Shared entry with refreshed text'
        if address not in moved or text is not None:
            new,_=repage(installed)
            assert max(pages(new[2:]))<=2
            cursor=(cursor+3)&~3;assert cursor+len(new)<=END,'Help-page reservation exhausted'
            rom[cursor:cursor+len(new)]=new;allowed|=set(range(cursor,cursor+len(new)))
            moved[address]=(cursor+0x08000000,len(new));cursor+=len(new)
        struct.pack_into('<I',rom,slot,moved[address][0]);allowed|=set(range(slot,slot+4))
        entries.append(dict(helpId=help_id,index=index,previous=address,address=moved[address][0],
                            pages=pages(bytes(rom[moved[address][0]-0x08000000+2:])),
                            **(dict(previousText=teaching[help_id][0],text=text) if text else {})))
    assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,rom)))
    out=OUT/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    target=out/'FFTA_Reviewed_All_Classes.gba';target.write_bytes(rom)
    meta.update(path=str(target),romSha1=hashlib.sha1(rom).hexdigest(),romSha256=hashlib.sha256(rom).hexdigest())
    meta['helpPages']=dict(parent=str(parent),baseSha1=hashlib.sha1(original).hexdigest(),reservation=[START,END],
                           used=[START,cursor],bank=BANK,table=table+0x08000000,entries=entries)
    manifest=out/'candidate.json';manifest.write_text(json.dumps(meta,indent=2)+'\n')
    (OUT/'current.json').write_text(json.dumps(dict(manifest=str(manifest)))+'\n')
    print(json.dumps(dict(status='passed',manifest=str(manifest),romSha1=meta['romSha1'],entries=len(entries),renamed=sum('text' in e for e in entries),
                          texts=len(moved),bytes=cursor-START)))

if __name__=='__main__':main()
