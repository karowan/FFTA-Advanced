import {sha1} from './rom-data.mjs';

/** A bounded allocator and explicit pointer-change ledger for expansion data. */
export class ROMBuilder {
  constructor(base,{start=0x1020000,end=0x1100000}={}) {
    this.base=base;this.rom=Buffer.from(base);this.next=start;this.end=end;
    this.allocations=[];this.changes=[];
  }
  allocate(name,bytes,alignment=4) {
    const offset=Math.ceil(this.next/alignment)*alignment;
    if(offset+bytes.length>this.end)throw Error(`Data allocation exceeds reserved area: ${name}`);
    if(!this.rom.subarray(offset,offset+bytes.length).every(x=>x===255))throw Error(`Allocation overlaps data: ${name}`);
    bytes.copy(this.rom,offset);this.next=offset+bytes.length;
    this.allocations.push({name,offset,address:offset+0x08000000,bytes:bytes.length,sha1:sha1(bytes)});
    return offset+0x08000000;
  }
  repoint(original,address,expectedCount) {
    const matches=[];
    for(let offset=0;offset<0x1000000-3;offset+=4)
      if(this.base.readUInt32LE(offset)===original)matches.push(offset);
    if(expectedCount!==undefined&&matches.length!==expectedCount)throw Error(`Pointer manifest changed for ${original.toString(16)}: ${matches.length}`);
    if(!matches.length)throw Error(`No original pointer references: ${original.toString(16)}`);
    for(const offset of matches){
      if(this.rom.readUInt32LE(offset)!==original)throw Error(`Pointer patch conflict at ${offset.toString(16)}`);
      this.rom.writeUInt32LE(address,offset);this.changes.push({offset,original,address});
    }
    return matches;
  }
}

export function encodeText(text) {
  const bytes=[];
  for(const character of text){
    const n=character.charCodeAt(0);
    if(n>=65&&n<=90)bytes.push(0x80,0xb0+n-65);
    else if(n>=97&&n<=122)bytes.push(0x80,0xca+n-97);
    else if(n>=48&&n<=57)bytes.push(0x80,0xa6+n-48);
    else if(character===' ')bytes.push(0x40,0x73);
    else if(character==='-')bytes.push(0x81,0x0b);
    else if(character==="'")bytes.push(0x80,0xf4);
    else if(character==='.')bytes.push(0x80,0xe4);
    else if(character===',')bytes.push(0x80,0xec);
    else if(character===':')bytes.push(0x80,0xee);
    else if(character==='/')bytes.push(0x80,0xf1);
    else if(character==='\n')bytes.push(0x40,0x6e);
    else throw Error(`Unmapped text character ${character}`);
  }
  return Buffer.from([...bytes,0]);
}

/** Ordinary uncompressed help entry, preserving the native dialog header. */
export function encodeHelp(text,width=27) {
  const lines=[];let line='';
  for(const word of text.split(/\s+/)) {
    if(word.length>width)throw Error('Help word exceeds line width: '+word);
    if(line.length+word.length+(line?1:0)>width){lines.push(line);line='';}
    line+=(line?' ':'')+word;
  }
  if(line)lines.push(line);
  const body=encodeText(lines.join('\n'));
  return Buffer.concat([Buffer.from([0x28,0x18]),body.subarray(0,-1),Buffer.from([0x40,0x61,0x40,0x63,0])]);
}
