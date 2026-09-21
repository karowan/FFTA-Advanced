#ifndef FFTA_CURABLE_STATUS_H
#define FFTA_CURABLE_STATUS_H
#include <stdint.h>
/* Shared custom broad-remedy tags. A reservation is not an installed effect.
 * Call after ordinary hit/immunity admission, before applying the explicit
 * context+8 recipient's harmful effect. Nonzero means prevent this effect.
 * Query calls cannot consume stock, draw RNG or alter live state/claims.
 * Inoculated is considered before Auto-Cureall. Self-paid/linked drawbacks
 * are outside this interface. Invoke once per application, not per UI pass. */
enum FFTA_CurableTag {
 FFTA_CURABLE_BLADE_WOUND=1, FFTA_CURABLE_CHALLENGED=2,
 FFTA_CURABLE_WISP_EXPOSURE=3, FFTA_CURABLE_POLKA=4,
 FFTA_CURABLE_HEATHEN_FROLIC=5
};
unsigned ffta_chemist_prevent_custom(const uint8_t *context,unsigned tag);
#endif
