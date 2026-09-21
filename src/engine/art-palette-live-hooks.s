.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.align 2
.global ffta_art_native_copy_entry
.thumb_func
ffta_art_native_copy_entry:
    cmp r2,#0
    beq 2f
    ldr r3,=0x03003c60
    cmp r0,r3
    bhs 2f
    adds r3,r0,r2
    cmp r3,r0
    blo 2f
    push {r4}
    ldr r4,=0x03003a60
    cmp r3,r4
    pop {r4}
    bls 2f
    ldr r3,=ffta_art_live_palette_copy
    bx r3
2:
    ldr r3,=ffta_art_original_native_copy
    bx r3
.ltorg
.align 2
.global ffta_art_original_begin
.thumb_func
ffta_art_original_begin:
    push {r7,lr}
    mov r7,sp
    ldr r0,=0x03002bbc
    movs r1,#128
    ldr r3,=0x080006d9
    bx r3
.ltorg

.thumb
.align 2
.global ffta_art_original_end
.thumb_func
ffta_art_original_end:
    push {r7,lr}
    mov r7,sp
    ldr r0,=0x04000004
    ldr r1,=0x03000ea0
    ldr r3,=0x08000791
    bx r3
.ltorg
.align 2
.global ffta_art_original_reset
.thumb_func
ffta_art_original_reset:
    push {r4,r5,r6,lr}
    ldr r5,=0x0836d4b8
    ldr r4,=0x03000028
    ldrb r0,[r4]
    ldr r3,=0x0800119d
    bx r3
.ltorg
.macro original name, continuation
.align 2
.global \name
.thumb_func
\name:
    push {r4,r5,r6,r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    ldr r3,=\continuation
    bx r3
.ltorg
.endm
original ffta_art_original_compose,0x080012c5
original ffta_art_original_render,0x08021701
original ffta_art_original_battle_render,0x0808f1fd

@ Called only after the existing three exact native heap-start comparisons.
@ Preserve old endpoint recognition and add this build's palette heap limit.
.align 2
.global ffta_art_clear_endpoint
.thumb_func
ffta_art_clear_endpoint:
    ldr r2,=ffta_art_live_base
    cmp r7,r2
    beq 1f
    ldr r3,=0xfffffbff
    ldr r2,=0x0203f000
    ands r3,r7
    cmp r3,r2
    bne 2f
1:
    push {r0,r1,r2,lr}
    bl ffta_art_heap_reset
    pop {r0,r1,r2,r3}
    mov lr,r3
    movs r2,#0
    cmp r2,#0
2:
    ldr r3,=ffta_art_clear_continue
    bx r3
.ltorg

@ Four-argument entries and the callback's task register require r3 intact.
.align 2
.global ffta_art_original_fade_cancel
.thumb_func
ffta_art_original_fade_cancel:
    push {r4,r5,r6,r7,lr}
    lsls r0,r0,#16
    lsrs r6,r0,#16
    lsls r1,r1,#16
    ldr r3,=0x08146dd1
    bx r3
.ltorg
.align 2
.global ffta_art_original_fade_rotate
.thumb_func
ffta_art_original_fade_rotate:
    push {r4,r5,r6,r7,lr}
    mov r7,sl
    mov r6,sb
    mov r5,r8
    ldr r3,=0x0814686d
    bx r3
.ltorg
.align 2
.macro object_effect_entry name
.align 2
.global ffta_art_live_fade_\name\()_entry
.thumb_func
ffta_art_live_fade_\name\()_entry:
    @ Native callbacks take onlyr0. Background-only cycles cannot affect an
    @ OBJ binding; avoid all C bookkeeping on this frequent native path.
    ldrh r1,[r0,#8]
    movs r2,#128
    lsls r2,r2,#1
    cmp r1,r2
    blo 1f
    lsls r2,r2,#1
    ldrh r1,[r0,#6]
    cmp r1,r2
    bhs 1f
    ldr r3,=ffta_art_live_fade_\name
    bx r3
1:
    ldr r3,=ffta_art_original_fade_\name
    bx r3
.ltorg
.endm
object_effect_entry rotate
object_effect_entry cycle
.align 2
.global ffta_art_original_fade_cycle
.thumb_func
ffta_art_original_fade_cycle:
    push {r4,r5,r6,r7,lr}
    adds r4,r0,#0
    adds r3,r4,#0
    adds r3,#12
    push {r2}
    ldr r2,=0x08146bb9
    mov ip,r2
    pop {r2}
    bx ip
.ltorg
.align 2
.global ffta_art_original_fade_delete
.thumb_func
ffta_art_original_fade_delete:
    push {lr}
    @ Displaced148738 is an authenticated identity (BX LR), not a selector.
    adds r1,r0,#0
    ldr r3,=0x081484a1
    bx r3
.ltorg
.align 2
.global ffta_art_original_fade_collect
.thumb_func
ffta_art_original_fade_collect:
    push {r4,lr}
    adds r4,r0,#0
    cmp r4,#0
    beq 1f
    ldr r3,=0x081484d5
    bx r3
1:
    ldr r3,=0x08148511
    bx r3
.ltorg
.align 2
.global ffta_art_original_fade_delete_all
.thumb_func
ffta_art_original_fade_delete_all:
    push {r4,lr}
    ldr r0,=0x03003c60
    ldr r4,[r0,#4]
    cmp r4,#0
    ldr r3,=0x08148549
    bx r3
.ltorg
.macro preserve_continue address
    push {r3}
    ldr r3,=\address
    mov ip,r3
    pop {r3}
    bx ip
.endm
.align 2
.global ffta_art_original_fade_setup
.thumb_func
ffta_art_original_fade_setup:
    push {r4,r5,r6,r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    push {r5,r6,r7}
    sub sp,#24
    lsls r0,r0,#16
    lsrs r0,r0,#16
    preserve_continue 0x08146e65
.ltorg
.macro fade_solid name,address
.align 2
.global \name
.thumb_func
\name:
    push {r4,r5,r6,lr}
    lsls r0,r0,#16
    lsrs r4,r0,#16
    lsls r1,r1,#16
    preserve_continue \address
.ltorg
.endm
fade_solid ffta_art_original_fade_black,0x08147a85
fade_solid ffta_art_original_fade_white,0x08147ad9
.macro transform_four name,address,destination
.align 2
.global \name
.thumb_func
\name:
    push {r4,r5,r6,r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    push {r5,r6,r7}
    sub sp,#4
    lsls r0,r0,#16
    lsrs \destination,r0,#16
    preserve_continue \address
.ltorg
.endm
transform_four ffta_art_original_fade_brighten,0x08147ed9,r7
transform_four ffta_art_original_fade_darken,0x08147f61,r7
transform_four ffta_art_original_fade_exposure,0x0814732d,r0
.align 2
.global ffta_art_original_fade_blend
.thumb_func
ffta_art_original_fade_blend:
    push {r4,r5,r6,r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    push {r5,r6,r7}
    sub sp,#4
    ldr r4,[sp,#36]
    ldr r5,[sp,#40]
    preserve_continue 0x08147da5
.ltorg
.align 2
.global ffta_art_original_fade_exposure_rgb
.thumb_func
ffta_art_original_fade_exposure_rgb:
    push {r4,r5,r6,r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    push {r5,r6,r7}
    sub sp,#12
    ldr r4,[sp,#44]
    ldr r5,[sp,#48]
    preserve_continue 0x081473f5
.ltorg
original ffta_art_original_fade_gray,0x08147b31
.macro table_transform name,localbytes,argument,continuation
.align 2
.global \name
.thumb_func
\name:
    push {r4,r5,r6,r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    push {r5,r6,r7}
    sub sp,#\localbytes
    str r3,[sp,#4]
    ldr r3,[sp,#\argument]
    preserve_continue \continuation
.ltorg
.endm
table_transform ffta_art_original_fade_table_exposure,12,44,0x081474cd
table_transform ffta_art_original_fade_table_blend,8,40,0x08147e39
original ffta_art_original_fade_tint,0x08147bad
.align 2
.global ffta_art_original_fade_rgb
.thumb_func
ffta_art_original_fade_rgb:
    push {r4,r5,r6,r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    push {r5,r6,r7}
    sub sp,#4
    ldr r4,[sp,#36]
    ldr r5,[sp,#40]
    preserve_continue 0x08147c3d
.ltorg
.align 2
.global ffta_art_original_fade_solid
.thumb_func
ffta_art_original_fade_solid:
    push {r4,r5,r6,r7,lr}
    ldr r4,[sp,#20]
    ldr r5,[sp,#24]
    lsls r0,r0,#16
    lsrs r6,r0,#16
    lsls r1,r1,#16
    lsrs r1,r1,#16
    lsls r2,r2,#16
    preserve_continue 0x08147cd1
.ltorg
.align 2
.global ffta_art_original_fade_table
.thumb_func
ffta_art_original_fade_table:
    push {r4,r5,r6,r7,lr}
    adds r7,r3,#0
    lsls r0,r0,#16
    lsrs r5,r0,#16
    lsls r1,r1,#16
    lsrs r1,r1,#16
    lsls r2,r2,#16
    lsrs r2,r2,#16
    preserve_continue 0x08147d3d
.ltorg
.align 2
.global ffta_art_original_fade_tick
.thumb_func
ffta_art_original_fade_tick:
    push {lr}
    adds r3,r0,#0
    ldrh r1,[r3,#2]
    movs r0,#32
    preserve_continue 0x08148749
.ltorg
