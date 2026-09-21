.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_reviewed_menu_init_entry
.thumb_func
ffta_reviewed_menu_init_entry:
    push {r4,r5,r6,lr}
    mov r6,r8
    push {r6}
    bl ffta_reviewed_menu_reset
    ldr r0,=ffta_reviewed_menu_palette_table
    ldr r3,=0x08089669
    bx r3
.ltorg

.macro track destination
    push {r0-r4,lr}
    movs r3,r0
    movs r0,r2
    movs r1,\destination
    movs r2,r3
    bl ffta_reviewed_menu_upload
    pop {r0-r4}
    pop {r3}
.endm
.align 2
.global ffta_reviewed_menu_upload_a_entry
.thumb_func
ffta_reviewed_menu_upload_a_entry:
    track r4
    movs r3,#1
    push {r4,lr}
    ldr r4,=0x08005319
    bl .Ldecode_r4
    pop {r4}
    pop {r3}
    mov r0,r9
    adds r1,r4,#0
    movs r2,#0xa0
    ldr r3,=0x08087b9d
    bx r3
.Ldecode_r4:
    bx r4
.ltorg

.align 2
.global ffta_reviewed_menu_upload_b_entry
.thumb_func
ffta_reviewed_menu_upload_b_entry:
    track r4
    mov r1,r9
    movs r3,#1
    push {r4,lr}
    ldr r4,=0x08005319
    bl .Ldecode_r4
    pop {r4}
    pop {r3}
    movs r2,#0xa0
    lsls r2,r2,#1
    ldr r3,=0x08087c35
    bx r3
.ltorg

.align 2
.global ffta_reviewed_menu_upload_c_entry
.thumb_func
ffta_reviewed_menu_upload_c_entry:
    track r5
    ldr r1,=0x02003cb0
    movs r3,#1
    push {r4,lr}
    ldr r4,=0x08005319
    bl .Ldecode_r4
    pop {r4}
    pop {r3}
    ldr r0,=0x02003cb0
    adds r1,r5,#0
    ldr r3,=0x08087d65
    bx r3
.ltorg

.align 2
.global ffta_reviewed_menu_draw_entry
.thumb_func
ffta_reviewed_menu_draw_entry:
    adds r0,r5,#0
    adds r1,r6,#0
    bl ffta_reviewed_menu_draw
    ldrb r0,[r5,#15]
    ldr r3,=0x08088069
    bx r3
.ltorg
