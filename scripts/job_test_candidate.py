"""Explicit candidate selection for the same deterministic job scenarios."""
import hashlib
import json
import os
import pathlib
import struct

def initialize_inactive_turn_domain(machine):
    """Initialize both differential inputs, never normalize their outputs.

    Shared schema2 records reserve12/13 and14 for turn origin/history/allowance.
    Only the high5 bits of19 belong to movement; preserve Steady's low3 bits.
    Call this only for candidates exporting the integrated turn lifecycle.
    """
    for index in range(36):
        record=0x0203f410+22*index
        machine.put(record+12,bytes(3))
        machine.put(record+19,bytes((machine.read(record+19,1)[0]&7,)))


def normalize_native_context(data,candidate_rom,base_rom):
    """Compare original actions after proving two relocated context references.

    No result, RNG, unit, ledger, or other scratch byte is excluded. Both
    references must point to the same native row and identical descriptor data.
    """
    assert len(data)==0x40000
    result=bytearray(data)
    for field,literal,count,stride,within in [(0xf420,0x12f2a0,209,4,0),(0xf41c,0xccd84,432,28,12)]:
        new=struct.unpack_from('<I',candidate_rom,literal)[0]
        old=struct.unpack_from('<I',base_rom,literal)[0]
        value=struct.unpack_from('<I',result,field)[0]
        if new!=old and new<=value<new+count*stride:
            offset=value-new
            assert offset%stride==within,('unexpected context interior pointer',field,value)
            a=value-0x08000000;b=old+offset-0x08000000
            assert candidate_rom[a:a+4]==base_rom[b:b+4],('changed native context descriptor',field,value,old+offset)
            struct.pack_into('<I',result,field,old+offset)
    return bytes(result)

def load_candidate(default):
    default=pathlib.Path(default)
    override=os.environ.get('FFTA_TEST_CANDIDATE')
    if not override:return json.loads(default.read_text())
    candidate=json.loads(pathlib.Path(override).read_text())
    job=default.parent.name
    assert job in candidate['jobViews'],('candidate does not contain job',job)
    view=dict(candidate['jobViews'][job])
    for key in ('path','romSha1','baseSha1','heapEnd','symbols','tables','upstream','priorSymbols','fixtureBaseSha1'):
        view[key]=candidate[key]
    if job in candidate['help']:view['help']=candidate['help'][job]
    assert hashlib.sha1(pathlib.Path(view['path']).read_bytes()).hexdigest()==view['romSha1']
    return view
