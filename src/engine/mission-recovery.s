.syntax unified
.cpu arm7tdmi
.thumb
.text

/* Native callers can enter with only4-byte stack alignment. Keep the saved
 * register frame in r4 and align independently before entering compiled C.
 * The continuation blocks overwrite r3 before consuming it. */
.macro recovery_save
    pop {r3}
    push {r0-r4,lr}
    mov r4,sp
    mov r0,sp
    movs r1,#7
    bics r0,r1
    mov sp,r0
.endm
.macro recovery_restore
    mov sp,r4
    pop {r0-r4}
    pop {r3}
    mov lr,r3
.endm

/* Installer: replaceCFD00..CFD0C. Replay native loop bookkeeping even when
 * custom eligibility returns0; native code retains all ordinary predicates. */
.align 2
.global ffta_recovery_posting_entry
.thumb_func
ffta_recovery_posting_entry:
    recovery_save
    movs r0,r6
    ldrb r1,[r5,#3]
    movs r2,#0x70
    ands r1,r2
    bl ffta_recovery_pub_mask
    str r0,[r4]
    recovery_restore
    adds r4,r6,#1
    str r4,[sp,#4]
    movs r1,r5
    ldr r3,=0x080cfd0d
    bx r3
.ltorg

/* ReplaceD0FB2..D0FC4, preserving the independent D0FC4 continuation. Native
 * success commits original flags; recovery completion owns no new flag. */
.align 2
.global ffta_recovery_completion_entry
.thumb_func
ffta_recovery_completion_entry:
    recovery_save
    movs r0,r3
    movs r1,r2
    bl ffta_recovery_complete_original
    recovery_restore
    ldr r3,=0x080d0fc5
    bx r3
.ltorg

/* The cached mission-result consumer has its own success flag writer. Native
 * success is any nonzero quality here, unlike the event-result C8 tag above. */
.align 2
.global ffta_recovery_dispatch_complete_entry
.thumb_func
ffta_recovery_dispatch_complete_entry:
    recovery_save
    movs r0,r3
    mov r1,r10
    cmp r1,#0
    beq 2f
    movs r1,#0xc8
2:
    bl ffta_recovery_complete_original
    recovery_restore
    ldr r3,=0x080d1ead
    bx r3
.ltorg

/* Installer: replaceD0590..D059C. Prune before native enumeration, not after
 * its capacity-limited output, which could otherwise starve later missions. */
.align 2
.global ffta_recovery_pub_list_entry
.thumb_func
ffta_recovery_pub_list_entry:
    recovery_save
    bl ffta_recovery_prune_offers
    recovery_restore
    push {r4-r7,lr}
    mov r7,r10
    mov r6,r9
    mov r5,r8
    push {r5-r7}
    sub sp,#16
    ldr r3,=0x080d059d
    bx r3
.ltorg

/* Installer: replace5EE20..5EE2C, on Yes before fee animation/debit. The later
 * 5EF18 acknowledgement occurs after payment and is too late to reject.
 * A stale offer follows the existing No path in this same native frame. */
.align 2
.global ffta_recovery_accept_entry
.thumb_func
ffta_recovery_accept_entry:
    recovery_save
    ldr r0,[r5]
    ldr r1,=0x1450
    ldr r0,[r0,r1]
    bl ffta_recovery_cached_allowed
    str r0,[r4]
    recovery_restore
    cmp r0,#0
    beq 1f
    ldr r3,=0x08013365
    bl .Lrecovery_close_dialog
    ldr r0,[r5]
    ldr r2,=0x119a
    adds r0,r0,r2
    movs r1,#0x0e
    ldr r3,=0x0805ee2d
    bx r3
1:
    ldr r3,=0x0805ede9
    bx r3
.Lrecovery_close_dialog:
    bx r3
.ltorg
