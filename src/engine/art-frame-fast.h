#ifndef FFTA_ART_FRAME_FAST_H
#define FFTA_ART_FRAME_FAST_H
#include "art-palette-owners.h"
#include "art-palette-plan.h"
typedef struct {
 const FFTA_ArtOwners *owners;
 const uint8_t *iwram;
 const uint16_t *hardware;
 uint8_t *tags;
 unsigned enabled;
 uint16_t *banks;
} FFTA_ArtOwnerFrame;
typedef struct {
 FFTA_ArtOwnerFrame owner;
 FFTA_ArtOamDemands *demands;
 unsigned *extent;
} FFTA_ArtFusedOwnerFrame;
unsigned ffta_art_frame_owners(const FFTA_ArtOwnerFrame *frame);
/* Only immediately after the authenticated native compositor has copied the
 * selected source buffers. Generic callers must use frame_owners instead. */
unsigned ffta_art_frame_native_owners(const FFTA_ArtOwnerFrame *frame);
unsigned ffta_art_frame_fused_owners(const FFTA_ArtFusedOwnerFrame *frame);
void ffta_art_frame_publish(FFTA_ArtPaletteFrame *frame, uint16_t *backup,
                            unsigned count);
#endif
