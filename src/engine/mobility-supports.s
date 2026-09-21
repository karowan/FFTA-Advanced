.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_move_support_entry
.thumb_func
ffta_move_support_entry:
    pop {r3}
    push {r4,r5,lr}
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_move_with_support
    mov sp,r4
    pop {r4,r5}
    pop {r1}
    bx r1

.align 2
.global ffta_original_move
.thumb_func
ffta_original_move:
    push {r4-r7,lr}
    movs r4,r0
    movs r1,#0x1e
    bl .Ljob_value
    lsls r0,r0,#24
    push {r1}
    ldr r1,=0x080ca3a1
    mov lr,r1
    pop {r1}
    bx lr
.Ljob_value:
    ldr r3,=0x080c92f1
    bx r3
.ltorg

.align 2
.global ffta_grace_evade_entry
.thumb_func
ffta_grace_evade_entry:
    pop {r3}
    push {r0-r7,lr}
    movs r1,#0
    ldrsb r0,[r0,r1]
    movs r1,r7
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_grace_evade_divisor
    mov sp,r4
    str r0,[sp,#4]
    pop {r0-r7}
    add sp,#4
    movs r0,r6
    bl .Ldivide
    adds r4,r0,#0
    push {r2}
    ldr r2,=0x0812c8a9
    mov lr,r2
    pop {r2}
    bx lr
.Ldivide:
    ldr r3,=0x081426b9
    bx r3
.ltorg
