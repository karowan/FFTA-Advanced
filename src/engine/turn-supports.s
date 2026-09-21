.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_turn_flag_entry
.thumb_func
ffta_turn_flag_entry:
 pop {r3}
 mov r2,lr
 b ffta_turn_flag
.global ffta_original_turn_flag
.thumb_func
ffta_original_turn_flag:
 push {lr}
 lsls r0,r0,#16
 lsls r1,r1,#16
 lsrs r3,r0,#19
 ldr r2,=0x02001f70
 adds r3,r3,r2
 ldr r2,=0x080c9581
 bx r2
.ltorg
