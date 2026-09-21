.syntax unified
.cpu arm7tdmi
.thumb
.section .text

.macro aligned_call target
 push {r4,lr}
 mov r4,sp
 mov r3,sp
 lsrs r3,r3,#3
 lsls r3,r3,#3
 mov sp,r3
 bl \target
 mov sp,r4
 pop {r4}
 pop {r3}
 mov lr,r3
.endm

.align 2
.global ffta_art_party_parent_entry
.thumb_func
ffta_art_party_parent_entry:
 aligned_call ffta_art_party_parent_allocate
 ldr r5,=0x03002778
 str r0,[r5]
 movs r4,#0xed
 lsls r4,r4,#8
 ldr r0,=0x03000e54
 str r4,[r0]
 ldr r3,=0x08024655
 bx r3
.ltorg

/* Assembler conditional is supplied only by the compact Status builder. */
.ifdef FFTA_ART_COMPACT_STATUS_ASM
.align 2
.global ffta_art_party_readonly_entry
.thumb_func
ffta_art_party_readonly_entry:
 aligned_call ffta_art_party_mark_readonly
 ldr r1,=0x030027a4
 movs r0,#0xff
 strb r0,[r1]
 movs r0,#1
 bl ffta_art_party_call_constructor
 ldr r3,=0x08070695
 bx r3
.ltorg
.thumb_func
ffta_art_party_call_constructor:
 ldr r3,=0x0807109d
 bx r3
.ltorg

.align 2
.global ffta_art_party_context_entry
.thumb_func
ffta_art_party_context_entry:
 aligned_call ffta_art_party_context_allocate
 adds r1,r0,#0
 str r1,[r5]
 ldr r3,=0x08071141
 bx r3
.ltorg

.align 2
.global ffta_art_party_list_entry
.thumb_func
ffta_art_party_list_entry:
 push {r4,lr}
 movs r4,r0
 aligned_call ffta_art_party_list_offset
 movs r1,r0
 movs r0,r4
 pop {r4}
 pop {r3}
 mov lr,r3
 adds r1,r0,r1
 ldr r2,=0x2d50
 adds r2,r0,r2
 ldr r3,=0x080711d5
 bx r3
.ltorg
.endif

.align 2
.global ffta_art_party_parent_free_entry
.thumb_func
ffta_art_party_parent_free_entry:
 aligned_call ffta_art_party_parent_free
 movs r0,#0
 str r0,[r4]
 ldr r3,=0x0802468d
 bx r3
.ltorg

/* Preserve the caller identity before any BL. Native arguments and callee
 * registers survive the guard; only the exact owned party callsites bypass. */
.macro heap_guard name,original
.align 2
.global \name
.thumb_func
\name:
 push {r0-r4,lr}
 mov r1,lr
 mov r4,sp
 mov r3,sp
 lsrs r3,r3,#3
 lsls r3,r3,#3
 mov sp,r3
 bl ffta_art_party_heap_bypass
 mov sp,r4
 cmp r0,#0
 beq 1f
 pop {r0-r4}
 pop {r3}
 bx r3
1:
 pop {r0-r4}
 pop {r3}
 mov lr,r3
 ldr r3,=\original
 bx r3
.ltorg
.endm

heap_guard ffta_art_party_heap_init_entry,ffta_art_party_original_heap_init
heap_guard ffta_art_party_heap_close_entry,ffta_art_party_original_heap_close

.align 2
.thumb_func
ffta_art_party_original_heap_init:
 push {r4-r6,lr}
 adds r4,r1,#0
 adds r6,r0,#0
 ldr r5,=0x0836d4b8
 ldr r3,=0x080070d1
 bx r3
.ltorg
.align 2
.thumb_func
ffta_art_party_original_heap_close:
 push {lr}
 ldr r1,=0x0836d4b8
 ldr r2,[r1]
 movs r1,#4
 ldr r3,=0x08007195
 bx r3
.ltorg
