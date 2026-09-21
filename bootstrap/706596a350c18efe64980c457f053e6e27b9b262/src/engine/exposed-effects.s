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
    ldr r0,[sp,#32]
    mov lr,r0
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
.global ffta_exposed_stage_entry
.thumb_func
ffta_exposed_stage_entry:
    pop {r3}
    movs r4,r0
    push {r3}
    ldr r3,=0x08133989
    bl 1f
    muls r4,r0
    ldr r3,=0x0812f359
    bl 1f
    pop {r3}
    save
    ldr r0,[r4,#20]
    ldr r1,[r4,#24]
    bl ffta_exposed_native_stage
    str r0,[r4,#20]
    restore
    tail 0x08131b57
1:  bx r3
.ltorg
.align 2
.global ffta_exposed_preview_entry
.thumb_func
ffta_exposed_preview_entry:
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
    bl ffta_exposed_preview
    mov sp,r4
    pop {r4-r5}
    pop {r1}
    bx r1
.global ffta_original_exposed_preview
.thumb_func
ffta_original_exposed_preview:
    push {r4-r7,lr}
    mov r7,r8
    push {r7}
    sub sp,#12
    movs r6,r0
    mov r8,r1
    tail 0x0813020d
.ltorg
.align 2
.global ffta_exposed_combo_entry
.thumb_func
ffta_exposed_combo_entry:
    pop {r3}
    push {r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl ffta_exposed_combo
    mov sp,r4
    pop {r4}
    pop {r1}
    bx r1
.global ffta_original_exposed_combo
.thumb_func
ffta_original_exposed_combo:
    push {r4-r7,lr}
    sub sp,#16
    movs r5,r0
    movs r6,r1
    movs r7,r2
    ldr r3,=0x08130869
    bl 1f
    tail 0x08130463
1:  bx r3
.ltorg
.align 2
.global ffta_exposed_event_ko_entry
.thumb_func
ffta_exposed_event_ko_entry:
    pop {r3}
    ldrb r1,[r4,#2]
    cmp r1,#0
    bne 2f
    save
    ldr r0,[r4,#24]
    ldr r0,[r0]
    movs r1,#2
    bl ffta_exposed_expire
    restore
    movs r1,#0
    ldr r0,[r5]
    strh r1,[r0,#0x18]
    ldr r0,[r5]
    tail 0x081230ff
2:  tail 0x08123101
.ltorg
.align 2
.global ffta_exposed_paid_entry
.thumb_func
ffta_exposed_paid_entry:
    pop {r3}
    subs r4,r0,r4
    cmp r4,#0
    blt 8f
    save
    movs r0,r4
    adds r0,#0x9c
    ldr r0,[r0] @ original SP+74: actor wrapper
    ldr r0,[r0]
    ldr r1,[r4,#0x74] @ original SP+4C: global action
    bl ffta_exposed_paid_commit
    cmp r0,#0
    beq 9f
    restore
    ldr r1,[sp,#0x74]
    ldr r0,[r1]
    strh r4,[r0,#0x1c]
    tail 0x080a45d5
9:  restore
8:  tail 0x080a4969
.ltorg
.align 2
.global ffta_exposed_turn_entry
.thumb_func
ffta_exposed_turn_entry:
    pop {r3}
    save
    ldr r0,[r4,#4]
    ldr r0,[r0]
    movs r1,#1
    bl ffta_exposed_expire
    restore
    ldr r0,[r0]
    movs r1,#0x82
    lsls r1,r1,#1
    adds r0,r0,r1
    ldrb r1,[r0]
    movs r0,#0x34
    tail 0x0809302f
.ltorg
.align 2
.global ffta_exposed_battle_end_entry
.thumb_func
ffta_exposed_battle_end_entry:
    pop {r3}
    save
    bl ffta_exposed_battle_end
    restore
    ldr r0,=0x02000080
    movs r1,#24
    push {r3}
    ldr r3,=0x0809a951
    bl 1f
    pop {r3}
    ldr r1,=0x0200f390
    adds r1,#0x94
    tail 0x08095221
1:  bx r3
.ltorg
.align 2
.global ffta_exposed_reset_entry
.thumb_func
ffta_exposed_reset_entry:
    pop {r3}
    save
    ldr r0,[r4,#4]
    movs r1,#2
    bl ffta_exposed_expire
    restore
    push {r4,lr}
    adds r4,r0,#0
    movs r1,#0
    ldr r3,=0x080cdd1d
    mov lr,r3
    .short 0xf800
    adds r0,r4,#0
    tail 0x080972a5
.ltorg
.align 2
.global ffta_exposed_petrify_entry
.thumb_func
ffta_exposed_petrify_entry:
    pop {r3}
    save
    ldr r0,[r4,#4]
    movs r1,#6
    ldr r2,[r4,#8]
    bl ffta_exposed_native_status
    restore
    push {lr}
    lsls r1,r1,#24
    adds r2,r0,#0
    adds r2,#0xe8
    movs r3,#0x41
    negs r3,r3
    tail 0x080cdddd
.ltorg
.align 2
.global ffta_exposed_status_entry
.thumb_func
ffta_exposed_status_entry:
    pop {r3}
    save
    ldr r0,[r4,#4]
    ldr r1,[r4,#8]
    ldr r2,[r4,#12]
    bl ffta_exposed_native_status
    restore
    push {r4,lr}
    lsls r1,r1,#16
    lsls r2,r2,#24
    lsrs r3,r1,#19
    adds r3,#0xe8
    adds r4,r0,r3
    tail 0x080cd891
.ltorg
.align 2
.global ffta_exposed_job_entry
.thumb_func
ffta_exposed_job_entry:
    pop {r3}
    save
    ldr r0,[r4,#20]
    ldr r1,[r4,#28]
    bl ffta_exposed_job_change
    restore
    strb r6,[r4,#7]
    ldrb r0,[r4,#8]
    cmp r0,r6
    bne 1f
    strb r7,[r4,#8]
1:  ldrb r0,[r4,#5]
    tail 0x080c8c49
.ltorg
.align 2
.global ffta_exposed_cureall_entry
.thumb_func
ffta_exposed_cureall_entry:
    push {r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl ffta_exposed_cureall
    mov sp,r4
    pop {r4}
    pop {r1}
    bx r1
