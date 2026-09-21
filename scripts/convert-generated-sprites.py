"""Technical cell extraction, native scaling and shared 4bpp quantization.

No artwork is drawn here. Source images and visual revisions come from imagegen.
The output is an import draft, not a substitute for visual/runtime acceptance.
"""
import argparse,hashlib,json,struct
from pathlib import Path
from PIL import Image
from native_art import ROOT,pack_tiles,sha

def convert(source,out,columns=4,rows=2,height=29,row_cuts=None,quantizer='coverage',resampling='nearest',target_palette=None):
    source=source.resolve();out.mkdir(parents=True,exist_ok=True)
    image=Image.open(source).convert('RGBA');frames=[];records=[]
    row_edges=[i*image.height//rows for i in range(rows+1)]
    if row_cuts is not None:
        assert len(row_cuts)==rows-1
        row_edges=[0,*row_cuts,image.height]
        assert all(a<b for a,b in zip(row_edges,row_edges[1:]))
        # Explicit extraction boundaries may accommodate uneven imagegen row
        # spacing, but must pass through completely transparent separators.
        for cut in row_cuts:
            assert not image.getchannel('A').crop((0,cut-1,image.width,cut+1)).point(lambda a:255 if a>=128 else 0).getbbox(),'Row cut crosses artwork'
    for row in range(rows):
        for column in range(columns):
            box=(column*image.width//columns,row_edges[row],
                 (column+1)*image.width//columns,row_edges[row+1])
            cell=image.crop(box)
            mask=cell.getchannel('A').point(lambda a:255 if a>=128 else 0)
            bounds=mask.getbbox();assert bounds,'Empty generated cell'
            assert bounds[0]>0 and bounds[1]>0 and bounds[2]<cell.width and bounds[3]<cell.height,('Generated figure crosses cell boundary',column,row,bounds)
            cropped=cell.crop(bounds)
            # Same scale for all frames. The tallest row establishes scale;
            # shorter idle poses retain their relative height.
            records.append(dict(cell=[column,row],box=box,bounds=bounds))
            frames.append(cropped)
    factor=min(height/max(f.height for f in frames),28/max(f.width for f in frames))
    resized=[]
    for frame in frames:
        size=(max(1,round(frame.width*factor)),max(1,round(frame.height*factor)))
        frame=frame.resize(size,{'nearest':Image.Resampling.NEAREST,'box':Image.Resampling.BOX,'lanczos':Image.Resampling.LANCZOS}[resampling])
        frame.putalpha(frame.getchannel('A').point(lambda a:255 if a>=128 else 0))
        resized.append(frame)
    samples=[f.getpixel((x,y))[:3] for f in resized for y in range(f.height) for x in range(f.width) if f.getpixel((x,y))[3]]
    strip=Image.new('RGB',(len(samples),1));strip.putdata(samples)
    # Coverage quantization preserves rare light facial/boot details that
    # population-based median cut merged into the much more common gold/red.
    if target_palette is None:
        method={'coverage':Image.Quantize.MAXCOVERAGE,'median':Image.Quantize.MEDIANCUT}[quantizer]
        quant=strip.quantize(colors=15,method=method,dither=Image.Dither.NONE)
        colors=[quant.getpalette()[i*3:i*3+3] for _,i in sorted(quant.getcolors(),key=lambda v:v[1])]
        gba=[sum(round(c*31/255)<<s for c,s in zip(rgb,(0,5,10))) for rgb in colors]
        gba=list(dict.fromkeys(gba))
    else:
        # Map original sampled source colors directly to the real consumer.
        # An intermediate generated palette can lose a rare eye/highlight
        # before the importer ever sees it. Keep native index order intact.
        assert len(target_palette)==32,'Expected one exact native16-color palette'
        gba=list(struct.unpack('<16H',target_palette)[1:])
    rgb=[tuple(((v>>s)&31)*255//31 for s in (0,5,10)) for v in gba]
    palette=[0,0,0]+[c for p in rgb for c in p]
    palette+=([0]*(768-len(palette)))
    sheet=Image.new('P',(columns*32,rows*32));sheet.putpalette(palette)
    errors=[]
    for i,frame in enumerate(resized):
        indexed=Image.new('P',(32,32));indexed.putpalette(palette)
        left=(32-frame.width)//2;top=31-frame.height
        for y in range(frame.height):
            for x in range(frame.width):
                r,g,b,a=frame.getpixel((x,y))
                if a:
                    best=min(range(len(rgb)),key=lambda j:sum((v-w)**2 for v,w in zip((r,g,b),rgb[j])))
                    errors.append(sum((v-w)**2 for v,w in zip((r,g,b),rgb[best])))
                    indexed.putpixel((left+x,top+y),best+1)
        indexed.info['transparency']=0
        path=out/f'frame-{i:02}.png';indexed.save(path,bits=4)
        raw=pack_tiles(indexed,16);(out/f'frame-{i:02}.4bpp').write_bytes(raw)
        sheet.paste(indexed,((i%columns)*32,(i//columns)*32))
        records[i].update(nativeSize=list(frame.size),origin=[left,top],tileSha256=sha(raw))
    sheet.info['transparency']=0;sheet.save(out/'native-sheet.png',bits=4)
    sheet.resize((sheet.width*8,sheet.height*8),Image.Resampling.NEAREST).save(out/'native-review.png')
    rawpalette=target_palette if target_palette is not None else struct.pack('<16H',0,*gba,*([0]*(15-len(gba))))
    (out/'palette.bin').write_bytes(rawpalette)
    report=dict(source=str(source),sourceSha256=sha(source.read_bytes()),sourceSize=list(image.size),
                colors=len(gba),paletteSha256=sha(rawpalette),frames=records,scale=factor,columns=columns,rows=rows,rowEdges=row_edges,
                quantizer='native-palette' if target_palette is not None else quantizer,resampling=resampling,quantizationMeanSquaredError=sum(errors)/(3*len(errors)),
                conversion='Cell crop with authenticated transparent borders; alpha>=128; common native scale; '+('direct mapping to exact native palette; ' if target_palette is not None else 'shared15 palette; RGB555 rounding; ')+'no drawn pixels.',
                status='Converted imagegen draft; visual and native-consumer acceptance outstanding')
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(out=str(out),colors=len(gba),sourceSize=image.size)))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('out',type=Path)
    p.add_argument('--height',type=int,default=29);p.add_argument('--columns',type=int,default=4);p.add_argument('--rows',type=int,default=2)
    p.add_argument('--row-cuts',type=int,nargs='+',help='Explicit transparent source row separators, excluding outer edges')
    p.add_argument('--quantizer',choices=['coverage','median'],default='coverage');p.add_argument('--resampling',choices=['nearest','box','lanczos'],default='nearest')
    p.add_argument('--native-palette-offset',type=lambda v:int(v,0),help='Exact32-byte palette in the authenticated clean USA ROM; bypasses intermediate quantization')
    p.add_argument('--palette-file',type=Path,help='Retained generated class palette; preserve indices across action sheets')
    p.add_argument('--palette-sha256',help='Required identity for --palette-file');a=p.parse_args()
    assert 1<=a.height<=31
    assert 1<=a.columns<=8 and 1<=a.rows<=8
    target=None
    assert bool(a.palette_file)==bool(a.palette_sha256),'Palette file and its exact hash must be supplied together'
    assert not (a.palette_file and a.native_palette_offset is not None),'Select one palette source'
    if a.palette_file:
        target=a.palette_file.read_bytes()
        assert len(target)==32 and sha(target)==a.palette_sha256,'Supplied class palette identity mismatch'
    if a.native_palette_offset is not None:
        from native_table_literals import authenticate
        clean=(ROOT/'roms/clean/FFTA_US_clean.gba').read_bytes();authenticate(clean)
        assert 0<=a.native_palette_offset<=len(clean)-32 and a.native_palette_offset%2==0
        target=clean[a.native_palette_offset:a.native_palette_offset+32]
    convert(a.source,a.out,columns=a.columns,rows=a.rows,height=a.height,row_cuts=a.row_cuts,quantizer=a.quantizer,resampling=a.resampling,target_palette=target)
