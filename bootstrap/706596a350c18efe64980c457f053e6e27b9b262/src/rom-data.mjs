import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
export const root=path.resolve(import.meta.dirname,'..');
export const cleanPath=path.join(root,'roms/clean/FFTA_US_clean.gba');
export const sha1=b=>crypto.createHash('sha1').update(b).digest('hex');
export function cleanROM(){const b=fs.readFileSync(cleanPath);if(sha1(b)!=='4ac05441f4de70a4ec3dd932116346c61b8783d9')throw Error('Wrong clean USA ROM');return b;}
const chars=JSON.parse(fs.readFileSync(path.join(root,'tools/ffta-randomizer-source/src/main/ffta/utils/charLookup.json')));
export function textAt(b,o){let s='';for(let i=o;i<Math.min(o+1024,b.length)&&b[i];i++){
  if(b[i]===1)continue;
  if(b[i]===0x40&&b[i+1]===0x3e){s+=' ';i+=2;continue;}
  if(b[i]===0x80){const z=b[++i];if(z>=0xb0&&z<=0xc9)s+=String.fromCharCode(65+z-0xb0);else if(z>=0xca&&z<=0xe3)s+=String.fromCharCode(97+z-0xca);else if(z>=0xa6&&z<=0xaf)s+=String.fromCharCode(48+z-0xa6);else s+=({0xf4:"'",0xe4:'.',0xea:'?',0xeb:'!',0xec:',',0xee:':',0xf1:'/'})[z]??`[80${z.toString(16)}]`;continue;}
  const a=b[i].toString(16).toUpperCase(),z=b[i+1]?.toString(16).toUpperCase();if(z&&chars[a+z]){s+=chars[a+z];i++;}else s+=chars[a]??`[${a}]`;
}return s;}
export function nameAt(b,table,id){const p=b.readUInt32LE(table+id*4)&0x1ffffff;return textAt(b,p);}
export function missions(b){return Array.from({length:406},(_,index)=>{const offset=0x55ae4c+index*0x46,id=b.readUInt16LE(offset);return {index,id,name:nameAt(b,0x55a64c,id),offset,rewards:[b.readUInt16LE(offset+0x22),b.readUInt16LE(offset+0x24)],required:[b[offset+0x36],b[offset+0x37]],recruit:b[offset+0x35],flags:b.subarray(offset+5,offset+14).toString('hex'),repeatable:!!(b[offset+0x41]&8),raw:b.subarray(offset,offset+0x46).toString('hex')};});}
export function itemName(b,id){if(!id)return 'none';if(id>=0xfff0)return `random reward ${id.toString(16)}`;const textID=id<=375?b.readUInt16LE(0x51d1a0+(id-1)*32):id+123;return nameAt(b,0x526680,textID);}
