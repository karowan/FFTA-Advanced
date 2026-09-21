/* Source-only fixed-point proof of repeatable quest-item ingredient chains.
 * A witness proves an acyclic recipe supply after its original gates unlock;
 * it does not certify campaign reachability or replace native posting tests.
 */
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {root, sha1} from '../src/rom-data.mjs';

const ledger = JSON.parse(fs.readFileSync(path.join(root, 'build/reports/mission-item-dependencies.json'), 'utf8'));
const meta = JSON.parse(fs.readFileSync(path.join(root, 'build/expansion/probes/integrated-jobs/current.json'), 'utf8'));
assert.equal(ledger.candidateSha1, meta.romSha1);
assert.equal(sha1(fs.readFileSync(meta.path)), meta.romSha1);
const recovery = new Set(meta.missionRecovery.rules.map(r => r.mission));
const records = ledger.installedRecords.filter(m => m.pubEnabled && m.repeatable && !recovery.has(m.record));
const byId = new Map(ledger.items.map(item => [item.localId, item]));
const witnesses = new Map();
// Do not use a recursion-cycle escape that could certify mutually dependent
// recipes. Only a previously proven ingredient can unlock the next layer.
for (let pass = 0; pass <= ledger.items.length; pass++) {
  const prior = new Map(witnesses);
  for (const item of ledger.items) {
    if (prior.has(item.localId)) continue;
    const eligible = records.filter(m => m.rewards.includes(item.globalId) &&
      m.requirements.every(req => prior.has(req.localId)));
    eligible.sort((a, b) => a.requirements.length-b.requirements.length ||
      Number(a.eventLocation !== null)-Number(b.eventLocation !== null) || a.record-b.record);
    if (!eligible.length) continue;
    const route = eligible[0];
    const ingredients = route.requirements.map(req => ({...req, witness:prior.get(req.localId)}));
    const positiveFlags = [...new Set([...route.unlock.filter(c => c.kind === 'flag' && c.selector && c.value === 1).map(c => c.index),
      ...ingredients.flatMap(i => i.witness.positiveFlags)])].sort((a,b) => a-b);
    const otherGates = [...route.unlock.filter(c => c.selector && !(c.kind === 'flag' && c.value === 1)),
      ...ingredients.flatMap(i => i.witness.otherGates)];
    witnesses.set(item.localId, {item:item.localId, name:item.name, mission:route.record,
      missionName:route.name, layer:pass, month:route.pubMonth, location:route.eventLocation,
      specialAbsentFlags:route.specialAbsentFlags, positiveFlags, otherGates, ingredients});
  }
  if (witnesses.size === prior.size) break;
}
const candidates = ledger.items.filter(item => item.independentRepeatableSourceRecords.length);
const unresolved = candidates.filter(item => !witnesses.has(item.localId));
assert.equal(candidates.length, 24, 'Reassess the source ledger if the candidate set changes');
assert.deepEqual(unresolved, [], 'Repeatable recipe has no acyclic renewable ingredient witness');
const rows = candidates.map(item => witnesses.get(item.localId));
const gatedAlternatives = ledger.items.map(item => ({item:item.localId, name:item.name,
  sources:item.originalRewardSources.filter(m => m.specialAbsentFlags.length ||
    m.unlock.some(c => c.selector && (c.value === 0 || c.selector >= 1279)))})).filter(row => row.sources.length);
const result = {passed:true, candidateSha1:meta.romSha1, originalSha1:ledger.cleanSha1,
  renewableItems:rows.length, ingredientFree:rows.filter(row => !row.ingredients.length).length,
  chained:rows.filter(row => row.ingredients.length).length, maxLayer:Math.max(...rows.map(row => row.layer)),
  witnesses:rows, nonMissionFlags:[...new Set(rows.flatMap(row => row.positiveFlags).filter(flag => flag >= 1279))],
  unusualOriginalSourceGates:gatedAlternatives,
  scope:'Acyclic renewable ingredient witnesses under preserved original gates. No runtime or campaign reachability claim.'};
for (const row of rows) {
  assert.equal(row.otherGates.length, 0, `${row.name}: non-monotone prerequisite requires review`);
  assert.equal(row.specialAbsentFlags.length, 0, `${row.name}: exclusion requires review`);
  assert(row.month >= 0 && row.month <= 5);
  for (const ingredient of row.ingredients) assert(byId.has(ingredient.localId));
}
const out = path.join(root, 'build/reports/mission-renewable-chains.json');
fs.writeFileSync(out, JSON.stringify(result, null, 2)+'\n');
console.log(JSON.stringify({...result, witnesses:rows.map(({ingredients, ...row}) =>
  ({...row, ingredients:ingredients.map(i => i.localId)})), unusualOriginalSourceGates:gatedAlternatives.map(row =>
  ({item:row.item, name:row.name, sources:row.sources.map(m => m.record)}))}, null, 2));
