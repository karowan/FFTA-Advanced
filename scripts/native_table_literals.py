"""Verified USA table literals; never infer pointers from arbitrary ROM words.

Each site is paired with its actual clean-ROM Thumb LDR instruction. Original
graphics compressed tokens sometimes match expansion addresses, even with a
spurious LDR-shaped word nearby. Therefore neither numeric ranges nor a raw
instruction scan are sufficient provenance. New sites require explicit review.
"""
import hashlib
import struct

CLEAN_SHA1='4ac05441f4de70a4ec3dd932116346c61b8783d9'
# literal: (load instruction, original table pointer)
NATIVE_TABLE_LITERALS={
    0x23320:(0x23302,0x0855187c),0x236ac:(0x23692,0x0855187c),
    0x25998:(0x25934,0x0855187c),0x26c9c:(0x26c36,0x0855187c),
    0x26d3c:(0x26ce8,0x0855187c),0x26e18:(0x26da2,0x0855187c),
    0x27048:(0x26ff8,0x0855187c),0x27170:(0x27116,0x0855187c),
    0x279a0:(0x27964,0x0855187c),0x27a94:(0x27a3c,0x0855187c),
    0xa784c:(0xa7836,0x0855187c),0xb4cec:(0xb4cb6,0x08553e70),
    0xb5d18:(0xb5cee,0x0855187c),0xc1ca4:(0xc1c88,0x08553e70),
    0xc230c:(0xc21a6,0x08553e70),0xc3080:(0xc2f34,0x0855187c),
    0xc3474:(0xc335a,0x0855187c),0xccd84:(0xccd62,0x0855187c),
    0x12f2a0:(0x12f28c,0x08553e70),0x12f348:(0x12f33a,0x08553e70),
    0x12f3c8:(0x12f3c0,0x08553e70),0x1323b8:(0x13239c,0x083a87b0),
    0x132430:(0x132410,0x083a87b0),0x133920:(0x1338a8,0x083a87b0),
    0x133984:(0x133974,0x083a87b0),0x1339a4:(0x13398a,0x083a87b0),
    0x1339c8:(0x1339b6,0x0852790c),0x1339ec:(0x1339da,0x08527d5c),
    0x133e70:(0x133e38,0x0855187c),0x13416c:(0x134162,0x0855187c),
}

def authenticate(clean):
    assert hashlib.sha1(clean).hexdigest()==CLEAN_SHA1,'Wrong native revision'
    for literal,(load,pointer) in NATIVE_TABLE_LITERALS.items():
        op=struct.unpack_from('<H',clean,load)[0]
        assert op&0xf800==0x4800 and ((load+4)&~3)+(op&255)*4==literal
        assert struct.unpack_from('<I',clean,literal)[0]==pointer

def native_literal_allowed(clean,rom,offset):
    if offset in NATIVE_TABLE_LITERALS:
        # The source table address may already have been expanded upstream;
        # authenticate the surviving native load, not that intermediate value.
        load,_=NATIVE_TABLE_LITERALS[offset]
        assert rom[load:load+2]==clean[load:load+2],('Native table load changed',hex(load))
        return True
    # An unregistered changed word might be a new genuine reference. Stop
    # instead of silently omitting it. Original data coincidences stay exact.
    assert rom[offset:offset+4]==clean[offset:offset+4],('Unreviewed native relocation',hex(offset))
    return False
