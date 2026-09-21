# Expansion status effects

These notes describe the expansion engineering build. The ordinary development
launcher still opens the earlier foundation build.

## Exposed — cracked-shield icon

Fell Cleave is a powerful axe attack that leaves its user open to retaliation.
It applies Exposed when the attack is committed, even if the attack misses.
Immediate counters can therefore exploit the drawback.

While Exposed, a unit takes **20 percent more direct physical HP damage**.
Protect still mitigates normally. Reapplying Exposed does not stack it.
It does not increase healing, MP damage, or effects classified as neutral fixed
or percentage damage.

Exposed ends at the **start of the affected unit's next turn**. KO, Petrify,
the end of battle, a job change, and broad remedies such as Esuna also clear it.
Saving and resuming a battle preserves it. Previewing or cancelling an attack
does not apply it.

Immunity prevents Exposed. A unit that cannot receive this drawback cannot use
Fell Cleave; it cannot gain the attack's power for free.

## Centered — focus-ring icon

Centered grants and consumption are implemented in the private Samurai build.
Ashura grants Centered after positive enemy HP damage; eligible Iaido techniques
consume it for 25 percent more damage or healing. It does not increase Wound
pulses. The assembled player build does not yet include these Samurai actions.

## Blade Wound — three-cut icon

The private Samurai build adds Higanbana's lingering wound. A successful initial
HP hit schedules two pulses, one at the end of each of the target's next two
turns. Reapplication replaces the remaining schedule. Broad remedies remove it;
KO, Petrify, changing job, and ending the battle also clear it.

The stored amount does not recalculate on each pulse. Protect, Shell, Centered
and Exposed do not change an already stored pulse. Native Poison retains its
separate schedule. Saving and resuming preserves the remaining pulse count.

The three-cut icon cycles alongside original statuses, Exposed and Centered.
Scripted native rendering, exact graphics bytes, expiry and cold-save checks pass
on private candidate `bf9414aaa75f28c950091d6edf83e1bc98864f97`. This is focused
UI evidence; full Samurai acceptance and the remaining expansion are still open.

Original status icons continue to use the game's existing display. The private
Wound display reserves two additional graphics tiles without another sprite slot.
