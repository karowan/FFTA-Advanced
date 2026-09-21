#ifndef FFTA_CUSTOM_LAWS_H
#define FFTA_CUSTOM_LAWS_H
#include <stdint.h>
/* Only after the actual effect was stored. QUERY/copy/reaction calls cannot
 * create primary law evidence. Refreshes count even if state bytes match. */
void ffta_custom_law_applied(const uint8_t *unit);
unsigned ffta_custom_law_forecast(const uint8_t *,const uint8_t *,unsigned);
int ffta_custom_law_reference(int,unsigned,const uint8_t *,const uint8_t *);
#endif
