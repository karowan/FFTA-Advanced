.syntax unified
.cpu arm7tdmi
.thumb
.section .text

@ Native Thumb callers use both stack residues. Preserve r4 and the original
@ return address while supplying an 8-byte aligned C call boundary.
.macro ability_entry entry, target
.align 2
.global \entry
.thumb_func
\entry:
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
ability_entry ffta_ability_available_entry, ffta_ability_available
ability_entry ffta_ability_grant_entry, ffta_ability_grant
ability_entry ffta_job_mastered_entry, ffta_job_mastered
ability_entry ffta_commands_entry, ffta_commands
ability_entry ffta_command_browse_entry, ffta_command_browse
ability_entry ffta_import_abilities_entry, ffta_import_with_abilities
ability_entry ffta_give_abilities_entry, ffta_give_with_abilities

.align 2
.global ffta_original_commands
.thumb_func
ffta_original_commands:
    push {r4-r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    push {r5-r7}
    sub sp,#4
    push {r0}
    ldr r0,=0x080c8ec9
    mov lr,r0
    pop {r0}
    bx lr
.ltorg

.align 2
.global ffta_original_command_browse
.thumb_func
ffta_original_command_browse:
    push {r4-r5,lr}
    sub sp,#4
    lsls r0,r0,#24
    lsrs r1,r0,#24
    push {r0}
    ldr r0,=0x0807d8f5
    mov lr,r0
    pop {r0}
    bx lr
.ltorg

.align 2
.global ffta_original_import_abilities
.thumb_func
ffta_original_import_abilities:
    push {r4-r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    push {r0}
    ldr r0,=0x080c9f91
    mov lr,r0
    pop {r0}
    bx lr
.ltorg

.align 2
.global ffta_native_clear_entry
.thumb_func
ffta_native_clear_entry:
    push {r0-r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl ffta_on_unit_clear
    mov sp,r4
    ldr r0,[sp,#20]
    mov lr,r0
    pop {r0-r4}
    add sp,#4
    ldr r2,=0x03005e79
    bx r2
.ltorg

.align 2
.global ffta_sort_sidecars
.thumb_func
ffta_sort_sidecars:
    push {r0-r7,lr}
    movs r1,r4
    movs r2,r5
    ldr r0,=0x02000000
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl ffta_swap_extra
    mov sp,r4
    ldr r0,[sp,#32]
    mov lr,r0
    pop {r0-r7}
    add sp,#4
    @ Displaced first two instructions of the foundation scratch cleanup.
    ldr r0,=0x02002fc4
    movs r1,#0
    bx lr
.ltorg

@ Interior hooks enter with r3 saved by the installed absolute jump. Preserve
@ every native live low register except r0, the explicit helper result.
.macro ap_call target, unit, index
    pop {r3}
    push {r0-r7,lr}
.ifc \unit,r8
    mov r0,r8
.else
.ifc \unit,r10
    mov r0,r10
.else
    movs r0,\unit
.endif
.endif
.ifc \index,r8
    mov r1,r8
.else
    movs r1,\index
.endif
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
.macro ap_tail address
    push {r0}
    ldr r0,=\address
    mov lr,r0
    pop {r0}
    bx lr
.endm
.macro read_mastery name, unit, address
.align 2
.global \name
.thumb_func
\name:
    ap_call ffta_ap_value,\unit,r5
    movs r4,#0x7f
    ands r4,r0
    ap_tail \address
.ltorg
.endm
read_mastery ffta_ap_remove_read,r7,0x080caff7
read_mastery ffta_ap_replace_read,r7,0x080cb155
read_mastery ffta_ap_candidate_read,r8,0x080caed1

.align 2
.global ffta_ap_results
.thumb_func
ffta_ap_results:
    ap_call ffta_ap_address,r8,r6
    cmp r0,#0
    beq 1f
    movs r7,r0
    ldrb r4,[r7]
    mov r5,r8
    ldrb r0,[r5,#6]
    ap_tail 0x0804903f
1:
    ap_tail 0x080490a7
.ltorg

.align 2
.global ffta_ap_item_grant
.thumb_func
ffta_ap_item_grant:
    ap_call ffta_ability_grant,r5,r1
    ap_tail 0x080ccf8d
.ltorg

.macro revoke name,address
.align 2
.global \name
.thumb_func
\name:
    ap_call ffta_ability_revoke,r7,r5
    ap_tail \address
.ltorg
.endm
revoke ffta_ap_remove_clear,0x080cb045
revoke ffta_ap_replace_clear,0x080cb1a1

.align 2
.global ffta_ap_typed_available
.thumb_func
ffta_ap_typed_available:
    ap_call ffta_ap_value,r8,r1
    movs r1,r0
    movs r0,#0x80
    ands r0,r1
    ap_tail 0x080cd07f
.ltorg

.align 2
.global ffta_ap_typed_known
.thumb_func
ffta_ap_typed_known:
    ap_call ffta_ap_value,r8,r2
    cmp r0,#0
    beq 1f
    ap_tail 0x080cd1ab
1:
    ap_tail 0x080cd1bd
.ltorg

.align 2
.global ffta_ap_party_filter
.thumb_func
ffta_ap_party_filter:
    pop {r3}
    ldr r0,[r1]
    push {r3}
    ap_call ffta_ap_value,r0,r6
    cmp r0,#0
    beq 1f
    ap_tail 0x0807b9b7
1:
    ap_tail 0x0807b9ff
.ltorg

.align 2
.global ffta_ap_party_row
.thumb_func
ffta_ap_party_row:
    pop {r3}
    ldr r0,[r1]
    push {r3}
    ap_call ffta_ap_value,r0,r6
    strb r0,[r4,#14]
    mov r1,r10
    ap_tail 0x0807b9d9
.ltorg

.align 2
.global ffta_ap_menu_filter
.thumb_func
ffta_ap_menu_filter:
    pop {r3}
    ldr r0,[r2,r1]
    push {r3}
    ap_call ffta_ap_value,r0,r6
    cmp r0,#0
    beq 1f
    ap_tail 0x0807c36f
1:
    ap_tail 0x0807c411
.ltorg

.align 2
.global ffta_ap_job_filter
.thumb_func
ffta_ap_job_filter:
    pop {r3}
    ldr r0,[r0]
    push {r3}
    ap_call ffta_ap_value,r0,r6
    cmp r0,#0
    beq 1f
    ap_tail 0x0807c4a9
1:
    ap_tail 0x0807c53b
.ltorg

.macro menu_row name, destination
.align 2
.global \name
.thumb_func
\name:
    pop {r3}
    ldr r3,=0x524
    add r3,sp
    ldr r3,[r3]
    push {r3}
    ap_call ffta_ap_value,r1,r3
    strb r0,[r4,#14]
    ap_tail \destination
.ltorg
.endm
menu_row ffta_ap_reaction_row,0x0807c5e7
menu_row ffta_ap_support_row,0x0807c6a5

.align 2
.global ffta_ap_combo_row
.thumb_func
ffta_ap_combo_row:
    pop {r3}
    ldr r1,=0x524
    add r1,sp
    ldr r1,[r1]
    push {r3}
    ap_call ffta_ap_value,r3,r1
    strb r0,[r4,#14]
    ap_tail 0x0807c781
.ltorg

.align 2
.global ffta_ap_command_discovery
.thumb_func
ffta_ap_command_discovery:
    ap_call ffta_ap_value,r7,r4
    adds r3,r4,#1
    mov r8,r3
    ap_tail 0x080c8f83
.ltorg

.align 2
.global ffta_secondary_job_entry
.thumb_func
ffta_secondary_job_entry:
    movs r1,r0
    adds r1,#0x36
    ldrb r1,[r1]
    cmp r1,#116
    blo 1f
    cmp r1,#125
    bhi 1f
    push {r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl ffta_new_secondary_job
    mov sp,r4
    pop {r4}
    pop {r1}
    bx r1
1:
    push {r4-r7,lr}
    mov r7,r8
    push {r7}
    mov r8,r0
    ap_tail 0x080c9081
.ltorg

.align 2
.global ffta_lesson_job_entry
.thumb_func
ffta_lesson_job_entry:
    push {r0-r4,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl ffta_new_lesson_job
    mov sp,r4
    cmp r0,#0
    beq 1f
    ldr r4,[sp,#16]
    ldr r1,[sp,#20]
    add sp,#24
    bx r1
1:
    ldr r0,[sp,#20]
    mov lr,r0
    pop {r0-r4}
    add sp,#4
    push {r4-r7,lr}
    mov r7,r8
    push {r7}
    lsls r0,r0,#24
    ap_tail 0x080c94d9
.ltorg

@ Whole native runtime dispatch hooks retain every original argument/register.
.macro owner_call target, argument
    push {r0-r7,lr}
    movs r0,\argument
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    bl \target
    mov sp,r4
    ldr r0,[sp,#32]
    mov lr,r0
    pop {r0-r7}
    add sp,#4
.endm
.align 2
.global ffta_native_copy_entry
.thumb_func
ffta_native_copy_entry:
    owner_call ffta_on_unit_copy,r0
    ldr r3,=0x03005ee9
    bx r3
.ltorg

.align 2
.global ffta_native_free_entry
.thumb_func
ffta_native_free_entry:
    owner_call ffta_copy_owner_free,r1
    push {lr}
    subs r1,#12
    ldr r3,=0x08006fcd
    bl 1f
    pop {r0}
    bx r0
1:  bx r3
.ltorg

.align 2
.global ffta_snapshot_entry
.thumb_func
ffta_snapshot_entry:
    owner_call ffta_snapshot_register,r0
    push {r4-r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    ap_tail 0x0809de9d
.ltorg

.align 2
.global ffta_manager_entry
.thumb_func
ffta_manager_entry:
    push {lr}
    bl ffta_original_manager
    owner_call ffta_manager_register,r0
    pop {r1}
    bx r1
.thumb_func
ffta_original_manager:
    push {r4-r7,lr}
    sub sp,#4
    movs r5,r0
    movs r4,#128
    lsls r4,r4,#3
    ap_tail 0x0809700b
.ltorg

.align 2
.global ffta_selection_allocate
.thumb_func
ffta_selection_allocate:
    pop {r3}
    push {r1-r7,lr}
    ldr r0,=0x3828
    ldr r3,=0x08022841
    bl 1f
    owner_call ffta_selection_register,r0
    ldr r1,[sp,#28]
    mov lr,r1
    pop {r1-r7}
    add sp,#4
    movs r4,r0
    ldr r5,=0x0200f454
    ap_tail 0x08064f1f
1:  bx r3
.ltorg

.align 2
.global ffta_library_copy_entry
.thumb_func
ffta_library_copy_entry:
    owner_call ffta_on_unit_copy,r0
    push {r4-r5,lr}
    movs r5,r0
    movs r4,r5
    movs r3,r1
    ap_tail 0x08144405
.ltorg

.align 2
.global ffta_party_copy_entry
.thumb_func
ffta_party_copy_entry:
    push {lr}
    bl ffta_original_party_constructor
    owner_call ffta_party_copy_register,r0
    pop {r1}
    bx r1
.thumb_func
ffta_original_party_constructor:
    push {r4-r6,lr}
    sub sp,#8
    movs r6,r0
    cmp r6,#0
    ap_tail 0x080710a5
.ltorg

.align 2
.global ffta_ap_preview_row
.thumb_func
ffta_ap_preview_row:
    pop {r3}
    ldr r0,[r3]
    ldr r1,=0x1be4
    adds r0,r0,r1
    push {r3}
    ap_call ffta_ap_value,r0,r6
    ldr r1,=0x1c24
    ap_tail 0x0807c50f
.ltorg

.align 2
.global ffta_ap_primary_preview_row
.thumb_func
ffta_ap_primary_preview_row:
    pop {r3}
    ldr r0,=0x1be4
    adds r0,r1,r0
    push {r3}
    ap_call ffta_ap_value,r0,r6
    push {r0}
    ldr r0,=0x1c24
    adds r1,r1,r0
    pop {r0}
    ap_tail 0x0807c3d7
.ltorg

.align 2
.global ffta_prerequisite_count
.thumb_func
ffta_prerequisite_count:
    ap_call ffta_job_prerequisite_count,r10,r5
    movs r2,r0
    ap_tail 0x080c8b95
.ltorg

.align 2
.global ffta_ap_loss_filter
.thumb_func
ffta_ap_loss_filter:
    ap_call ffta_ap_value,r8,r2
    movs r1,r0
    movs r0,r7
    ands r0,r1
    cmp r0,#0
    beq 1f
    ap_tail 0x081291b9
1:  ap_tail 0x081291bf
.ltorg

.align 2
.global ffta_ap_loss_read
.thumb_func
ffta_ap_loss_read:
    ap_call ffta_ap_value,r8,r5
    mov r1,r8
    adds r1,#0x40
    movs r4,#0x7f
    ands r4,r0
    ap_tail 0x08129231
.ltorg

.align 2
.global ffta_ap_loss_write
.thumb_func
ffta_ap_loss_write:
    movs r2,r4
    ap_call ffta_ap_write_and_equipment_check,r8,r5
    ap_tail 0x08129271
.ltorg

read_mastery ffta_ap_theft_read,r8,0x08132e6f

.align 2
.global ffta_ap_theft_grant
.thumb_func
ffta_ap_theft_grant:
    pop {r3}
    ldr r0,[r6]
    movs r1,r4
    movs r2,#0xe4
    owner_call ffta_ap_set_value,r0
    movs r5,#0
    movs r1,#0xe4
    ap_tail 0x08132fd3
.ltorg

.align 2
.global ffta_ap_theft_revoke
.thumb_func
ffta_ap_theft_revoke:
    pop {r3}
    lsls r4,r0,#24
    lsrs r4,r4,#24
    ldr r0,[r6,#8]
    movs r2,r5
    push {r3}
    ap_call ffta_ap_write_and_equipment_check,r0,r4
    ap_tail 0x0813300f
.ltorg

.align 2
.global ffta_ap_theft_count
.thumb_func
ffta_ap_theft_count:
    ap_call ffta_ap_value,r6,r8
    movs r4,#0x7f
    ands r4,r0
    ap_tail 0x08133d3d
.ltorg

ability_entry ffta_battle_command_entry, ffta_battle_command
ability_entry ffta_special_action_entry, ffta_special_action
ability_entry ffta_action_command_entry, ffta_action_command
ability_entry ffta_action21_entry, ffta_action21

.align 2
.global ffta_original_battle_command
.thumb_func
ffta_original_battle_command:
    push {r4-r6,lr}
    sub sp,#4
    lsls r0,r0,#24
    lsrs r0,r0,#24
    ap_tail 0x08025fe5
.ltorg

.align 2
.global ffta_original_special_action
.thumb_func
ffta_original_special_action:
    push {r4-r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    ap_tail 0x08026ac1
.ltorg

.macro command_original name,continuation
.align 2
.global \name
.thumb_func
\name:
    push {r4-r7,lr}
    mov r7,r9
    mov r6,r8
    push {r6-r7}
    ap_tail \continuation
.ltorg
.endm
command_original ffta_original_action_command,0x08133d81
command_original ffta_original_action21,0x081341f5
