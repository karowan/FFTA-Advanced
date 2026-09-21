.syntax unified
.cpu arm7tdmi
.thumb
.section .text
.macro law_allocation name, result, size_register, continuation, cleanup
.align 2
.global \name
.thumb_func
\name:
    push {r1-r7,lr}
    mov r4,sp
    mov r3,sp
    lsrs r3,r3,#3
    lsls r3,r3,#3
    mov sp,r3
    movs r0,#0x84
    lsls r0,r0,#1
    bl ffta_evaluated_allocate
    mov sp,r4
    pop {r1-r7}
    pop {r3}
    mov lr,r3
    cmp r0,#0
    beq 1f
.ifc \result,r8
    mov \result,r0
.else
    movs \result,r0
.endif
    movs \size_register,#0x84
    lsls \size_register,\size_register,#1
    ldr r3,=\continuation
    bx r3
1:
.ifnc \cleanup,none
.ifc \cleanup,r8
    mov r0,\cleanup
.else
    movs r0,\cleanup
.endif
    ldr r3,=0x08022855
    bl .Lfree_\@
.endif
    @ Return through the native false-result epilogue if allocation fails;
    @ retire the first allocation if the second one could not be obtained.
    ldr r3,=0x081344e3
    bx r3
.ifnc \cleanup,none
.Lfree_\@:
    bx r3
.endif
.ltorg
.endm
law_allocation ffta_law_actor_a, r8, r5, 0x081347dd, none
law_allocation ffta_law_target_a, r6, r5, 0x081347e5, r8
law_allocation ffta_law_actor_b, r7, r4, 0x08134899, none
law_allocation ffta_law_target_b, r6, r4, 0x081348a1, r7
