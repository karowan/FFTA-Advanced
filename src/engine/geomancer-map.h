#ifndef FFTA_GEOMANCER_MAP_H
#define FFTA_GEOMANCER_MAP_H
#include <stdint.h>
/* Canvas coordinates precede camera subtraction. Each quarter is16x8 pixels;
 * plane0 lies above the native foreground, plane1 lies behind it. */
typedef struct {
 int16_t x,y;
 uint8_t plane[4];
} FFTA_GeoProjection;
unsigned ffta_geo_project_tile(int,int,FFTA_GeoProjection *);
/* One byte per16x16 board cell: bit0 Rime, bit1 Refuge. This is geometry,
 * independent of a viewer's faction, Float, flight or Surefoot. The supplied
 * unit selects its exact owned cohort; copied cohorts cannot borrow live fields. */
unsigned ffta_geo_field_board(uint8_t *,uint8_t *);
#endif
