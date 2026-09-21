"""Two original narrow GBA status glyphs: cracked shield and focus ring."""
import pathlib,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
glyphs=[[
'00000000','00111100','01366310','13666331',
'13663161','13631661','13663161','13666361',
'13663161','13631661','01363110','00131100',
'00011000','00000000','00000000','00000000'],[
'00000000','00011000','00177100','01733710',
'17300371','17377371','13733731','13733731',
'17377371','17300371','01733710','00177100',
'00011000','00000000','00000000','00000000']]
data=bytes(int(row[x],16)|(int(row[x+1],16)<<4) for g in glyphs for row in g for x in range(0,8,2))
assert len(data)==128
values=struct.unpack('<64H',data)
(ROOT/'build/expansion/status-glyphs.h').write_text('static const uint16_t ffta_status_glyphs[64]={'+','.join(hex(v) for v in values)+'};\n')
