.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
@ Entry patches push R3. Each observer preserves native arguments/LR and aligns
@ the C stack. Their stolen original prologues are replayed below.
.macro observer target
 pop {r3}
 push {r0-r4,lr}
 mov r4,sp
 lsrs r0,r4,#3
 lsls r0,r0,#3
 mov sp,r0
 bl \target
 mov sp,r4
 cmp r0,#0
 ldr r0,[sp,#20]
 mov lr,r0
 pop {r0-r4}
 add sp,#4
.endm
.global ffta_geo_map_reset_entry
.thumb_func
ffta_geo_map_reset_entry:
 observer ffta_geo_renderer_retire
 push {r4-r7,lr}
 mov r7,r10
 mov r6,r9
 mov r5,r8
 push {r5-r7}
 ldr r7,=0x02007f40
 ldr r3,=0x0801a06d
 bx r3
.ltorg
.align 2
.global ffta_geo_native_allocate
.thumb_func
ffta_geo_native_allocate:
 @ Replay the original7138 prologue; both native branches/rounding stay native.
 push {lr}
 adds r2,r0,#0
 cmp r1,#0
 bne 1f
 ldr r3,=0x08007141
 bx r3
1:
 ldr r3,=0x08007145
 bx r3
.ltorg
.align 2
.global ffta_geo_map_end_entry
.thumb_func
ffta_geo_map_end_entry:
 pop {r3}
 mov r4,sp
 lsrs r1,r4,#3
 lsls r1,r1,#3
 mov sp,r1
 mov r0,r9
 ldrb r0,[r0]
 bl ffta_geo_renderer_update
 mov sp,r4
 add sp,#64
 pop {r3-r5}
 mov r8,r3
 mov r9,r4
 mov r10,r5
 pop {r4-r7}
 pop {r0}
 bx r0
.align 2
.global ffta_geo_stream_entry
.thumb_func
ffta_geo_stream_entry:
 @ Overlay calls use a different descriptor and must not be intercepted.
 pop {r3}
 push {r3}
 ldr r3,=0x02007f40
 cmp r0,r3
 beq 1f
 pop {r3}
 b 2f
1:
 observer ffta_geo_renderer_stream
 beq 2f
 bx lr
2:
 push {r4-r5,lr}
 sub sp,#8
 ldr r5,[sp,#20]
 ldr r4,[sp,#24]
 lsls r4,r4,#24
 lsrs r4,r4,#24
 push {r3}
 ldr r3,=0x0801b805
 mov ip,r3
 pop {r3}
 bx ip
.ltorg
.align 2
.global ffta_geo_pump_entry
.thumb_func
ffta_geo_pump_entry:
 observer ffta_geo_renderer_pump
 bx lr
.global ffta_geo_native_pump
.thumb_func
ffta_geo_native_pump:
 push {r4-r5,lr}
 sub sp,#8
 ldr r0,=0x03000e10
 ldrh r0,[r0]
 cmp r0,#0
 bne 1f
 ldr r3,=0x0801ac85
 bx r3
1:
 ldr r3,=0x0801ad0d
 bx r3
.ltorg
