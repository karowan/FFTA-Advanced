#ifndef FFTA_GEOMANCER_COMPOSITOR_H
#define FFTA_GEOMANCER_COMPOSITOR_H
#include <stdint.h>
#include "geomancer-map.h"

/* Detached frame builder. The renderer must own the allocation and publish
 * only successful frames. This module does not allocate or write hardware. */
#define FFTA_GEO_CACHE_TILES 672u
#define FFTA_GEO_HASH_SIZE 1024u
/* Immutable build-time source for one tile/flip combination. Pixel buckets
 * use exactly the runtime interner hash; equality still resolves collisions. */
typedef struct {
 const uint32_t *pixels;
 uint16_t bucket,opaque;
} FFTA_GeoSource;
_Static_assert(sizeof(FFTA_GeoSource)==8,"Prepared terrain source ABI");
typedef struct {
 const uint16_t *arrangement[2]; /* Native64x64 planes; original words. */
 const uint32_t *graphics;      /* Original current animation frame,8 words/tile. */
 const uint16_t *palette;       /* Original eight terrain palette banks. */
 const FFTA_GeoProjection *projection; /*256 entries, indexed by field board. */
 const uint8_t *board;          /* bit0 Rime, bit1 Refuge; accepted geometry. */
 unsigned tile_count;
 int camera_x,camera_y;         /* Canvas pixel at screen origin. */
 const uint32_t *animated_graphics; /* Owned original prefix, before outlines. */
 unsigned animated_tiles;          /*0 for immutable whole-frame input. */
 const uint16_t *retained_ids;      /* Sparse native tiles beyond decoded atlas. */
 const uint32_t *retained_graphics; /* Snapshot before the cache takes ownership. */
 unsigned retained_count;
} FFTA_GeoScene;
typedef struct {
 uint16_t count,ready;
 uint16_t map[2][1024];
 uint32_t (*graphics)[8]; /* Separate owned cache; avoids one large heap block. */
 uint16_t hash[FFTA_GEO_HASH_SIZE];
 /* Scratch is owned with the frame, never placed on the native UI stack. */
 uint32_t row[2][31][8];
 uint16_t palette_bits[2][31];
 uint8_t light[8],dark[8];
 uint16_t memo_key[256],memo_value[256];
 uint8_t fields[256];
 unsigned field_count;
 uint32_t animated_used[4];
 /* Per cached tile: one original animated tile/flip key, immutable pixels,
  * or shared/outlined pixels that require exact validation before refresh. */
 uint16_t animation_key[FFTA_GEO_CACHE_TILES];
 const uint32_t *row_source[2][31];
 uint16_t row_metadata[2][31]; /* bucket bits0..9,opaque bit10;FFFF unknown. */
 int origin_x,origin_y; /* Tile coordinates of the complete cached viewport. */
} FFTA_GeoFrame;

/* Logical graphics640..671 occupy the second screenblock at06006800.
 * The live owner switches both terrain maps to256x256 before publication.
 * Caller must NOT upload them while native512x256 tilemaps are active. */
unsigned ffta_geo_cache_index(unsigned logical);
/* 1 complete,0 invalid input or capacity failure. ready==1 is publication. */
/* Optional sources has4*tile_count entries, indexed flip*tile_count+tile.
 * Animated prefixes and retained RAM tiles always use their current pixels. */
unsigned ffta_geo_compose(const FFTA_GeoScene *scene,FFTA_GeoFrame *frame,
 const FFTA_GeoSource *sources);
/* Refresh only animation-dependent pixels.0 requests full composition; it
 * never partially changes the published maps/cache on refusal. */
unsigned ffta_geo_refresh_animation(const FFTA_GeoScene *scene,FFTA_GeoFrame *frame);
/* Reuse the intersection after a camera move with unchanged field/terrain and
 * source pixels. Caller must refresh old animation first when necessary.
 * 0 requires full composition before publication; partial scratch is allowed. */
unsigned ffta_geo_shift(const FFTA_GeoScene *scene,FFTA_GeoFrame *frame,
 const FFTA_GeoSource *sources);
#endif
