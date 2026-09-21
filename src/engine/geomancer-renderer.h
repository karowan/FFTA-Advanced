#ifndef FFTA_GEOMANCER_RENDERER_H
#define FFTA_GEOMANCER_RENDERER_H
#include <stdint.h>
void ffta_geo_renderer_update(unsigned map_state);
void ffta_geo_renderer_pump(void);
unsigned ffta_geo_renderer_stream(void);
void ffta_geo_renderer_retire(void);
void ffta_geo_renderer_free(void *allocation);
void ffta_geo_reset_owners(void);
void *ffta_geo_allocate(void *heap,unsigned bytes);
#endif
