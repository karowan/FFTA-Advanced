.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_recruit_prerequisite_entry
.thumb_func
ffta_recruit_prerequisite_entry:
    pop {r3}
    push {r0-r7,lr}
    movs r0,r7
    movs r1,r5
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_recruit_prerequisite_count
    mov sp,r4
    cmp r0,#0
    blt .Lnative
    str r0,[sp,#12]
    pop {r0-r7}
    pop {r1}
    mov lr,r1
    ldr r1,=0x08062113
    bx r1
.Lnative:
    pop {r0-r7}
    pop {r1}
    mov lr,r1
    adds r0,r5,#0
    adds r1,r5,#0
    movs r2,#0x25
    bl .Ljob_value
    adds r4,r0,#0
    push {r1}
    ldr r1,=0x080620b9
    mov lr,r1
    pop {r1}
    bx lr
.Ljob_value:
    ldr r3,=0x080c8571
    bx r3
.ltorg
