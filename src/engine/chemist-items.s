.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.macro callback name,fn
.align 2
.global \name
.thumb_func
\name:
 push {r4-r5,lr}
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl \fn
 mov sp,r4
 pop {r4-r5}
 pop {r1}
 bx r1
.endm
callback ffta_chemist_eligibility_entry,ffta_chemist_eligibility
callback ffta_chemist_hp_entry,ffta_chemist_hp
callback ffta_chemist_mp_entry,ffta_chemist_mp
callback ffta_chemist_revive_entry,ffta_chemist_revive
.align 2
.global ffta_chemist_consumption_entry
.thumb_func
ffta_chemist_consumption_entry:
 pop {r3}
 lsls r0,r0,#24
 cmp r0,#0
 beq 1f
 ldrh r0,[r4,#0x12]
 movs r1,#1
 mov r2,r9
 bl ffta_chemist_consumption_aligned
1:
 push {r0}
 ldr r0,=0x080a2eeb
 mov lr,r0
 pop {r0}
 bx lr
.ltorg
.align 2
.global ffta_chemist_range_entry
.thumb_func
ffta_chemist_range_entry:
 pop {r3}
 push {r0-r7,lr}
 mov r7,r12
 push {r7}
 mov r4,sp
 ldr r0,[r4,#0x34]
 ldr r1,[r4,#32]
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_chemist_range
 mov sp,r4
 str r0,[sp,#32]
 pop {r7}
 mov r12,r7
 pop {r0-r7}
 add sp,#4
 ldr r3,=0x0000ff3f
 movs r0,r3
 ands r7,r0
 push {r1}
 ldr r1,=0x080a014b
 mov lr,r1
 pop {r1}
 bx lr
.ltorg
callback ffta_chemist_consumption_aligned,ffta_chemist_consumption
.align 2
.global ffta_chemist_context_entry
.thumb_func
ffta_chemist_context_entry:
 pop {r3}
 b ffta_chemist_context_aligned
callback ffta_chemist_context_aligned,ffta_chemist_context
.align 2
.global ffta_original_chemist_context
.thumb_func
ffta_original_chemist_context:
 push {r4-r7,lr}
 sub sp,#4
 adds r5,r0,#0
 adds r4,r3,#0
 lsls r1,r1,#16
 lsrs r6,r1,#16
 push {r0}
 ldr r0,=0x0812f23d
 mov lr,r0
 pop {r0}
 bx lr
.ltorg
callback ffta_chemist_inoculation_entry,ffta_chemist_inoculation
callback ffta_chemist_beneficial_entry,ffta_chemist_beneficial
callback ffta_chemist_snapshot_flags_entry,ffta_chemist_snapshot_flags

callback ffta_chemist_hp_loss_entry,ffta_chemist_hp_loss
callback ffta_chemist_reaction_queue_entry,ffta_chemist_reaction_queue
callback ffta_chemist_inert_entry,ffta_chemist_inert_presentation

.align 2
.global ffta_chemist_native_item_debit_entry
.thumb_func
ffta_chemist_native_item_debit_entry:
 pop {r3}
 lsrs r0,r0,#16
 cmp r0,#0
 beq 1f
 movs r1,#1
 mov r2,r9
 bl ffta_chemist_consumption_aligned
1:
 push {r0}
 ldr r0,=0x080a2ec5
 mov lr,r0
 pop {r0}
 bx lr
.ltorg
