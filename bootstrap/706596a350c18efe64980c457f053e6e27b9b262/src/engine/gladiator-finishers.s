.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_executioner_chance_entry
.thumb_func
ffta_executioner_chance_entry:
    pop {r3}
    push {r4,lr}
    mov r0,lr
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl ffta_executioner_chance_dispatch
    mov sp,r4
    pop {r4}
    pop {r1}
    bx r1

.align 2
.global ffta_original_finisher_chance
.thumb_func
ffta_original_finisher_chance:
    push {r4,r5,lr}
    ldr r5,=0x0200f3f0
    ldr r0,[r5]
    ldr r1,[r5,#4]
    ldr r2,[r5,#0x30]
    ldrb r2,[r2,#1]
    ldr r3,=0x08131385
    bx r3
.ltorg

@ Installer B5816..B5820: ten-byte r3-preserving veneer. Native ordinary
@ chance in r4 has already been capped100; r8=action,r6=target wrapper.
@ Replays UI argument setup, preserving incoming V across the C boundary.
.align 2
.global ffta_executioner_preview_entry
.thumb_func
ffta_executioner_preview_entry:
    pop {r3}
    push {r0-r7,lr}
    movs r7,#0
    bvc 1f
    movs r7,#1
1:
    movs r0,r4
    mov r1,r8
    ldr r2,[r6]
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_executioner_preview_chance
    mov sp,r4
    str r0,[sp,#16]
    cmp r7,#0
    beq 2f
    movs r0,#1
    lsls r0,r0,#31
    subs r0,#1
2:
    ldr r0,[sp,#32]
    mov lr,r0
    pop {r0-r7}
    add sp,#4
    lsls r1,r4,#24
    lsrs r1,r1,#24
    mov r3,r10
    lsls r2,r3,#16
    asrs r2,r2,#16
    push {r0}
    ldr r0,=0x080b5821
    mov lr,r0
    pop {r0}
    bx lr
.ltorg

.align 2
.global ffta_executioner_roll_entry
.thumb_func
ffta_executioner_roll_entry:
    pop {r3}
    push {r0-r7,lr}
    movs r0,r4
    mov r5,sp
    mov r6,sp
    lsrs r6,r6,#3
    lsls r6,r6,#3
    mov sp,r6
    bl ffta_executioner_resolve_chance
    mov sp,r5
    str r0,[sp,#16]
    ldr r0,[sp,#32]
    mov lr,r0
    pop {r0-r7}
    add sp,#4
    movs r0,r4
    bl .Lroll_native
    lsls r0,r0,#24
    cmp r0,#0
    bne .Lhit
    push {r1}
    ldr r1,=0x080a3011
    mov lr,r1
    pop {r1}
    bx lr
.Lhit:
    push {r1}
    ldr r1,=0x080a305b
    mov lr,r1
    pop {r1}
    bx lr
.Lroll_native:
    ldr r3,=0x0812f1dd
    bx r3
.ltorg
