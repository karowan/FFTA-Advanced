.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.macro save
    push {r0-r7,lr}
    mov r7,r12
    push {r7}
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
.endm
.macro restore
    mov sp,r4
    pop {r7}
    mov r12,r7
    pop {r0-r7}
    add sp,#4
.endm
.macro tail address
    push {r0}
    ldr r0,=\address
    mov lr,r0
    pop {r0}
    bx lr
.endm
.align 2
.global ffta_samurai_paid_entry
.thumb_func
ffta_samurai_paid_entry:
    pop {r3}
    subs r4,r0,r4
    cmp r4,#0
    blt 9f
    save
    movs r0,r4
    adds r0,#0x9c
    ldr r0,[r0] @ original SP+74 actor wrapper
    ldr r0,[r0]
    ldr r1,[r4,#0x74] @ original SP+4C global action
    bl ffta_custom_physical_paid
    cmp r0,#0
    beq 8f
    restore
    cmp r4,#0
    ldr r1,[sp,#0x74]
    ldr r0,[r1]
    strh r4,[r0,#0x1c]
    tail 0x080a45d5
8:  restore
9:  tail 0x080a4969
.ltorg
.align 2
.global ffta_samurai_law_entry
.thumb_func
ffta_samurai_law_entry:
    push {r0-r7,lr}
    ldr r0,=0x0200f3f0
    mov r1,r8
    movs r2,r6
    movs r3,r7
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_samurai_law_hit
    mov sp,r4
    str r0,[sp]
    ldr r0,[sp,#32]
    mov lr,r0
    pop {r0-r7}
    add sp,#4
    push {r0}
    ldr r0,=0x08131b21
    bl .Lsamurai_law_call
    pop {r1}
    cmp r1,#0
    bne 1f
    ldr r1,=0x08134351
    cmp r0,#0
    bne 2f
    tail 0x08134355
1:  tail 0x08134383
2:  tail 0x081343b7
.Lsamurai_law_call:
    bx r0
.ltorg
.align 2
.global ffta_samurai_attempt_entry
.thumb_func
ffta_samurai_attempt_entry:
    pop {r3}
    save
    movs r0,r4
    adds r0,#0x9c
    ldr r0,[r0]
    ldr r0,[r0]
    ldr r1,[r4,#0x74]
    mov r2,r10
    movs r3,#0xb0
    lsls r3,r3,#2
    ldrb r2,[r2,r3]
    bl ffta_samurai_after_attempt
    restore
    ldr r2,[sp,#0x64]
    cmp r2,#0xe9
    bne 1f
    mov r3,r10
    ldrh r0,[r3,#4]
    tail 0x080a467d
1:  tail 0x080a4687
.ltorg
.align 2
.global ffta_samurai_execute_entry
.thumb_func
ffta_samurai_execute_entry:
    pop {r3}
    push {r4-r7,lr}
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    sub sp,#16
    ldr r5,[r4,#20]
    str r5,[sp]
    ldr r5,[r4,#24]
    str r5,[sp,#4]
    ldr r5,[r4,#28]
    str r5,[sp,#8]
    ldr r5,[r4,#32]
    str r5,[sp,#12]
    bl ffta_samurai_execute
    mov sp,r4
    pop {r4-r7}
    pop {r1}
    bx r1
.align 2
.global ffta_original_samurai_execute
.thumb_func
ffta_original_samurai_execute:
    push {r4-r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    push {r5-r7}
    sub sp,#0xb8
    tail 0x080a4349
.ltorg
.align 2
.global ffta_samurai_law_status_entry
.thumb_func
ffta_samurai_law_status_entry:
    pop {r3}
    push {r4-r5,lr}
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    sub sp,#8
    ldr r5,[r4,#12]
    str r5,[sp]
    ldr r5,[r4,#16]
    str r5,[sp,#4]
    bl ffta_samurai_law_status
    mov sp,r4
    pop {r4-r5}
    pop {r1}
    bx r1
.align 2
.global ffta_original_samurai_law_status
.thumb_func
ffta_original_samurai_law_status:
    push {r4-r7,lr}
    mov r7,r8
    push {r7}
    movs r7,r0
    movs r4,r1
    ldr r6,[sp,#24]
    tail 0x081342d9
.ltorg
