.syntax unified
.cpu arm7tdmi
.thumb
.text
.macro save_call name
 push {r1-r7,lr}
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl \name
 mov sp,r4
 pop {r1-r7}
 pop {r3}
 mov lr,r3
.endm
.macro tail address
 push {r0}
 ldr r0,=\address
 mov ip,r0
 pop {r0}
 bx ip
.endm
.align 2
.global ffta_dancer_attack_entry
.thumb_func
ffta_dancer_attack_entry:
 pop {r3}
 save_call ffta_dancer_attack
 lsls r0,r0,#16
 asrs r0,r0,#16
 add sp,#4
 pop {r3,r4}
 tail 0x0812fdd1
.ltorg
.align 2
.global ffta_dancer_power_entry
.thumb_func
ffta_dancer_power_entry:
 /* This call site has another native branch entering its final MUL.
  * The compact hook leaves that instruction intact; R3 is scratch here. */
 mov r0,r8
 mov r1,r9
 movs r2,#10
 mov r3,r10
 save_call ffta_dancer_power
 tail 0x0812ff6f
.ltorg

.align 2
.global ffta_dancer_coefficient_entry
.thumb_func
ffta_dancer_coefficient_entry:
 mov r0,r10
 mov r1,r8
 mov r2,r9
 save_call ffta_dancer_coefficient
 tail 0x0812ff6f
.ltorg
