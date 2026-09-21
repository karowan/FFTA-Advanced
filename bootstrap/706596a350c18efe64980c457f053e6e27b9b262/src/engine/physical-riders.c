#include <stdint.h>
#include "registry.h"
#include "evaluated-units.h"

static unsigned half(const uint8_t *p) { return p[0]|((unsigned)p[1]<<8); }

/* Native formula has already capped effective WDef at999 here. Change its
 * scalar input only; no unit stat, equipment, owner or persistent state moves.
 * The displaced instructions subsequently normalize both operands to s16. */
int ffta_physical_effective_defense(int defense,unsigned action) {
    if (action!=FFTA_GLD_AX_A1) return defense;
    return ((int)(int16_t)defense*3)/4;
}

static void remove_protect(uint8_t *recipient) {
    /* CDB0C reads EB bit02; CE094 clears it, CE448 clears its DE timer.
     * These native setters touch only the explicitly supplied unit. */
    ((void (*)(uint8_t *,unsigned))0x080ce095u)(recipient,0);
    ((void (*)(uint8_t *,unsigned))0x080ce449u)(recipient,0);
}

/* Caller contract: an evaluated successful recipient, after accuracy and
 * interception, before magnitude. This is NOT a query/eligibility callback.
 * Native A3072 supplies context+8 after12F34C selected that recipient. */
void ffta_physical_before_hit(const uint8_t *context) {
    if (!context || half(context+12)!=FFTA_SLD_AX_A4 || context[0x28]!=0) return;
    uint8_t *recipient=*(uint8_t *const *)(context+8);
    if (recipient) remove_protect(recipient);
}

/* Native1342CC has already accepted the simulated stage and selected its
 * recipient. Its nonzero-magnitude path skips ordinary status application,
 * so this combined status+damage action must also report the removal query.
 * status_byte/bit describe native context+10 status-output lookup; neither is
 * a live-unit pointer. No copying or persistent-owner resolution occurs here. */
unsigned ffta_physical_law_hit(const uint8_t *context,unsigned removal,
                               const uint8_t *status_byte,unsigned bit) {
    if (half(context+12)!=FFTA_SLD_AX_A4 || context[0x28]!=0) return 0;
    uint8_t *recipient=*(uint8_t *const *)(context+8);
    if (!recipient) return 0;
    unsigned had_protect=recipient[0xeb]&2;
    remove_protect(recipient);
    return had_protect && removal && status_byte==context+0x13 && bit==1;
}

/* Pure predicted physical reference. Shatter's target copy has Protect removed
 * before ALL native P inputs; querying a live unit, AI copy or law copy cannot
 * mutate that input. The commit hook separately applies the real removal.
 * Callers still own legal primary selection, costs, coefficient/restorative
 * policy and weapon-effect exclusions. No AP owner resolution is appropriate
 * for this temporary evaluated target. Its independent Exposed byte belongs
 * to an explicitly initialized and retired stack container. */
int ffta_physical_rider_reference(const uint8_t *context,unsigned primary,unsigned mode) {
    const uint8_t *actor=*(const uint8_t *const *)context;
    const uint8_t *target=*(const uint8_t *const *)(context+4);
    unsigned action=half(context+12);
    FFTA_EvaluatedUnit predicted;
    unsigned active=0;
    if (action==FFTA_SLD_AX_A4 && target) {
        active=ffta_evaluated_init(&predicted,target);
        if (active) {
            remove_protect(predicted.unit);
            target=predicted.unit;
        }
    }
    int reference=((int (*)(const uint8_t *,const uint8_t *,unsigned,unsigned,unsigned,unsigned,unsigned))0x0812fe39u)
        (actor,target,action,primary,0,mode,0);
    if (active) ffta_evaluated_close(&predicted);
    return reference;
}
