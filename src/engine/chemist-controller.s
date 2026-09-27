.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_cp_battle_tick_entry
.thumb_func
ffta_cp_battle_tick_entry:
 push {r4-r5,lr}
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_cp_battle_tick
 mov sp,r4
 pop {r4-r5}
 pop {r1}
 bx r1
.align 2
.global ffta_cp_original_battle_tick
.thumb_func
ffta_cp_original_battle_tick:
 @ Exact overwritten native92784..92793 prologue. No PC-relative operand.
 push {r4-r7,lr}
 mov r7,r10
 mov r6,r9
 mov r5,r8
 push {r5-r7}
 sub sp,#0x90
 lsls r1,r1,#16
 lsrs r1,r1,#16
 ldr r3,=0x08092795
 bx r3
.ltorg
