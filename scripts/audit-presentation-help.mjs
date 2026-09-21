/* Read-only reuse audit: native-decoded descriptions still equal every byte
 * installed in the current image. No emulator, native execution or fixtures. */
import fs from 'node:fs';
import path from 'node:path';
import {root,sha1} from '../src/rom-data.mjs';
import {encodeHelp} from '../src/rom-builder.mjs';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p)));
const meta=read('build/expansion/probes/integrated-jobs/current.json');
const image=fs.readFileSync(meta.path),registry=read('build/expansion/registry.json');
const acceptedSha='7908cc6e3ee78206cc0df16bee627e86f88c68d4';
const base=path.dirname(path.dirname(meta.path));
const reportPath=path.join(base,acceptedSha,'installed-lesson-help.json');
const reportBytes=fs.readFileSync(reportPath),prior=JSON.parse(reportBytes);
const previous=fs.readFileSync(path.join(base,acceptedSha,'integrated.gba'));
let checks=0;function check(ok,label){checks++;if(!ok)throw Error(label);}
check(sha1(image)===meta.romSha1,'Current executable');
check(sha1(previous)===acceptedSha&&prior.passed&&prior.romSha1===acceptedSha,'Previously native-decoded executable/report');
check(prior.lessons.length===129&&registry.lessons.length===129,'Complete lesson domain');
for(const [lo,hi] of [[0x13e9c,0x14100],[0x19a50,0x19b00]])
 check(image.subarray(lo,hi).equals(previous.subarray(lo,hi)),'Original native help decoder/routing '+lo.toString(16));
const banks=image.readUInt32LE(0x257e8)&0x1ffffff;
const help=image.readUInt32LE(0x36d6c4)&0x1ffffff;
const oldHelp=previous.readUInt32LE(0x36d6c4)&0x1ffffff;
const lessons=[];
for(const row of prior.lessons){
 const lesson=registry.lessons.find(x=>x.id===row.id);check(Boolean(lesson),'Approved lesson '+row.id);
 const p=image.readUInt32LE(help+4*(row.helpId-0x1de))&0x1ffffff;
 const old=previous.readUInt32LE(oldHelp+4*(row.helpId-0x1de))&0x1ffffff;
 const expected=encodeHelp(row.text,27),actual=image.subarray(p,p+expected.length);
 check(actual.equals(expected),'Complete current encoded description '+row.id);
 check(actual.equals(previous.subarray(old,old+expected.length)),'Retained native-decoded description '+row.id);
 for(const owner of lesson.owners){
  const racial=image.readUInt32LE(banks+4*owner.race)&0x1ffffff;
  check(image.readUInt16LE(racial+8*owner.abilityIndex+2)===row.helpId,'Current racial route '+row.id+':'+owner.race);
 }
 lessons.push({...row,address:p+0x08000000,encodedSha1:sha1(actual)});
}
const result={passed:true,candidateSha1:meta.romSha1,priorSha1:acceptedSha,priorReport:reportPath,
 priorReportSha1:sha1(reportBytes),checks,lessons,
 scope:'Exact current bytes and racial routes reuse previously native-decoded help; wording review remains the documented root review.'};
const output=path.join(root,'build/reports/presentation-help-reuse.json');fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({passed:true,checks,lessons:lessons.length,report:output}));
