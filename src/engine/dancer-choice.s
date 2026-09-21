.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_dancer_choice_transport_entry
.thumb_func
ffta_dancer_choice_transport_entry:
 pop {r3}
 @ A447A..A4484 normally admits the supplied extra only for item actions.
 @ A dance uses that extra as a choice, without gaining item/debit semantics.
 ldr r0,=406
 cmp r4,r0
 beq .Lchoice
 ldr r0,=376
 cmp r4,r0
 beq .Lchoice
 ldr r0,=381
 cmp r4,r0
 beq .Lchoice
 ldr r0,=421
 cmp r4,r0
 beq .Lchoice
 adds r0,r4,#0
 movs r1,#27
 bl .Lnative_field
 cmp r0,#0
 bne .Lselected
 push {r0}
 ldr r0,=0x080a4487
 b .Lresume
.Lchoice:
 movs r0,#1
 movs r1,#27
.Lselected:
 push {r0}
 ldr r0,=0x080a448f
.Lresume:
 mov lr,r0
 pop {r0}
 bx lr
.Lnative_field:
 push {r3}
 ldr r3,=0x080ccd51
 mov ip,r3
 pop {r3}
 bx ip
.ltorg

.align 2
.global ffta_dancer_preview_choice_entry
.thumb_func
ffta_dancer_preview_choice_entry:
 pop {r3}
 push {r0-r5,lr}
 mov r4,sp
 mov r0,r9
 ldr r1,[r4,#16] @ original R4 action, before R4 became the saved SP
 movs r2,r6
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_dancer_preview_choice
 mov sp,r4
 str r0,[sp,#4]
 pop {r0-r5}
 add sp,#4
 movs r0,r4
 movs r2,#0
 bl .Lpreview_init
 ldr r4,=0x0200f390
 push {r0}
 ldr r0,=0x080b4cfd
 mov lr,r0
 pop {r0}
 bx lr
.Lpreview_init:
 push {r3}
 ldr r3,=0x0812f2a5
 mov ip,r3
 pop {r3}
 bx ip
.ltorg

.align 2
.global ffta_dancer_player_choice_entry
.thumb_func
ffta_dancer_player_choice_entry:
 pop {r3}
 ldr r4,[sp,#0x64]
 ldrh r0,[r4]
 push {r1}
 ldr r1,=406
 cmp r0,r1
 beq .Lplayer_pop
 ldr r1,=376
 cmp r0,r1
 beq .Lplayer_pop
 ldr r1,=381
 cmp r0,r1
 beq .Lplayer_pop
 ldr r1,=421
 cmp r0,r1
.Lplayer_pop:
 pop {r1}
 beq .Lplayer_choice
 movs r1,#27
 bl .Lnative_field
 cmp r0,#0
 bne .Lplayer_copy
 push {r0}
 ldr r0,=0x08094351
 b .Lplayer_resume
.Lplayer_choice:
 movs r0,#1
 movs r1,#27
.Lplayer_copy:
 push {r0}
 ldr r0,=0x0809435b
.Lplayer_resume:
 mov lr,r0
 pop {r0}
 bx lr
.ltorg

.align 2
.global ffta_dancer_chance_choice_entry
.thumb_func
ffta_dancer_chance_choice_entry:
 pop {r3}
 add r0,sp,#0x10
 ldrh r1,[r0]
 push {r0-r5,lr}
 mov r4,sp
 movs r0,r6
 movs r2,r1
 movs r1,r7
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_dancer_preview_choice
 mov sp,r4
 str r0,[sp,#4]
 pop {r0-r5}
 add sp,#4
 movs r0,r7
 movs r2,#0
 bl .Lpreview_init
 push {r0}
 ldr r0,=0x0812dbd7
 mov lr,r0
 pop {r0}
 bx lr
.ltorg

.align 2
.global ffta_dancer_magnitude_choice_entry
.thumb_func
ffta_dancer_magnitude_choice_entry:
 pop {r3}
 push {r0-r5,lr}
 mov r4,sp
 movs r0,r6
 movs r1,r2
 movs r2,r7
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_dancer_preview_choice
 mov sp,r4
 str r0,[sp,#4]
 pop {r0-r5}
 add sp,#4
 movs r0,r2
 movs r2,#0
 bl .Lpreview_init
 str r6,[r4]
 push {r0}
 ldr r0,=0x08130269
 mov lr,r0
 pop {r0}
 bx lr
.ltorg
