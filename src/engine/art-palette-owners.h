#ifndef FFTA_ART_PALETTE_OWNERS_H
#define FFTA_ART_PALETTE_OWNERS_H
#include <stdint.h>

typedef struct {
    uint16_t attributes[3];
    uint8_t owner, reserved;
} FFTA_ArtOwnerEntry;

/* Caller-owned transient state. Reset the selected bank with native 1194;
 * record each 216F8 emission after it returns. Never store in a unit/save. */
typedef struct {
    FFTA_ArtOwnerEntry entries[2][128];
    uint32_t ready[2];
} FFTA_ArtOwners;

void ffta_art_owners_reset(FFTA_ArtOwners *, unsigned bank);
unsigned ffta_art_owners_record(FFTA_ArtOwners *, unsigned bank,
                              const uint16_t *source, unsigned before,
                              unsigned after, unsigned resource);
/* Read native compositor inputs before 12BC and its hardware OAM afterwards.
 * Successful output contains 128 tags (0..9 or 255). Failure writes nothing.
 * IWRAM is the full native 32KiB image, not a changed copy of its OAM counts. */
unsigned ffta_art_owners_compose(const FFTA_ArtOwners *, const uint8_t *iwram,
                               const uint16_t *hardware, uint8_t *output);
/* Fused enabled-owner tagging/native-bank collection. Returns requested mask;
 * zero means no enabled owner or refusal. Refusal writes neither output. */
unsigned ffta_art_owners_compose_filtered(const FFTA_ArtOwners *, const uint8_t *,
        const uint16_t *, uint8_t *, unsigned enabled, uint16_t native_banks[10]);
#endif
