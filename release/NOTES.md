# FFTA Advanced v0.7.8

New teaching weapons now follow the original shop upgrades. At 10 completed
battles, or after Twisted Flow, Cyril offers 47 new teaching weapons in total.
At 20 battles, or after Pale Company, it offers 74. Opening stock has 20; the
final 95 still require Desert Patrol. The shipments are cumulative. Regional
shops continue to carry their assigned new weapons.

Later teaching weapons now have prices comparable to original weapons available
at the same shop tier. Prices rose for 56 weapons; weapon stats, lessons and AP
costs did not change.

This release also includes the subsequent AI planning work. In the controlled
four-job benchmark, the fully learned mean is 4.19 seconds per decision, down
from 5.50 seconds in v0.7.7; the starting-skill mean is 1.56 seconds, down from
2.02. All 24 matched decisions kept the same available actions and final
choices. These measurements exclude camera and attack playback and do not
describe every campaign battle.

Download **FFTA-Advanced-v0.7.8.zip** and apply its BPS patch to your own clean
Final Fantasy Tactics Advance (USA) ROM. The ZIP contains no ROM or emulator.

- Clean ROM SHA-1: `4ac05441f4de70a4ec3dd932116346c61b8783d9`
- Patched ROM SHA-1: `e13b1c7afa34fcb608a8360911b0425eb27e46fc`

Back up your normal in-game save, restart the game and load it through Continue
after updating. Do not carry an emulator savestate across versions.

The exact shop ROM passed native stock and purchase checks, real shop-menu
checks, and new-job teaching checks. The AI parent, whose non-shop bytes are
preserved, passed assembled effects, AI, save/resume and timing checks. This is
bounded release acceptance, not a full campaign or physical GBA certification.

New job artwork is AI-generated. Artist contributions to improve or replace
it are welcome.
