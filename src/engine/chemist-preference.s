.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_potion_roster_entry
.thumb_func
ffta_potion_roster_entry:
 pop {r3}
 push {r4,lr}
 mov r4,sp
 mov r3,sp
 lsrs r3,r3,#3
 lsls r3,r3,#3
 mov sp,r3
 bl ffta_potion_roster
 mov sp,r4
 pop {r4}
 pop {r1}
 bx r1
.align 2
.global ffta_original_potion_roster
.thumb_func
ffta_original_potion_roster:
 push {r4-r7,lr}
 mov r7,r10
 mov r6,r9
 mov r5,r8
 push {r5-r7}
 sub sp,#0x104
 push {r3}
 ldr r3,=0x0807d979
 mov ip,r3
 pop {r3}
 bx ip
.ltorg
.align 2
.global ffta_potion_confirm_entry
.thumb_func
ffta_potion_confirm_entry:
 pop {r3}
 push {r0-r7,lr}
 movs r0,r1
 mov r4,sp
 mov r3,sp
 lsrs r3,r3,#3
 lsls r3,r3,#3
 mov sp,r3
 bl ffta_potion_confirm
 mov sp,r4
 pop {r0-r7}
 pop {r3}
 mov lr,r3
 ldr r3,=0x0807e04d
 bx r3
.ltorg
