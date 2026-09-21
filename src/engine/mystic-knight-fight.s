.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_myk_fight_element_hook
.thumb_func
ffta_myk_fight_element_hook:
 pop {r3}
 cmp r1,#0
 beq .Lcustom_element
 ldr r3,=360
 cmp r1,r3
 bne .Lordinary
.Lcustom_element:
 push {r0-r5,lr}
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_myk_fight_element
 mov sp,r4
 cmp r0,#0
 blt .Lfallback
 str r0,[sp]
 pop {r0-r5}
 pop {r3}
 bx r3
.Lfallback:
 pop {r0-r5}
 pop {r3}
 mov lr,r3
.Lordinary:
 push {r3}
 ldr r3,=ffta_dancer_element_entry
 bx r3
.ltorg

@ Preserve the native caller and r4 loop index before the shared preview
@ wrapper opens its read-only snapshot. All paths restore the prior scope.
.align 2
.global ffta_myk_fight_preview_hook
.thumb_func
ffta_myk_fight_preview_hook:
 pop {r3}
 push {r4-r7,lr}
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 sub sp,#8
 str r4,[sp]
 bl ffta_myk_fight_preview
 mov sp,r4
 pop {r4-r7}
 pop {r1}
 bx r1
.ltorg

@ Preserve the existing custom-technique exclusions on every fallback.
.macro weapon_wrapper name, fallback
.align 2
.global \name
.thumb_func
\name:
 pop {r3}
 push {r0-r5,lr}
 mov r1,lr
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_myk_fight_replace_weapon
 mov sp,r4
 cmp r0,#0
 beq 1f
 movs r0,#0
 str r0,[sp]
 pop {r0-r5}
 pop {r3}
 bx r3
1:
 pop {r0-r5}
 pop {r3}
 mov lr,r3
 push {r3}
 ldr r3,=\fallback
 bx r3
.ltorg
.endm
weapon_wrapper ffta_myk_fight_drain_hook,ffta_integrated_weapon_drain_entry
weapon_wrapper ffta_myk_fight_effect_hook,ffta_integrated_weapon_effect_entry

.align 2
.global ffta_myk_fight_status_hook
.thumb_func
ffta_myk_fight_status_hook:
 pop {r3}
 push {r0-r7,lr}
 mov r4,sp
 adds r4,#36
 ldr r2,=0x33c
 ldr r1,[r4,r2]
 adds r1,r1,r5
 ldr r1,[r1]
 ldr r1,[r1]
 mov r0,r9
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_myk_fight_status
 mov sp,r4
 pop {r0-r7}
 pop {r3}
 mov lr,r3
 @ Original Fight cleanup tail, after native wake-on-damage and effect3E.
 ldr r2,[sp,#0x33c]
 adds r0,r2,r5
 ldr r0,[r0]
 ldr r0,[r0]
 ldr r3,=0x08131c59
 bl .Lnative_refresh
 ldr r3,=0x080a2dd9
 bx r3
.Lnative_refresh:
 bx r3
.ltorg
