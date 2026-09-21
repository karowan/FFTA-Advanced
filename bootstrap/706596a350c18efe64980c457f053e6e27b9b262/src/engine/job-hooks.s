.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.macro tail address
    push {r0}
    ldr r0,=\address
    mov lr,r0
    pop {r0}
    bx lr
.endm
.macro saved_call target
    push {r0-r7,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl \target
    mov sp,r4
    str r0,[sp]
    ldr r0,[sp,#32]
    mov lr,r0
    pop {r0-r7}
    add sp,#4
.endm
.align 2
.global ffta_wheel_initial_entry
.thumb_func
ffta_wheel_initial_entry:
    saved_call ffta_wheel_initial
    movs r2,r0
    ldr r0,[r6]
    tail 0x08085c99
.ltorg

.align 2
.global ffta_wheel_input_entry
.thumb_func
ffta_wheel_input_entry:
    pop {r3}
    saved_call ffta_wheel_turn
    cmp r0,#0
    beq 1f
    ldr r6,=0x03002818
    ldr r4,=0x1278
    movs r2,r0
    ldr r0,[r6]
    tail 0x08085c99
1:  ldr r0,=0x03002818
    ldr r2,[r0]
    movs r4,r2
    adds r4,#0x25
    ldrb r3,[r4]
    mov r10,r0
    tail 0x08086179
.ltorg

.align 2
.global ffta_wheel_confirm_entry
.thumb_func
ffta_wheel_confirm_entry:
    pop {r3}
    saved_call ffta_wheel_can_confirm
    cmp r0,#0
    beq 1f
    ldr r1,=0x1d0c
    adds r0,r2,r1
    ldr r0,[r0]
    ldrb r4,[r0,#7]
    movs r1,#0
    tail 0x080861c9
1:  tail 0x08086231
.ltorg

.macro entry name,target
.align 2
.global \name
.thumb_func
\name:
    push {r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl \target
    mov sp,r4
    pop {r4}
    pop {r1}
    bx r1
.endm
entry ffta_job_icon_entry,ffta_job_icon
entry ffta_job_palette_entry,ffta_job_palette
entry ffta_reaction_guard_entry,ffta_reaction_staging_guard

.align 2
.global ffta_original_job_icon
.thumb_func
ffta_original_job_icon:
    push {lr}
    movs r3,r0
    lsls r1,r1,#24
    lsrs r1,r1,#24
    tail 0x080cb9e9
.ltorg
.align 2
.global ffta_original_job_palette
.thumb_func
ffta_original_job_palette:
    push {lr}
    lsls r0,r0,#24
    lsrs r1,r0,#24
    cmp r1,#0x52
    tail 0x080cba1d
.ltorg

.align 2
.global ffta_original_reaction_available
.thumb_func
ffta_original_reaction_available:
    push {r4-r5,lr}
    movs r4,r0
    ldr r3,=0x080cd4d5
    bl invoke_r3
    tail 0x0812e6ad
.ltorg
.thumb_func
invoke_r3:
    bx r3
