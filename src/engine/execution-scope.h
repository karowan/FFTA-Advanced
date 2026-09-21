#ifndef FFTA_EXECUTION_SCOPE_H
#define FFTA_EXECUTION_SCOPE_H
#include <stdint.h>
typedef struct FFTA_ExecutionScope {
    uint32_t magic;
    uintptr_t self;
    struct FFTA_ExecutionScope *previous;
    const uint8_t *actor,*target;
    uint8_t *object,*row;
    int reference;
    unsigned action,armed,ready;
} FFTA_ExecutionScope;
unsigned ffta_execution_open(FFTA_ExecutionScope *,const uint8_t *,unsigned);
void ffta_execution_close(FFTA_ExecutionScope *);
void ffta_execution_arm(uint8_t *,uint8_t *,const uint8_t *);
void ffta_execution_capture(int,unsigned,const uint8_t *,const uint8_t *);
void ffta_execution_disarm(void);
unsigned ffta_execution_take(uint8_t *,uint8_t *,const uint8_t *,int *);
#endif
