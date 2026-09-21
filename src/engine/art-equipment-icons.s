.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_art_equipment_entry
.thumb_func
ffta_art_equipment_entry:
    mov r2,lr
    movs r3,r5
    push {r4-r6,lr}
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_art_equipment_draw
    mov sp,r4
    pop {r4-r6}
    pop {r1}
    bx r1
