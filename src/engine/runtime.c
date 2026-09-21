#include <stddef.h>

/* GCC may emit this for initialized local arrays even in freestanding mode.
 * Volatile stores prevent this definition being transformed into itself. */
void *memset(void *destination, int value, size_t count) {
    volatile unsigned char *p=destination;
    for (size_t i=0; i<count; ++i) p[i]=(unsigned char)value;
    return destination;
}
