.syntax unified
.cpu arm7tdmi
.thumb
.text
.macro save
 push {r0-r7,lr}
 mov r4,sp
 mov r3,sp
 lsrs r3,r3,#3
 lsls r3,r3,#3
 mov sp,r3
.endm
.macro restore result=0
 mov sp,r4
 .if \result
 str r0,[sp]
 .endif
 ldr r0,[sp,#32]
 mov lr,r0
 pop {r0-r7}
 add sp,#4
.endm
.macro tail target
 push {r0}
 ldr r0,=\target
 mov ip,r0
 pop {r0}
 bx ip
.endm
.align 2
.global ffta_preview_party_init
.thumb_func
ffta_preview_party_init:
 save
 lsrs r0,r6,#16
 movs r1,#0
 movs r2,#0
 bl ffta_preview_draw
 restore
 tail 0x0808e53d
.ltorg
.align 2
.global ffta_preview_shop_init
.thumb_func
ffta_preview_shop_init:
 pop {r3}
 save
 ldr r0,=0x0200f428
 ldr r0,[r0]
 ldr r1,=0x44ec
 ldrh r0,[r0,r1]
 movs r1,#1
 movs r2,#0
 bl ffta_preview_draw
 restore
 ldr r7,=0x0200f428
 tail 0x0806af3f
.ltorg
.macro turn name,shop,target
.align 2
.global \name
.thumb_func
\name:
 save
 movs r0,#\shop
 bl ffta_preview_turn
 restore 1
 tail \target
.ltorg
.endm
turn ffta_preview_party_input,0,0x0808e581
turn ffta_preview_shop_input,1,0x0806afc1
turn ffta_preview_sell_input,1,0x0806d03d
.align 2
.global ffta_preview_sell_init
.thumb_func
ffta_preview_sell_init:
 pop {r3}
 save
 ldr r0,=0x0200f428
 ldr r0,[r0]
 ldr r1,=0x44ec
 ldrh r0,[r0,r1]
 movs r1,#1
 movs r2,#0
 bl ffta_preview_draw
 restore
 ldr r7,=0x0200f428
 tail 0x0806cfbb
.ltorg
