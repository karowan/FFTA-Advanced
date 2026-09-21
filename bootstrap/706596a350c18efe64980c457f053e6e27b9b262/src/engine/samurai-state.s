.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_centered_turn_end_entry
.thumb_func
ffta_centered_turn_end_entry:
    pop {r3}
    push {r0-r7,lr}
    mov r7,r12
    push {r7}
    ldr r0,[r5,#4]
    cmp r0,#0
    beq 1f
    ldr r0,[r0]
1:  mov r4,sp
    mov r6,sp
    lsrs r6,r6,#3
    lsls r6,r6,#3
    mov sp,r6
    bl ffta_centered_turn_end
    mov sp,r4
    pop {r7}
    mov r12,r7
    pop {r0-r7}
    add sp,#4
    @ Original92F94..92FA0. Native99544 recomputes flags before returning;
    @ its caller immediately stores and compares its result.
    str r0,[r5,#4]
    movs r0,#5
    strh r0,[r7]
    ldr r0,[r5]
    bl .Lnext_phase
    push {r1}
    ldr r1,=0x08092fa1
    mov lr,r1
    pop {r1}
    bx lr
.Lnext_phase:
    push {r3}
    ldr r3,=0x08099545
    mov r12,r3
    pop {r3}
    bx r12
.ltorg
