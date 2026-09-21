.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_status_icon_entry
.thumb_func
ffta_status_icon_entry:
    push {r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl ffta_status_icon
    mov sp,r4
    pop {r4}
    pop {r1}
    bx r1
.align 2
.global ffta_original_status_icon
.thumb_func
ffta_original_status_icon:
    push {r4,lr}
    adds r4,r0,#0
    lsls r1,r1,#16
    lsrs r0,r1,#16
    ldr r3,=0x0809da15
    bx r3
.ltorg

.align 2
.global ffta_status_next_entry
.thumb_func
ffta_status_next_entry:
    pop {r3}
    push {r0-r7,lr}
    mov r7,r12
    push {r7}
    movs r0,r6
    ldrb r1,[r4,#2]
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_status_next_key
    mov sp,r4
    ldr r1,[sp,#20]
    strb r0,[r1,#2]
    pop {r7}
    mov r12,r7
    pop {r0-r7}
    pop {r0}
    mov lr,r0
    ldr r0,=0x0809dd63
    bx r0
.ltorg

.align 2
.global ffta_status_visual_entry
.thumb_func
ffta_status_visual_entry:
    pop {r3}
    push {r0-r7,lr}
    mov r7,r12
    push {r7}
    ldr r0,[r6,#0x48]
    str r0,[sp,#4]
    mov r1,r8
    ldrb r1,[r1]
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_status_visual
    mov sp,r4
    str r0,[sp,#8]
    pop {r7}
    mov r12,r7
    pop {r0-r7}
    pop {r2}
    mov lr,r2
    movs r2,#0
    cmp r2,#1
    movs r2,#0
    ldr r3,=0x01430000
    strh r1,[r0,#0x12]
    strh r2,[r0,#0x16]
    push {r4}
    ldr r4,=0x08097ae7
    mov lr,r4
    pop {r4}
    bx lr
.ltorg
