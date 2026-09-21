#ifndef FFTA_GEOMANCER_ASSETS_H
#define FFTA_GEOMANCER_ASSETS_H
#include <stdint.h>
#include "geomancer-compositor.h"
/* Generated from the clean USA image; graphics and palette bytes stay private.
 * The integrated builder validates and installs this private reservation. */
typedef struct {
 const uint32_t *graphics;
 const uint16_t *palette;
 uint16_t tiles,prefix_tiles,retained_count,reserved;
 const uint16_t *retained_ids;
 const FFTA_GeoSource *sources;
} FFTA_GeoAsset;
_Static_assert(sizeof(FFTA_GeoAsset)==24,"Immutable map asset table ABI");
#define FFTA_GEO_ASSET_BASE 0x09400000u
#define FFTA_GEO_ASSET_LIMIT 0x09a00000u
#endif
