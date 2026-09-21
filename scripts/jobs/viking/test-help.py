"""Reuse the native help consumer contract for this exact Viking candidate."""
import pathlib
source=(pathlib.Path(__file__).resolve().parents[2]/'test-samurai-help.py').read_text()
source=source.replace('parents[1]','parents[3]').replace("P/'samurai/current.json'","P/'viking/current.json'")
exec(compile(source,__file__,'exec'))
