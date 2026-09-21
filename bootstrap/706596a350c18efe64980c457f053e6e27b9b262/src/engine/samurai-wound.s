.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_samurai_success_entry
.thumb_func
ffta_samurai_success_entry:
    pop {r3}
    push {r0-r7,lr}
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    ldr r0,=0x0200f3f0
    mov r1,r9
    movs r2,r6
    bl ffta_samurai_magnitude
    mov sp,r4
    str r0,[sp,#20] @ native r5 receives the magnitude
    ldr r0,[sp,#32]
    mov lr,r0
    pop {r0-r7}
    add sp,#4
    movs r0,r5
    ldr r1,=0x080a3077
    cmp r4,#1
    bgt 1f
    ldr r3,=0x080a307d
    bx r3
1:  ldr r3,=0x080a3087
    bx r3
.ltorg
