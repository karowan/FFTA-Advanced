.syntax unified
.cpu arm7tdmi
.thumb
.text
.macro tail address
 push {r0}
 ldr r0,=\address
 mov ip,r0
 pop {r0}
 bx ip
.endm
.macro entry name
.align 2
.global \name\()_entry
.thumb_func
\name\()_entry:
 pop {r3}
 push {r4-r5,lr}
 mov r4,sp
 mov r5,sp
 lsrs r5,r5,#3
 lsls r5,r5,#3
 mov sp,r5
 bl \name
 mov sp,r4
 pop {r4-r5}
 pop {r1}
 bx r1
.endm
entry ffta_geo_mobility
/* This entry has four live native arguments; recover saved r3 before C. */
entry ffta_geo_tile
entry ffta_geo_move
.align 2
.global ffta_geo_original_mobility
.thumb_func
ffta_geo_original_mobility:
 push {r4-r7,lr}
 movs r5,r0
 movs r1,#0x22
 ldr r3,=0x080c92f1
 bl .Lcall
 lsls r0,r0,#24
 tail 0x080ca2f5
.Lcall: bx r3
.ltorg
.align 2
.global ffta_geo_original_tile
.thumb_func
ffta_geo_original_tile:
 push {r4-r7,lr}
 mov r7,r10
 mov r6,r9
 mov r5,r8
 push {r5-r7}
 sub sp,#0x38
 tail 0x08097821
.ltorg
