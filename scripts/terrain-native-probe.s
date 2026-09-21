.syntax unified
.cpu arm7tdmi
.arm
.section .text
.global _start
_start:
    ldr sp, =0x03007e00
    adr r0, thumb_entry+1
    bx r0
.thumb
.thumb_func
thumb_entry:
    ldr r4, =0x0203ffe0
    movs r0, #1
    str r0, [r4, #4]
wait_request:
    ldr r0, [r4]
    cmp r0, #0
    beq wait_request
    subs r0, #1
    movs r1, #88
    muls r0, r1
    ldr r5, =0x08569104
    adds r6, r0, r5
    ldr r0, [r6, #4]
    adds r0, r0, r5
    ldr r3, =0x0801f1a9
    bl call_r3
    ldr r0, [r6, #8]
    adds r0, r0, r5
    ldr r3, =0x0801f2ed
    bl call_r3
    ldr r0, [r6, #16]
    adds r0, r0, r5
    ldr r3, =0x0801f439
    bl call_r3
    movs r0, #0
    str r0, [r4]
    ldr r0, [r4, #4]
    adds r0, #1
    str r0, [r4, #4]
    b wait_request
.thumb_func
call_r3:
    bx r3
.ltorg
