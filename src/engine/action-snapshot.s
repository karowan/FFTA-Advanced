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
    sub sp,#24
    ldr r5,[r4,#20]
    str r5,[sp]
    ldr r5,[r4,#24]
    str r5,[sp,#4]
    ldr r5,[r4,#28]
    str r5,[sp,#8]
    ldr r5,[r4,#32]
    str r5,[sp,#12]
    ldr r5,[r4,#16] @ authenticated native caller return address
    str r5,[sp,#16]
    movs r5,r4
    adds r5,#20 @ original native caller SP, not an inferred unit root
    str r5,[sp,#20]
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
.align 2
.global ffta_action_hp_apply_entry
.thumb_func
ffta_action_hp_apply_entry:
    pop {r3}
    push {r4-r5,lr}
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_action_hp_apply
    mov sp,r4
    pop {r4-r5}
    pop {r1}
    bx r1
.align 2
.global ffta_original_action_hp_apply
.thumb_func
ffta_original_action_hp_apply:
    push {r4-r7,lr}
    movs r6,r0
    lsls r1,r1,#16
    lsrs r5,r1,#16
    ldr r3,=0x080c8281
    bl .Laction_hp_native_call
    ldr r3,=0x080a221d
    bx r3
.Laction_hp_native_call:
    bx r3
.ltorg
@ Rebindable optional providers. Each default owns16bytes for an overlay jump.
@ Strong definitions replace these at link time; independent job overlays may
@ redirect a checked default stub to a composed provider in their reservation.
.macro optional_provider name
.align 2
.weak \name
.thumb_func
\name:
    movs r0,#0
    bx lr
    .space 12,0
.endm
optional_provider ffta_additional_beneficial
optional_provider ffta_additional_snapshot_flags
optional_provider ffta_additional_extra_snapshot_flags
optional_provider ffta_additional_snapshot_storage
optional_provider ffta_additional_result_storage
optional_provider ffta_additional_action_limit
optional_provider ffta_additional_action_category
optional_provider ffta_additional_action_event

optional_provider ffta_additional_hp_loss

optional_provider ffta_additional_reaction_queue
optional_provider ffta_additional_reaction_wrapper
