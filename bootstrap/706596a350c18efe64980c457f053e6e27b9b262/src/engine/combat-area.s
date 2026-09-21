.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_area_list_entry
.thumb_func
ffta_area_list_entry:
    pop {r3}
    push {r4,r5,lr}
    mov r4,sp
    mov r5,sp
    subs r5,#16
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    ldr r5,[r4,#8]
    str r5,[sp]
    str r7,[sp,#4]
    mov r5,r8
    str r5,[sp,#8]
    bl ffta_area_list_dispatch
    mov sp,r4
    pop {r4,r5}
    pop {r1}
    bx r1

.align 2
.global ffta_original_area_list
.thumb_func
ffta_original_area_list:
    push {r4-r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    push {r5-r7}
    sub sp,#32
    push {r0}
    ldr r0,=0x080b4a29
    mov lr,r0
    pop {r0}
    bx lr
.ltorg

@ Shared pre-action facing animation at96A40 uses the chosen arc direction,
@ before9D3A8 writes the wrapper and the action constructor captures it.
.align 2
.global ffta_arc_launch_entry
.thumb_func
ffta_arc_launch_entry:
    pop {r3}
    push {r0-r7,lr}
    mov r1,r8
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_arc_launch_facing
    mov sp,r4
    str r0,[sp]
    pop {r0-r7}
    add sp,#4
    mov r1,r8
    adds r1,#0x88
    strb r0,[r1]
    mov r0,r8
    adds r0,#0x8a
    strb r4,[r0]
    push {r2}
    ldr r2,=0x08096a4d
    mov lr,r2
    pop {r2}
    bx lr
.ltorg

@ AI-only action scheduling at93A66. Preserve the incoming carry/overflow:
@ displaced MOVS updates N/Z but leaves C/V unchanged.
.align 2
.global ffta_arc_ai_entry
.thumb_func
ffta_arc_ai_entry:
    pop {r3}
    push {r0-r7,lr}
    movs r7,#0
    bcc 1f
    movs r7,#1
1:
    bvc 2f
    movs r6,#2
    orrs r7,r6
2:
    mov r0,r8
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_arc_ai_facing
    mov sp,r4
    cmp r7,#0
    beq 3f
    cmp r7,#1
    beq 4f
    cmp r7,#2
    beq 5f
    movs r0,#1
    lsls r0,r0,#31
    adds r0,r0,r0
    b 6f
3:
    movs r0,#0
    adds r0,#0
    b 6f
4:
    movs r0,#0
    subs r0,#0
    b 6f
5:
    movs r0,#1
    lsls r0,r0,#31
    subs r0,#1
    adds r0,#1
6:
    pop {r0-r7}
    add sp,#4
    mov r1,r8
    ldr r0,[r1,#4]
    str r0,[r1,#8]
    movs r2,#0x13
    strh r2,[r7]
    push {r3}
    ldr r3,=0x08093a71
    mov lr,r3
    pop {r3}
    bx lr
.ltorg

@ UI confirmation must retain the selected arc direction before the native
@ animation rotates the actor toward an automatically selected flank target.
.align 2
.global ffta_arc_confirm_entry
.thumb_func
ffta_arc_confirm_entry:
    pop {r3}
    push {r0-r7,lr}
    movs r7,#0
    bvc 1f
    movs r7,#1
1:
    movs r0,r3
    mov r1,r8
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_arc_confirm_facing
    mov sp,r4
    str r0,[sp,#12]
    cmp r7,#0
    beq 2f
    movs r0,#1
    lsls r0,r0,#31
    subs r0,#1
2:
    pop {r0-r7}
    add sp,#4
    mov r0,r8
    ldr r1,[r0]
    lsls r0,r3,#24
    asrs r6,r0,#24
    movs r0,#0x1f
    push {r2}
    ldr r2,=0x080b6fc1
    mov lr,r2
    pop {r2}
    bx lr
.ltorg

@ A3ABA..A3AC4 follows the native direction store. Correct only that store
@ for an arc, then replay the native flag setup and both branch outcomes.
.align 2
.global ffta_arc_commit_entry
.thumb_func
ffta_arc_commit_entry:
    pop {r3}
    push {r0-r7,lr}
    movs r0,r7
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_arc_commit_facing
    mov sp,r4
    pop {r0-r7}
    add sp,#4
    ldrh r1,[r7,#4]
    ldr r4,[sp,#0x360]
    cmp r4,#0
    beq 1f
    movs r0,#0x10
    push {r2}
    ldr r2,=0x080a3ac5
    mov lr,r2
    pop {r2}
    bx lr
1:
    push {r2}
    ldr r2,=0x080a3ac7
    mov lr,r2
    pop {r2}
    bx lr
.ltorg
