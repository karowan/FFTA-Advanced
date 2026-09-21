.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.macro wrap name,fn
.align 2
.global \name
.thumb_func
\name:
 pop {r3}
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
wrap ffta_chemist_menu_entry,ffta_chemist_menu
wrap ffta_chemist_restricted_menu_entry,ffta_chemist_restricted_menu
wrap ffta_chemist_menu_name_entry,ffta_chemist_menu_name
.macro original name,amount,target
.align 2
.global \name
.thumb_func
\name:
 push {r4-r7,lr}
 mov r7,r10
 mov r6,r9
 mov r5,r8
 push {r5-r7}
 sub sp,#\amount
 push {r0}
 ldr r0,=\target
 mov lr,r0
 pop {r0}
 bx lr
.ltorg
.endm
original ffta_original_chemist_menu,8,0x08026d51
original ffta_original_chemist_restricted_menu,4,0x08026fa9
.align 2
.global ffta_original_chemist_menu_name
.thumb_func
ffta_original_chemist_menu_name:
 push {r4-r5,lr}
 adds r5,r0,#0
 lsls r1,r1,#16
 lsrs r3,r1,#16
 ldr r1,=0x0200f438
 ldr r0,[r1]
 push {r2}
 ldr r2,=0x08025765
 mov lr,r2
 pop {r2}
 bx lr
.ltorg
.align 2
.global ffta_chemist_menu_selected_entry
.thumb_func
ffta_chemist_menu_selected_entry:
 pop {r3}
 push {r0-r7,lr}
 mov r7,r12
 push {r7}
 mov r4,sp
 ldr r0,[r4,#20] @ saved R4 menu
 ldr r1,[r4,#28] @ saved R6 row
 ldr r2,[r4,#12] @ saved R2 lesson record
 ldrh r2,[r2,#4]
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_chemist_menu_selected
 mov sp,r4
 str r0,[sp,#4]
 pop {r7}
 mov r12,r7
 pop {r0-r7}
 add sp,#4
 str r0,[r3,#0x14]
 cmp r5,#15
 beq 1f
 push {r1}
 ldr r1,=0x08028ad1
 b 2f
1: push {r1}
 ldr r1,=0x08028acf
2: mov lr,r1
 pop {r1}
 bx lr
.ltorg
