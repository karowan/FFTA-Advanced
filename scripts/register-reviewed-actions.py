"""Recalculate native X registration from preserved generated worksheets."""
import importlib.util
import json
import runpy
from PIL import Image
from native_art import ROOT

spec=importlib.util.spec_from_file_location('reviewed_actions',ROOT/'scripts/prepare-reviewed-actions.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
path=module.CATALOG;catalog=json.loads(path.read_text())
clear=runpy.run_path(str(ROOT/'scripts/assemble-other-race-studies.py'))['clear_background']
for unit in catalog['units']:
    for pose in unit['poses']:
        if pose['status'] not in ('generated-reviewed','generated-awaiting-review'):continue
        gen=pose['generation'];image=Image.open(ROOT/gen['generatedSource']['path']).convert('RGBA')
        worksheet=clear(image.resize(tuple(gen['logicalSize']),Image.Resampling.NEAREST))
        module.register_anchor(pose,worksheet)
path.write_text(json.dumps(catalog,indent=2)+'\n')
print('Registered generated worksheet anchors; no artwork pixels changed.')
