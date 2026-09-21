#ifndef FFTA_GEOMANCER_ANIMATION_H
#define FFTA_GEOMANCER_ANIMATION_H
#include <stdint.h>
/* The live map owner must allocate this source and retain it until restoration.
 * Native animations write the pristine prefix, never the composed tile cache. */
typedef struct {
 uint8_t *controller;
 const uint8_t *control,*source;
 unsigned destination;
} FFTA_GeoAnimationBinding;
typedef struct {
 unsigned magic,self,tiles,count;
 FFTA_GeoAnimationBinding bindings[4];
 uint32_t graphics[128][8];
} FFTA_GeoAnimationSource;
unsigned ffta_geo_animation_begin(FFTA_GeoAnimationSource *,uint8_t *pool,unsigned tiles);
void ffta_geo_animation_end(FFTA_GeoAnimationSource *);
#endif
