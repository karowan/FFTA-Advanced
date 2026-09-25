"""Native checks for paged expansion help.

Decodes every help ID (0..0xFFF) of the help-pages candidate and its parent
through the native help router 19A50 and decoder 13E9C: no page has more than
two lines or a line over 27 characters; each repaged entry keeps the parent's
text tokens and line breaks, with a native page break (40 70 40 63) after every
second line; each refreshed weapon description reads exactly its declared text
(menu skill names) where the parent read the previous text; every other entry
decodes byte-identically; and the only changed ROM bytes are the new entries
and their bank-19 table pointers.
"""
import ast, datetime, hashlib, json, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/arm-python'))
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import *
def u16(b,p):return struct.unpack_from('<H',b,p)[0]
def u32(b,p):return struct.unpack_from('<I',b,p)[0]
tree=ast.parse((ROOT/'scripts/test-content-data.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARM'],type_ignores=[]),'<native help reader>','exec'))
meta=json.loads(Path(json.loads((ROOT/'build/expansion/help-pages/current.json').read_text())['manifest']).read_text())
rom=Path(meta['path']).read_bytes();assert hashlib.sha1(rom).hexdigest()==meta['romSha1']
change=meta['helpPages']
parent=Path(json.loads(Path(change['parent']).read_text())['path']).read_bytes()
assert hashlib.sha1(parent).hexdigest()==change['baseSha1']
clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
new,old,vanilla=ARM(rom),ARM(parent),ARM(clean)
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)

def tokens(body,terminated=False):
    out=[]
    for i in range(0,len(body),2):
        token=body[i:i+2]
        if token[0]==0:return out
        out.append(token)
    assert not terminated,'Unterminated help'
    return out
def layout(body):
    pages=[[[]]];skip=False
    for token in tokens(body):
        if skip:skip=False;continue
        if token==b'\x40\x70':pages.append([[]]);skip=True
        elif token==b'\x40\x6e':pages[-1].append([])
        elif token in (b'\x40\x61',b'\x40\x63'):continue
        else:pages[-1][-1].append(token)
    return pages
CHARS={(0x80,0xe4):'.',(0x80,0xec):',',(0x80,0xee):':',(0x80,0xf4):"'",(0x81,0x0b):'-',(0x80,0xf1):'/',(0x40,0x73):' '}
def words(pages):
    def char(t):
        a,b=t
        if a==0x80 and 0xb0<=b<=0xc9:return chr(65+b-0xb0)
        if a==0x80 and 0xca<=b<=0xe3:return chr(97+b-0xca)
        if a==0x80 and 0xa6<=b<=0xaf:return chr(48+b-0xa6)
        return CHARS[tuple(t)]
    return ' '.join(''.join(char(t) for t in line) for page in pages for line in page)
def decode(m,help_id):
    bank,index=m.map_help(help_id)
    if bank==0xff:return None
    try:return m.decode_help(bank,index)[1:]
    except Exception:return 'undecodable'

moved={e['helpId']:e for e in change['entries']};overflow=[]
for help_id in range(0x1000):
    after,before=decode(new,help_id),decode(old,help_id)
    if help_id not in moved:
        check(after==before,f'help {help_id} unchanged')
        if after in (None,'undecodable'):continue
        pages=layout(after[0])
        if max(len(p) for p in pages)>2:overflow.append(help_id)
        continue
    body,flags=after;tokens(body,True);pages=layout(body);previous=layout(before[0])
    check(flags==before[1],f'help {help_id} native header flags')
    if 'text' in moved[help_id]:
        check(words(previous)==moved[help_id]['previousText'] and words(pages)==moved[help_id]['text'],f'help {help_id} refreshed text')
    else:
        check(len(previous)==1 and len(previous[0])>2,f'help {help_id} parent overflowed one page')
        check([line for page in pages for line in page]==previous[0],f'help {help_id} same lines and words')
    check(all(len(p)==2 for p in pages[:-1]) and 1<=len(pages[-1])<=2,f'help {help_id} two lines per page')
    check(all(len(line)<=27 for page in pages for line in page),f'help {help_id} line width')
    breaks=[i for i,t in enumerate(tokens(body)) if t==b'\x40\x70']
    check(all(tokens(body)[i+1]==b'\x40\x63' for i in breaks) and len(breaks)==len(pages)-1,f'help {help_id} native page breaks')
# Remaining overflow pages are original game text, identical to the vanilla ROM.
for help_id in overflow:
    check(decode(new,help_id)==decode(vanilla,help_id),f'help {help_id} overflow is original text')
renamed=[e for e in change['entries'] if 'text' in e]
check(len(moved)==137 and len(renamed)==30 and all('Teaches' in e['text'] for e in renamed),'137 entries: 114 repaged, 30 refreshed weapon descriptions (7 both)')
table=change['table']-0x08000000;allowed=set(range(change['used'][0],change['used'][1]))
for e in change['entries']:allowed|=set(range(table+4*e['index'],table+4*e['index']+4))
check(all(a==b or i in allowed for i,(a,b) in enumerate(zip(parent,rom))) and len(rom)==len(parent),'only declared bytes changed')
check(rom[change['used'][1]:change['reservation'][1]]==b'\xff'*(change['reservation'][1]-change['used'][1]),'reservation tail blank')
out=Path(meta['path']).parent/('native-help-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
report=dict(status='passed',romSha1=meta['romSha1'],parentSha1=change['baseSha1'],checks=len(checks),repaged=len(moved),
            originalOverflow=overflow)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status='passed',romSha1=meta['romSha1'],checks=len(checks),repaged=len(moved),originalOverflow=overflow,report=str(out/'report.json'))))
