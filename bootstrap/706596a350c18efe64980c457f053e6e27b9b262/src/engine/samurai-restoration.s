.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_murasame_magnitude_entry
.thumb_func
ffta_murasame_magnitude_entry:
    push {r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl ffta_murasame_magnitude
    mov sp,r4
    pop {r4}
    pop {r1}
    bx r1
