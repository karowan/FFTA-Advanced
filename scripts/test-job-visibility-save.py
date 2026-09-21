"""Fixed-input wheel and native save/cold Continue using a disposable old save."""
import ctypes as C, hashlib, json, runpy, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
meta=json.loads(Path(json.loads((ROOT/'build/expansion/job-visibility/current.json').read_text())['manifest']).read_text())
out=Path(meta['path']).parent/'save-test';out.mkdir()
ROM=Path(meta['path']);assert hashlib.sha1(ROM.read_bytes()).hexdigest()==meta['romSha1']
seedpath=ROOT/'build/test-lab/early-town.sav';seed=seedpath.read_bytes()
E=runpy.run_path(str(ROOT/'scripts/emulator-test.py'))['Emulator']
checks=[];inputs=[];captures=[];e=None
def check(ok,label):
    assert ok,label
    checks.append(label)
def tap(key,wait=180):inputs.append([8,key,wait]);e.run(8,key);e.run(wait)
def cold(saved):
    global e
    e=E(ROM);e.set_memory(0,saved,0);e.run(3600)
    for key in (8,256,256,256):tap(key,300)
def open_wheel():
    for index,key in enumerate([8,256,256,32,32]):
        tap(key)
        e.screenshot(out/('navigation-'+str(len(inputs))+'-'+str(index)+'.png'))
    tap(256,600)
def close_wheel():
    for key in [1,1,1]:tap(key,240)
def capture(name):
    ram=e.memory();iw=C.string_at(*e.maps[0x03000000]);p=struct.unpack_from('<I',iw,0x2818)[0]-0x02000000
    n=struct.unpack_from('<I',ram,p+0x1270)[0]
    e.save(out/(name+'.state'))
    check(0<n<=12,name+' bounded count '+str((hex(p),n,ram[p+0x1258:p+0x1260].hex())))
    rows=list(ram[p+0x1278:p+0x1278+n]);e.screenshot(out/(name+'.png'))
    (out/(name+'.ram')).write_bytes(ram);(out/(name+'.iwram')).write_bytes(iw)
    captures.append(dict(name=name,rows=rows,discovery=list(ram[0x1e7a:0x1e7c])))
    return rows
try:
    cold(seed);check(e.memory()[0x1e70:0x1e79]==b'FFTAEXP1\x01','old save loaded/migrated in current game')
    check(e.memory()[0x1e7a:0x1e7c]==bytes(2),'old save unused discovery bytes zero')
    original_units=e.memory()[0x80:0x1940]
    open_wheel();rows=capture('01-unseen-hidden')
    check(all(x&127<116 for x in rows),'undiscovered Human jobs absent from rendered wheel')
    close_wheel()
    # Existing deterministic AP setup exposes the two Human jobs. No player
    # save is opened and no live desktop process is controlled.
    e.set_memory(0xc0,bytes([100])*142);e.set_memory(0x1b40,bytes([100])*34)
    open_wheel();capture('02-qualified-page1');tap(2048,600);rows=capture('03-qualified-page2')
    check(244 in rows and 245 in rows,'both qualified additions selectable on page two')
    check(e.memory()[0x1e7a]&3==3,'both Human discoveries remembered')
    close_wheel()
    # Remove synthetic mastery: discovery should survive independently of it.
    e.set_memory(0x80,original_units);e.set_memory(0x1b40,bytes(34))
    for key,wait in [(8,180),(16,180),(256,180),(256,60),(256,60),(64,20),(256,300)]:tap(key,wait)
    saved=e.memory(0);check(saved!=seed,'native save wrote a new disposable file')
    (out/'test-save.sav').write_bytes(saved);e.close();e=None
    cold(saved);check(e.memory()[0x1e7a]&3==3,'discovery survives native save and cold Continue')
    check(e.memory()[0x87]==original_units[7],'existing character job preserved')
    check(e.memory()[0x1e79]==0 or e.memory()[0x1e79]&2,'Quin metadata remains valid')
    open_wheel();rows=capture('04-cold-known-page1')
    if not any(x&127==116 for x in rows):tap(2048,600);rows=capture('05-cold-known-page2')
    check(116 in rows and 117 in rows,'known jobs grey without personal prerequisites after cold load')
    close_wheel();open_wheel();capture('06-reopened');close_wheel()
    check(seedpath.read_bytes()==seed,'source save fixture unchanged')
    report=dict(status='passed',romSha1=meta['romSha1'],seedSha256=hashlib.sha256(seed).hexdigest(),checks=checks,inputs=inputs,captures=captures,
        scope='Old in-game save cold load, hidden jobs, newly qualified paging, persistent grey discovery after native save and cold Continue. Disposable fixed-input fixture; no player saves or battle behavior changed.')
except Exception as error:
    if e is not None:e.screenshot(out/'failure.png');(out/'failure.ram').write_bytes(e.memory())
    report=dict(status='failed',romSha1=meta['romSha1'],checks=checks,inputs=inputs,captures=captures,error=str(error));raise
finally:
    if e is not None:e.close()
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],romSha1=meta['romSha1'],report=str(out/'report.json'),checks=len(checks))))
