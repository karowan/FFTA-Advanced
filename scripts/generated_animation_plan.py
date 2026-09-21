"""Explicit imagegen frame assignments for native actor animation sequences.

Partial plans preserve unmapped temporary transports. Complete plans must cover
every present land/water slot of each declared job; coverage never accepts art.
"""
import importlib.util,json,struct
from pathlib import Path
from PIL import Image
from native_art import ROOT,sha,palette,pack_tiles

class AnimationPlan:
    def __init__(self, path, rom, resources, work):
        self.path=Path(path);self.payload=self.path.read_bytes();self.spec=json.loads(self.payload)
        assert self.spec['schema']==1 and self.spec['coverage'] in ('partial','complete'), 'Unknown animation-plan schema/coverage'
        self.assets=self.spec['assets'];self.bindings={};self.used=set();self.cache={};self.sources=[];self.work=Path(work)
        jobs=self.spec['jobs'];assert jobs and len(jobs)==len(set(jobs)) and all(type(j) is int and 116<=j<=125 for j in jobs),'Invalid or duplicate jobs'
        expected={}
        for res in resources:
            if res['job'] not in jobs:continue
            for slot in range(res['slots']):
                q=struct.unpack_from('<I',rom,res['descriptors']+12*slot)[0]
                if q:expected[(res['job'],res['lifetime'],slot)]=struct.unpack_from('<I',rom,q-0x08000000)[0]
        for entry in self.spec['sequences']:
            assert type(entry['job']) is int and type(entry['slot']) is int,'Job/slot must be integer IDs'
            key=(entry['job'],entry['lifetime'],entry['slot'])
            assert key in expected and key not in self.bindings,'Unknown/null/duplicate sequence '+str(key)
            frames=entry['frames'];assert len(frames)==expected[key],'Native frame count mismatch '+str(key)
            for ref in frames:
                assert ref['asset'] in self.assets,'Unknown generated asset'
                asset=self.assets[ref['asset']];settings=asset['conversion']
                assert type(ref['frame']) is int and 0<=ref['frame']<settings['columns']*settings['rows'],'Source frame outside sheet'
            self.bindings[key]=frames
        assert self.bindings,'Empty explicit animation plan'
        assert self.spec['coverage']!='complete' or set(expected)==set(self.bindings),'Complete plan has missing land/water slots'
        self.expected=expected
        for name,asset in self.assets.items():
            source=(ROOT/asset['source']).resolve()
            assert sha(source.read_bytes())==asset['sourceSha256'],'Generated source hash mismatch '+name
            cfg=asset['conversion']
            assert all(type(cfg[k]) is int and 1<=cfg[k]<=8 for k in ('columns','rows')) and type(cfg['height']) is int and 1<=cfg['height']<=31,'Invalid cell grid/height'
            assert cfg['resampling'] in ('nearest','box','lanczos')
            self.sources.append(dict(asset=name,path=str(source),sha256=asset['sourceSha256']))

    def sequence(self,job,lifetime,slot):
        key=(job,lifetime,slot)
        if key in self.bindings:self.used.add(key)
        return self.bindings.get(key)

    def frame(self,ref,rom,palette_offset):
        key=(ref['asset'],palette_offset)
        if key not in self.cache:
            asset=self.assets[ref['asset']];settings=asset['conversion'];pal,_=palette(rom,palette_offset)
            source=(ROOT/asset['source']).resolve()
            # Different revisions often reuse the same asset name. Keep their
            # conversion evidence separate by all pixel-affecting inputs.
            conversion_key=sha(json.dumps(dict(sourceSha256=asset['sourceSha256'],settings=settings,paletteSha256=sha(pal)),sort_keys=True).encode())
            out=self.work/conversion_key
            spec=importlib.util.spec_from_file_location('animation_conversion',ROOT/'scripts/convert-generated-sprites.py')
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            module.convert(source,out,columns=settings['columns'],rows=settings['rows'],height=settings['height'],resampling=settings['resampling'],row_cuts=settings.get('rowCuts'),target_palette=pal)
            meta=json.loads((out/'manifest.json').read_text())
            assert meta['sourceSha256']==asset['sourceSha256'] and (out/'palette.bin').read_bytes()==pal
            self.cache[key]=(out,meta)
        out,meta=self.cache[key];index=ref['frame']
        with Image.open(out/f'frame-{index:02}.png') as image:
            result=image.copy();result.info['transparency']=0
        assert result.size==(32,32) and result.mode=='P' and sha(pack_tiles(result,16))==meta['frames'][index]['tileSha256']
        return result

    def report(self):
        assert self.used==set(self.bindings),'Unconsumed animation assignments'
        return dict(path=str(self.path),sha256=sha(self.payload),coverage=self.spec['coverage'],jobs=self.spec['jobs'],
            mappedSequences=len(self.bindings),requiredSequences=len(self.expected),sources=self.sources,
            assignments=[dict(job=k[0],lifetime=k[1],slot=k[2],frames=v) for k,v in self.bindings.items()],
            conversions=[dict(asset=k[0],paletteOffset=k[1],manifest=str(p/'manifest.json'),manifestSha256=sha((p/'manifest.json').read_bytes())) for k,(p,m) in self.cache.items()],
            productionAccepted=False)
