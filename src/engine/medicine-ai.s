.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_medicine_recipient_entry
.thumb_func
ffta_medicine_recipient_entry:
 pop {r3}
 @ Every ordinary action retains the native stack depth. This gate is hot in
 @ the native planner, whose stack borders resident IWRAM renderer code.
 movs r3,#192
 lsls r3,r3,#1
 cmp r2,r3
 beq .Lmedicine_recipient
 b ffta_medicine_original_recipient
.Lmedicine_recipient:
 push {r4,r5,lr}
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_medicine_ai_recipient
 mov sp,r4
 pop {r4,r5}
 pop {r1}
 bx r1
.align 2
.global ffta_medicine_original_recipient
.thumb_func
ffta_medicine_original_recipient:
 push {r4-r7,lr}
 mov r7,r8
 push {r7}
 sub sp,#4
 adds r5,r0,#0
 adds r7,r1,#0
 ldr r3,=0x080c48b1
 bx r3
.ltorg
