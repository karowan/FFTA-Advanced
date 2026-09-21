.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_passing_begin_entry
.thumb_func
ffta_passing_begin_entry:
 pop {r3}
 mov r0,r8
 b ffta_passing_begin
.global ffta_passing_original_confirm
.thumb_func
ffta_passing_original_confirm:
 push {lr}
 sub sp,#32
 ldr r1,=0x0200f438
 ldr r0,[r1]
 movs r3,#0
 strb r3,[r0,#3]
 ldr r2,=0x0802572d
 bx r2
.align 2
.global ffta_passing_poll_entry
.thumb_func
ffta_passing_poll_entry:
 pop {r3}
 mov r0,r8
 ldr r1,[sp,#0x28]
 ldr r2,[sp,#0x2c]
 bl ffta_passing_poll
 lsls r0,r0,#16
 asrs r1,r0,#16
 movs r0,#1
 rsbs r0,r0,#0
 ldr r3,=0x080b6551
 bx r3
.align 2
.global ffta_passing_after_entry
.thumb_func
ffta_passing_after_entry:
 pop {r3}
 push {r0-r3}
 bl ffta_passing_after_action
 cmp r0,#0
 pop {r0-r3}
 bne passing_tick_end
 mov r3,r9
 ldr r0,[r3]
 movs r1,#0x40
 orrs r0,r1
 str r0,[r3]
 mov r4,r8
 ldr r3,=0x08093c6b
 bx r3
passing_tick_end:
 ldr r3,=0x08096b15
 bx r3
.align 2
.global ffta_passing_ai_entry
.thumb_func
ffta_passing_ai_entry:
 pop {r3}
 push {r0-r3}
 bl ffta_passing_ai_prepare
 cmp r0,#0
 pop {r0-r3}
 bne passing_tick_end
 movs r0,#3
 movs r1,#1
 bl passing_native_flag
 bl passing_native_selected
 push {r0}
 ldr r0,=0x080939a1
 mov lr,r0
 pop {r0}
 bx lr
passing_native_flag:
 ldr r3,=0x080c9575
 bx r3
passing_native_selected:
 ldr r3,=0x080c1515
 bx r3
.ltorg
