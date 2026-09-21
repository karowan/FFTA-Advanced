.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_workspace_manager_entry
.thumb_func
ffta_workspace_manager_entry:
 push {r4-r5,lr}
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_workspace_native_manager
 movs r5,r0
 bl ffta_battle_workspace_register
 movs r0,r5
 mov sp,r4
 pop {r4-r5}
 pop {r1}
 bx r1
.thumb_func
ffta_workspace_native_manager:
 push {r4-r7,lr}
 sub sp,#4
 movs r5,r0
 ldr r4,=0x440
 ldr r3,=0x0809700b
 bx r3
.ltorg
.align 2
.global ffta_workspace_parent_capacity
.thumb_func
ffta_workspace_parent_capacity:
 ldr r0,=0x4c0
 adds r4,r4,r0
 movs r0,r4
 ldr r3,=0x08096efd
 bx r3
.ltorg
