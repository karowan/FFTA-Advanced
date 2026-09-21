"""Council mGBA evidence for conditional native heap limits; isolated saves only."""
import hashlib, json, pathlib, runpy, struct

ROOT = pathlib.Path(__file__).resolve().parents[1]
p = runpy.run_path(str(ROOT/'scripts/probe-ap-copy-heap.py'))
h, OUT = p['h'], p['OUT']
ROM = ROOT/'build/expansion/probes/content-inventory.gba'
GUARD = b'\xA5' * 0xd0

def snapshot(e, label):
    ram=e.memory()
    result={'label':label, 'format':ram[0x1e70:0x1e79].hex(), 'heaps':[],
            'rosterHeader4to7':[list(ram[0x80+i*264+4:0x80+i*264+8]) for i in range(6)],
            'state1f00to2020':ram[0x1f00:0x2020].hex(),
            'nativeFlagsF390':ram[0xf390:0xf42c].hex(),
            'heapRoots':[]}
    result['viewGuardIntact']=ram[0x3ff30:0x40000]==GUARD
    for off in range(0xf380,0x3fff0,4):
        if ram[off+4:off+6]!=b'\x01\0' or ram[off+12:off+14] not in (b'la',b'ps'):continue
        end=off+8+struct.unpack_from('<H',ram,off+6)[0]*4
        if off+20<=end<=0x40000:result['heapRoots'].append({'base':hex(0x02000000+off),'end':hex(0x02000000+end)})
    for global_offset in (0xf434,0x1f53c,0xf3bc):
        base=struct.unpack_from('<I',ram,global_offset)[0]
        entry={'global':hex(global_offset),'base':hex(base)}
        if 0x02000000<=base<0x0203fff8:
            off=base-0x02000000
            entry['end']=hex(base+8+struct.unpack_from('<H',ram,off+6)[0]*4)
        result['heaps'].append(entry)
    try:result['battleHeap']=p['heap'](ram)
    except Exception as ex:result['battleHeapError']=repr(ex)
    e.screenshot(OUT/('conditional-'+label+'.png'))
    return result

def tap(e,key,wait=40):e.run(8,key);e.run(wait)

def cold():
    e=h['Emulator'](ROM);reports=[]
    try:
        e.set_memory(0,(ROOT/'build/test-lab/early-town.sav').read_bytes(),0)
        e.run(3600);e.set_memory(0x3ff30,GUARD);reports.append(snapshot(e,'cold-title'))
        for i,(key,wait) in enumerate([(8,180),(256,60),(256,60),(256,180),(8,40),(256,120),(8,120)]):
            tap(e,key,wait);reports.append(snapshot(e,f'cold-{i}'))
        tap(e,1,60);tap(e,1,80)
        tap(e,256,240);tap(e,32);tap(e,256,180);tap(e,256,120)
        reports.append(snapshot(e,'cold-shop'))
    finally:e.close()
    return reports

def startup():
    e=h['Emulator'](ROOT/'build/expansion/probes/inventory-startup.gba');reports=[]
    sequence=[(3600,0),(8,8),(300,0),(8,256),(300,0),
        (8,8),(60,0),(8,64),(30,0),(8,256),(180,0),
        (8,8),(60,0),(8,64),(30,0),(8,256),(300,0),
        (8,16),(60,0),(8,256),(120,0),
        (30,0),(40,128),(16,16),(30,0),(8,256),(120,0)]
    try:
        for i,(frames,keys) in enumerate(sequence):
            e.run(frames,keys)
            if i==0:e.set_memory(0x3ff30,GUARD)
            if frames>=120:reports.append(snapshot(e,f'startup-{i}'))
        tap(e,8);tap(e,256,120);reports.append(snapshot(e,'startup-party'))
    finally:e.close()
    return reports

def story():
    e=h['Emulator'](ROM);reports=[]
    try:
        e.run(3600);e.set_memory(0x3ff30,GUARD);tap(e,8,180);tap(e,256,1800)
        for step in range(71):
            if step:tap(e,8 if step==31 else 64 if step==32 else 256,120)
            if step%5==0:reports.append(snapshot(e,f'story-{step}'))
    finally:e.close()
    return reports

if __name__=='__main__':
    frozen=OUT/'integrated-2k.gba';frozen.write_bytes(ROM.read_bytes());ROM=frozen
    result={'romSha1':hashlib.sha1(ROM.read_bytes()).hexdigest(),
            'startupSha1':hashlib.sha1((ROOT/'build/expansion/probes/inventory-startup.gba').read_bytes()).hexdigest(),
            'cold':cold(),'startup':startup(),'story':story()}
    (OUT/'integrated-2k-report.json').write_text(json.dumps(result,indent=2))
    for mode in ('cold','startup','story'):
        for record in result[mode]:
            print(json.dumps({k:v for k,v in record.items() if k!='battleHeap'}|{'heap':{k:v for k,v in record.get('battleHeap',{}).items() if k!='allocationBlocks'}}))
