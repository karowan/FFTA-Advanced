.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_snapshot_native_reaction_entry
.thumb_func
ffta_snapshot_native_reaction_entry:
    pop {r3}
    push {r0-r7,lr}
    mov r4,sp
    mov r0,sp
    adds r0,#36
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_snapshot_native_reaction
    mov sp,r4
    pop {r0-r7}
    pop {r4}
    mov lr,r4
    mov r2,r9
    ldr r0,[r2]
    ldr r0,[r0]
    movs r1,#44
    ldr r3,[sp,#0x304]
    adds r4,r3,#0
    push {r0}
    ldr r0,=0x080a28ef
    mov ip,r0
    pop {r0}
    bx ip
.ltorg
.align 2
.global ffta_snapshot_result_entry
.thumb_func
ffta_snapshot_result_entry:
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
    bl ffta_snapshot_result
    mov sp,r4
    pop {r4-r7}
    pop {r1}
    bx r1
.align 2
.global ffta_original_snapshot_result
.thumb_func
ffta_original_snapshot_result:
    push {r4-r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    push {r5-r7}
    ldr r4,=0xfffffcc0
    add sp,r4
    mov r9,r0
    push {r0}
    ldr r0,=0x080a23c9
    mov lr,r0
    pop {r0}
    bx lr
.ltorg
