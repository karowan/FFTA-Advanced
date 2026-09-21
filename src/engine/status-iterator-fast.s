.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_art_status_next_entry
.thumb_func
@ Backport of integrated-jobs.c's unconditional native-key advance to the
@ authenticated existing art parent. The native entry has already pushed r3.
@ The slow path delegates to the intact original entry and all its lookups.
ffta_art_status_next_entry:
    ldrb r3,[r4,#2]
    adds r3,#1
    lsls r3,r3,#24
    asrs r3,r3,#24
    cmp r3,#24
    bgt 1f
    strb r3,[r4,#2]
    pop {r3}
    ldr r0,=0x0809dd63
    bx r0
1:
    ldr r3,=ffta_art_original_status_next_entry
    bx r3
.ltorg
