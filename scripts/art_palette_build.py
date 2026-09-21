"""Deterministic acceleration data for exact 8bpp palette-bank accounting."""
import struct

def write_pixel_banks(directory):
    # Each 16-bit input is two pixel indices. Index zero is transparent;
    # indices 1..15 genuinely occupy bank zero. This is lookup data, not art.
    values = []
    for pair in range(65536):
        lo, hi = pair & 255, pair >> 8
        values.append((1 << (lo >> 4) if lo else 0) | (1 << (hi >> 4) if hi else 0))
    source = directory / 'pixel-banks.c'
    source.write_text('#include <stdint.h>\nconst uint16_t ffta_art_pixel_banks[65536]={\n' +
                      ',\n'.join(','.join(str(v) for v in values[i:i + 256]) for i in range(0, 65536, 256)) + '\n};\n')
    return source, struct.pack('<65536H', *values)
