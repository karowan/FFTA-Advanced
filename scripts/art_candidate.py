"""Select an explicit assembled art manifest without replacing prior evidence."""
import json,sys
from pathlib import Path
from native_art import ROOT

def candidate(default,component):
    if '--manifest' not in sys.argv:
        return json.loads((ROOT/default).read_text())
    name=sys.argv[sys.argv.index('--manifest')+1]
    document=json.loads((ROOT/name).read_text())
    result=dict(document['components'][component])
    result.update(path=document['path'],romSha1=document['romSha1'])
    # A clean rebuilt parent need not contain the historical runtime fixtures.
    # Keep that provenance separate from the ROM used for comparisons.
    result['fixtureSource']=document.get('fixtureSource',document.get('source',result.get('source')))
    return result
