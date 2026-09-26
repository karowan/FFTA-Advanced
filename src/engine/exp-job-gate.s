@ Replacement entry of native 0812E5B4 (EXP an actor earns against one
@ target). The native function reads the actor's job (0C7EA4 attribute 4) and
@ treats every job above 82 as a special unit: EXP only for a few story
@ characters behind story flags, otherwise 0. The expansion jobs 116..125 are
@ ordinary playable jobs, so they take the ordinary path at 0812E62C like
@ jobs 0..82; all other jobs above 82 keep the special path at 0812E5C4.
@ Both continuations run with the native frame this entry rebuilds.
.syntax unified
.cpu arm7tdmi
.thumb
.text
.align 2
.global ffta_exp_job_gate
.thumb_func
ffta_exp_job_gate:
    push {r4,r5,r6,lr}
    adds r6,r0,#0
    adds r5,r1,#0
    movs r1,#4
    ldr r3,=0x080c7ea5
    bl .Lcall
    cmp r0,#82
    bls .Lordinary
    cmp r0,#116
    blo .Lspecial
    cmp r0,#125
    bhi .Lspecial
.Lordinary:
    ldr r3,=0x0812e62d
    bx r3
.Lspecial:
    ldr r3,=0x0812e5c5
    bx r3
.Lcall:
    bx r3
.ltorg
