"""Fresh, separately allocated vanilla/current-ROM captures for paired AI timing.

Never load a state across ROMs: their heap layouts and executable pointers differ.
The common early-town SRAM is a disposable test input, never a player's save.
"""
import hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from chemist_candidate import candidate, ROOT

OUT = ROOT / 'build/expansion/ai-timing'
RUN = OUT / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
meta = candidate()
vanilla = ROOT / 'roms/clean/FFTA_US_clean.gba'
assert hashlib.sha1(vanilla.read_bytes()).hexdigest() == '4ac05441f4de70a4ec3dd932116346c61b8783d9'
for name, rom, flags in (
    ('vanilla', vanilla, ['--vanilla', '--trace-pub']),
    ('mod', Path(meta['path']), ['--chemist-progression', '--heap-end', '0x0203f000', '--confirm-pub-exit']),
):
    folder = RUN / name
    subprocess.run([sys.executable, str(ROOT / 'scripts/create-battle-fixture.py'),
                    '--rom', str(rom), '--out', str(folder), *flags], check=True)
    receipt = json.loads((folder / 'report.json').read_text())
    assert receipt['romSha1'] == hashlib.sha1(rom.read_bytes()).hexdigest()
(OUT / 'fixtures.json').write_text(json.dumps(dict(directory=str(RUN), modSha1=meta['romSha1']), indent=2))
print('Two fresh native allocations captured for paired AI timing.', flush=True)
