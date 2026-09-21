.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_samurai_area_entry
.thumb_func
ffta_samurai_area_entry:
    pop {r3}
    push {r4,r5,lr}
    mov r4,sp
    mov r5,sp
    subs r5,#16
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    ldr r5,[r4,#8]
    str r5,[sp]
    str r7,[sp,#4]
    mov r5,r8
    str r5,[sp,#8]
    bl ffta_samurai_area_dispatch
    mov sp,r4
    pop {r4,r5}
    pop {r1}
    bx r1
