.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.macro save
    push {r0-r7,lr}
    mov r7,r12
    push {r7}
    mov r4,sp
    mov r6,sp
    lsrs r6,r6,#3
    lsls r6,r6,#3
    mov sp,r6
.endm
.macro restore_result
    mov sp,r4
    str r0,[sp,#4]
    pop {r7}
    mov r12,r7
    pop {r0-r7}
    add sp,#4
.endm
.macro tail address
    ldr r3,=\address
    bx r3
.endm
.align 2
.global ffta_samurai_turn_end_entry
.thumb_func
ffta_samurai_turn_end_entry:
    pop {r3}
    save
    ldr r0,[r5,#4]
    cmp r0,#0
    beq 1f
    ldr r0,[r0]
1:  mov r1,r8
    bl ffta_samurai_turn_end
    restore_result
    cmp r0,#0
    beq .Lend_original
    movs r0,#127
    tail 0x08096b13
.align 2
.global ffta_wound_turn_wait_entry
.thumb_func
ffta_wound_turn_wait_entry:
    save
    mov r0,r8
    bl ffta_wound_advance
    restore_result
    cmp r0,#0
    beq .Lend_original
    tail 0x08096b15
.Lend_original:
    movs r0,#0
    mov r5,r8
    str r0,[r5,#4]
    movs r0,#5
    strh r0,[r7]
    ldr r0,[r5]
    bl .Lnext_phase
    tail 0x08092fa1
.Lnext_phase:
    tail 0x08099545
.ltorg
.align 2
.global ffta_wound_periodic_entry
.thumb_func
ffta_wound_periodic_entry:
    @ Entered in native9ED38's existing frame with r7 = periodic context.
    movs r4,r7
    adds r4,#0x5e
    movs r1,r7
    adds r1,#0xc9
    movs r0,#32
    strb r0,[r1]
    tail 0x0809f4ef
.ltorg
