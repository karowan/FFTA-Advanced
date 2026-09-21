.syntax unified
.cpu arm7tdmi
.thumb
.macro reserve_heap name, continuation
.align 2
.global \name
.thumb_func
\name:
    ldr r4,=0x0203f800
    subs r4,r4,r5
    ldr r0,=0x0836d4b8
    push {r0}
    ldr r0,=\continuation
    mov lr,r0
    pop {r0}
    bx lr
.ltorg
.endm
@ The compatibility view and AP owner roots reserve 2KiB globally. Party
@ scratch uses its smaller native heap context; the shop owns a list tail.
reserve_heap ffta_battle_heap_limit,0x08022805
reserve_heap ffta_results_heap_limit,0x0804ca1d
reserve_heap ffta_global_heap_limit,0x0813c081

@ These entries restore r3 saved by the twelve-byte installed long jump.
@ Keep the selected item ID at native context+44EC when its list moves.
.align 2
.global ffta_shop_selected_setup
.thumb_func
ffta_shop_selected_setup:
    pop {r3}
    ldr r4,=0x9c08
    adds r1,r1,r4
    ldrh r2,[r1]
    ldr r4,=0x44ec
    adds r1,r3,r4
    strh r2,[r1]
    push {r0}
    ldr r0,=0x0806e1b5
    mov lr,r0
    pop {r0}
    bx lr
.ltorg
.align 2
.global ffta_shop_selected_refresh
.thumb_func
ffta_shop_selected_refresh:
    pop {r3}
    ldr r3,=0x9c08
    adds r1,r1,r3
    ldrh r2,[r1]
    ldr r3,=0x44ec
    adds r1,r0,r3
    strh r2,[r1]
    push {r0}
    ldr r0,=0x0806d469
    mov lr,r0
    pop {r0}
    bx lr
.ltorg

@ Native initialization shares one byte index for saved scroll and cursor.
@ Preserve its final registers while clearing six u16 scrolls and six byte rows.
.macro reset_shop_positions name, continuation
.align 2
.global \name
.thumb_func
\name:
    pop {r3}
    push {r6}
    ldr r5,=0xa33c
    ldr r3,=0x44f7
    movs r1,#0
    movs r2,#0
1:
    ldr r0,[r4]
    adds r0,r0,r5
    lsls r6,r1,#1
    strh r2,[r0,r6]
    ldr r0,[r4]
    adds r0,r0,r3
    adds r0,r0,r1
    strb r2,[r0]
    adds r0,r1,#1
    movs r1,r0
    cmp r1,#5
    bls 1b
    pop {r6}
    push {r0}
    ldr r0,=\continuation
    mov lr,r0
    pop {r0}
    bx lr
.ltorg
.endm
reset_shop_positions ffta_shop_buy_positions_reset,0x08069b19
reset_shop_positions ffta_shop_sell_positions_reset,0x0806bb83
.align 2
.global ffta_shop_buy_entry
.thumb_func
ffta_shop_buy_entry:
    @ The native fourth argument is the town. Restore it after the long jump.
    pop {r3}
    push {r4-r6,lr}
    mov r4,sp
    mov r5,sp
    lsrs r5,r5,#3
    lsls r5,r5,#3
    mov sp,r5
    bl ffta_shop_buy_list
    mov sp,r4
    pop {r4-r6}
    pop {r1}
    bx r1
.text
.align 2

/* r0=quantity, r4=record index, r5=CB210 slice. The original code leaves
 * r4 pointing at the record for its continuation. */
.global ffta_sell_commit
.thumb_func
ffta_sell_commit:
    lsls r4,r4,#16
    lsrs r4,r4,#14
    adds r4,r4,r5
    movs r1,r0
    ldrh r0,[r4]
    push {r2-r3,lr}
    sub sp,#4
    bl ffta_native_lose_item
    add sp,#4
    pop {r2-r3}
    pop {r3}
    mov lr,r3
    ldr r3,=0x0806c94f
    bx r3

/* Feeding uses the same native record transaction with r6 as slice base. */
.align 2
.global ffta_feed_commit
.thumb_func
ffta_feed_commit:
    lsls r4,r4,#16
    lsrs r4,r4,#14
    adds r4,r4,r6
    movs r1,r0
    ldrh r0,[r4]
    push {r2-r3,lr}
    sub sp,#4
    bl ffta_native_lose_item
    add sp,#4
    pop {r2-r3}
    pop {r3}
    mov lr,r3
    ldr r3,=0x0805b87f
    bx r3

/* Enter only the equipment arm of the native typed reward dispatcher.
 * Mission item and recruit capacity checks keep their original paths. */
.align 2
.global ffta_reward_equipment_cap
.thumb_func
ffta_reward_equipment_cap:
    ldr r0,[r2]
    ldr r0,[r0,#0x5c]
    bl ffta_native_at_cap
    ldr r3,=0x08061e69
    bx r3
.ltorg
