"""Sequential source-to-candidate recipe; tests and promotion are separate."""
import shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
node=shutil.which('node');assert node,'Node.js is required'
for name in ('build-chemist-progression-data.mjs','build-chemist-progression-art.py',
             'build-chemist-progression-menu.py','compile-chemist-progression.py',
             'install-chemist-progression-probe.py','build-chemist-progression-actions.py',
             'build-chemist-progression-help.mjs'):
 subprocess.run([node if name.endswith('.mjs') else sys.executable,str(ROOT/'scripts'/name)],cwd=ROOT,check=True)
