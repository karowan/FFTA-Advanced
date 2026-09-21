"""Authenticated native-pose substitutions using an existing class palette.

Partial plans replace only declared original pose identities. Unmapped frames
retain the existing transport, so coverage is never production-art acceptance.
"""
import hashlib,json,struct
from pathlib import Path
from PIL import Image
from native_art import ROOT,ANIM,TILES,OAM,sha,pack_tiles,layout

class LiveActionPlan:
    def __init__(self,path,job,rom,resources,palette):
        self.path=Path(path);raw=self.path.read_bytes();spec=json.loads(raw)
        assert spec['schema']==1 and spec['coverage']=='partial','Only explicit partial pose coverage supported'
        assert spec['job']==job and spec['productionAccepted'] is False,'Wrong job or premature production claim'
        clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes()
        assert hashlib.sha1(clean).hexdigest()==spec['cleanRomSha1']=='4ac05441f4de70a4ec3dd932116346c61b8783d9'
        self.bindings={};self.used=set();self.poses={};self.asset_proofs=[];self.proof=dict(path=str(self.path),sha256=sha(raw),job=job,coverage='partial',productionAccepted=False)
        for name,asset in spec['assets'].items():
            source=ROOT/asset['source'];manifest=ROOT/asset['conversionManifest'];proof=json.loads(manifest.read_bytes())
            assert sha(source.read_bytes())==proof['sourceSha256']==asset['sourceSha256'],'Source identity '+name
            assert sha(manifest.read_bytes())==asset['conversionManifestSha256'],'Conversion identity '+name
            assert (manifest.parent/'palette.bin').read_bytes()==palette and sha(palette)==proof['paletteSha256'],'Cross-sheet palette identity '+name
            for index,frame in enumerate(proof['frames']):
                with Image.open(manifest.parent/f'frame-{index:02}.png') as image:pose=image.copy()
                assert pose.mode=='P' and pose.size==(32,32),'Native action frame size'
                assert sha(pack_tiles(pose,16))==frame['tileSha256'],'Converted tile identity'
                assert (manifest.parent/f'frame-{index:02}.4bpp').read_bytes()==pack_tiles(pose,16),'Indexed image/binary agreement'
                assert Image.frombytes('L',pose.size,pose.tobytes()).getbbox(),'Empty action pose'
                self.poses[(name,index)]=pose
            self.asset_proofs.append(dict(asset=name,**asset))
        requests={}
        for group in spec['resources']:
            lifetime=group['lifetime'];assert lifetime not in requests and lifetime in ('land','water'),'Duplicate/unknown lifetime'
            selected=[r for r in resources if r['job']==job and r['lifetime']==lifetime];assert len(selected)==1
            resource=selected[0];donor=group['nativeResource'];assert type(donor) is int and 0<=donor<256
            native_table=struct.unpack_from('<I',clean,ANIM+donor*4)[0]-0x08000000
            poses={}
            for entry in group['poses']:
                key=entry['nativePose'];ref=(entry['asset'],entry['frame'])
                assert key not in poses and ref in self.poses,'Duplicate pose or invalid source cell'
                poses[key]=dict(entry,nativeResource=donor)
            seen=set();requests[lifetime]=poses
            for slot in range(resource['slots']):
                np=struct.unpack_from('<I',clean,native_table+slot*12)[0]
                rp=struct.unpack_from('<I',rom,resource['descriptors']+slot*12)[0]
                assert bool(np)==bool(rp),'Native null-slot mismatch'
                assert clean[native_table+slot*12+4:native_table+slot*12+12]==rom[resource['descriptors']+slot*12+4:resource['descriptors']+slot*12+12],'Native descriptor metadata changed'
                if not np:continue
                nq,rq=np-0x08000000,rp-0x08000000
                count=struct.unpack_from('<I',clean,nq)[0]
                assert count==struct.unpack_from('<I',rom,rq)[0],'Native frame-count mismatch'
                for frame in range(count):
                    p,q=nq+4+frame*20,rq+4+frame*20
                    assert clean[p+8:p+20]==rom[q+8:q+20],'Native command/timing mismatch'
                    t,o=struct.unpack_from('<II',clean,p);key=f'{t:06x}-{o:06x}'
                    if key not in poses:continue
                    ref=poses[key];objects,_=layout(clean,OAM+o)
                    count_tiles=max(v['tile']+v['width']*v['height']//64 for v in objects)
                    assert sha(clean[TILES+t:TILES+t+count_tiles*32])==ref['nativeTileSha256'],'Native donor pose identity'
                    k=(resource['id'],slot,frame);self.bindings[k]=ref;seen.add(key)
            assert seen==set(poses),'Unused native pose replacement'
        assert self.bindings,'Empty action plan'

    def frame(self,resource,slot,index):
        key=(resource,slot,index);ref=self.bindings.get(key)
        if ref is None:return None
        self.used.add(key)
        return self.poses[(ref['asset'],ref['frame'])].copy(),dict(ref)

    def report(self):
        assert self.used==set(self.bindings),'Unconsumed native pose substitutions'
        return dict(self.proof,mappedFrames=len(self.bindings),mappedSlots=len({(r,s) for r,s,f in self.bindings}),assets=self.asset_proofs,
                    assignments=[dict(resource=k[0],slot=k[1],index=k[2],**v) for k,v in self.bindings.items()])
