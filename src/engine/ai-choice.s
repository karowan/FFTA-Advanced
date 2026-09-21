.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_provoke_ai_filter_entry
.thumb_func
ffta_provoke_ai_filter_entry:
 pop {r3}
 @ Native common willingness and exact effect compatibility already passed.
 @ Its switch covers only effects1..92; accept only Provoke's own effect94.
 ldrh r0,[r6]
 cmp r0,#94
 bne .Lprovoke_native
 ldr r0,[sp,#12]
 ldrh r0,[r0]
 ldr r3,=373
 cmp r0,r3
 bne .Lprovoke_native
 ldr r3,=0x080c37b5
 bx r3
.Lprovoke_native:
 ldrh r0,[r6]
 subs r0,#1
 cmp r0,#92-1
 bhi .Lprovoke_next
 ldr r3,=0x080c3615
 bx r3
.Lprovoke_next:
 ldr r3,=0x080c477b
 bx r3
.ltorg
.align 2
.global ffta_ai_choice_row_entry
.thumb_func
ffta_ai_choice_row_entry:
 pop {r3}
 push {r4,r5,lr}
 mov r4,sp
 mov r5,sp
 subs r5,#8
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 ldr r5,[r4,#12]
 str r5,[sp]
 ldr r5,[r4,#16]
 str r5,[sp,#4]
 bl ffta_ai_choice_row
 mov sp,r4
 pop {r4,r5}
 pop {r0}
 bx r0
.align 2
.global ffta_ai_choice_score_entry
.thumb_func
ffta_ai_choice_score_entry:
 pop {r3}
 push {r4,r5,lr}
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_ai_choice_score
 mov sp,r4
 pop {r4,r5}
 pop {r1}
 bx r1
.macro original name,continuation,locals
.align 2
.global \name
.thumb_func
\name:
 push {r4-r7,lr}
 mov r7,r10
 mov r6,r9
 mov r5,r8
 push {r5-r7}
 sub sp,#\locals
 push {r0}
 ldr r0,=\continuation
 mov lr,r0
 pop {r0}
 bx lr
.ltorg
.endm
original ffta_ai_original_row,0x080c2625,20
original ffta_ai_original_score,0x080bded9,12
original ffta_geo_original_search,0x080bef35,64
.align 2
.global ffta_martial_ai_filter_entry
.thumb_func
ffta_martial_ai_filter_entry:
 pop {r3}
 push {r0-r4,lr}
 mov r4,sp
 mov r3,sp
 lsrs r3,r3,#3
 lsls r3,r3,#3
 mov sp,r3
 ldr r0,[r4,#36] @ native frame's row pointer at original SP+12
 mov r1,r10
 mov r2,r8
 bl ffta_martial_ai_custom_benefit
 cmp r0,#0
 beq .Lmartial_filter_native
 mov sp,r4
 pop {r0-r4}
 pop {r3}
 ldr r3,=0x080c37b5 @ native accepted-candidate epilogue
 bx r3
.Lmartial_filter_native:
 mov sp,r4
 pop {r0-r4}
 pop {r3}
 mov lr,r3
 mov r0,r8
 ldr r3,=0x080cd8fd
 bl .Lmartial_filter_call
 adds r5,r0,#0
 lsls r5,r5,#24
 lsrs r5,r5,#24
 ldr r3,=0x080c35e3
 bx r3
.Lmartial_filter_call:
 bx r3
.ltorg
.align 2
.global ffta_geo_ai_search_entry
.thumb_func
ffta_geo_ai_search_entry:
 pop {r3}
 push {r4,r5,lr}
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_geo_ai_search
 mov sp,r4
 pop {r4,r5}
 pop {r1}
 bx r1

original ffta_myk_ai_original_self_search,0x080bead5,60
.align 2
.global ffta_myk_ai_self_search_entry
.thumb_func
ffta_myk_ai_self_search_entry:
 pop {r3}
 push {r4,r5,lr}
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_myk_ai_self_search
 mov sp,r4
 pop {r4,r5}
 pop {r1}
 bx r1

original ffta_myk_ai_original_rank,0x080c294d,92
.align 2
.global ffta_myk_ai_rank_entry
.thumb_func
ffta_myk_ai_rank_entry:
 pop {r3}
 push {r4,r5,lr}
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl ffta_myk_ai_rank
 mov sp,r4
 pop {r4,r5}
 pop {r1}
 bx r1
