import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const root = path.resolve(import.meta.dirname, '..');
// The review compared v0.4 with the council proposal. Keep that baseline after adoption.
const baselineDirectory = path.join(root, 'notes/design-v0.4');
const original = JSON.parse(fs.readFileSync(path.join(baselineDirectory, 'job-theme-audit.json'), 'utf8'));
const files = ['balance-council-martial.md', 'balance-council-magic-utility.md', 'balance-council-supports-reactions.md'];
const rows = [];
for (const file of files) {
  const lines = fs.readFileSync(path.join(root, 'notes', file), 'utf8').split(/\r?\n/);
  lines.forEach((line, i) => {
    const match = line.match(/^\|\s*((?:SAM|DRK|VIK|GEO|CHM|BRD|DNC|MYK)-(?:[ASRC]\d)|(?:SLD|GLD)-AX-[ASR]\d)\b/);
    if (!match) return;
    const cells = line.split('|').slice(1, -1).map(x => x.trim());
    const apMatch = cells[2].match(/^(\d+)\s*(?:AP\b|;)/) || cells[1].match(/;\s*(\d+)\b/);
    const old = original.abilities.find(x => x.id === match[1]);
    rows.push({id: match[1], name: old?.name ?? null, type: old?.type ?? null, job: old?.job ?? null, originalAp: old?.ap ?? null, proposedAp: apMatch ? Number(apMatch[1]) : null, verdict: cells[1], report: `notes/${file}`, line: i + 1});
  });
}
const expected = original.abilities.map(x => x.id);
const missing = expected.filter(id => !rows.some(r => r.id === id));
const duplicates = [...new Set(rows.map(r => r.id))].filter(id => rows.filter(r => r.id === id).length !== 1);
const unexpected = rows.filter(r => !expected.includes(r.id)).map(r => r.id);
const missingAp = rows.filter(r => r.proposedAp === null).map(r => r.id);
const baselines = {
  'JOB-CLASS-SPECIFICATION.md': '85F6611090743E94DCCA1BA3B7BDFF788789C3C56B7AD6414B7D487F87095A40',
  'SUPPORT-SKILL-DESIGN.md': 'EBAC7FE9C7348D2A7735EDCC07FE2B7E53F710BAA7DC533D32C7D46F26A3B135',
  'AXE-SKILL-EXPANSION.md': '64CCB8886B29B8A8C7F2790377D55408816A024B1C2E751DB5E3563C2710A09C',
  'notes/job-theme-audit.json': '7922D33510561287F4E541B75C4306E6F072E1C5E482ED0681E53F305B31E653'
};
const reviewBaselinePreserved = Object.entries(baselines).every(([file, hash]) => crypto.createHash('sha256').update(fs.readFileSync(path.join(baselineDirectory, path.basename(file)))).digest('hex').toUpperCase() === hash);
const totals = {};
for (const row of rows) {
  const key = row.id.replace(/-[ASRC]\d$/, '');
  totals[key] ??= {entries: 0, originalAp: 0, proposedAp: 0};
  totals[key].entries++;
  totals[key].originalAp += row.originalAp;
  totals[key].proposedAp += row.proposedAp ?? 0;
}
const checks = {expected: expected.length, reviewed: rows.length, missing, duplicates, unexpected, missingAp, reviewBaselinePreserved, totals};
fs.writeFileSync(path.join(root, 'notes/balance-council-coverage.json'), JSON.stringify({date: '2026-09-14', purpose: 'Coverage and AP arithmetic only; not a gameplay simulation or proof of balance.', checks, entries: rows}, null, 2) + '\n');
console.log(JSON.stringify(checks, null, 2));
if (missing.length || duplicates.length || unexpected.length || missingAp.length || !reviewBaselinePreserved) process.exitCode = 1;
