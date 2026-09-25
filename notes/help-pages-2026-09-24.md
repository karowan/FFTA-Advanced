# Paged expansion help

Status: released in v0.7.2 (game `cc946527`, acceptance run `20260925T010005.954289Z`).
Builds on [Mystic Knight enchantments on every weapon](enchant-weapons-2026-09-24.md).

## Problem

The native help window shows two lines. Expansion help was encoded
(`encodeHelp`, [rom-builder.mjs](../src/rom-builder.mjs)) as up to three
27-character lines on one page, so 114 descriptions lost their third line. One
example is Holy Ench.: "Self: enchant. Foe: strike / and enchant. Holy on"
with "primary Fight. Icon HO." cut off. Original help that needs more
space continues on another page: the native page break `40 70 40 63` follows
every second line, the window shows its "more" arrow, and A shows the next page.
For example, Phoenix Down reads "...Revives KO'd unit." and then "Deals damage to
zombies.". The native help decoder shows that no original ability help has
more than two lines on a page. Original help ID 1086 is an exception: it uses its
own vanilla layout, which is identical to the original ROM.

The 85 expansion weapon descriptions ("Rime Saber. Teaches ...") were also
generated from the registry skill names. They still named skills renamed for
the menus ("Blizzard Spellblade", "Sanguine Sword", "Spellblade Combo"), and 30
of them no longer matched the skill lists.

## Change

[Builder](../scripts/build-help-pages.py) is a bounded text patch on the
enchant-weapons candidate. Every uncompressed expansion entry in help bank 19
with a page of more than two lines is rewritten in blank ROM
`0x1FF4000..0x1FFBFFF` (18,015 bytes used, 137 entries), and its bank-19 table
pointer is repointed. The 30 stale weapon descriptions are regenerated from
[`ability-display-names.mjs`](../src/ability-display-names.mjs). Where the
menu name only abbreviates the full name, the description keeps the full name:
"Counter Rhythm" rather than "Counter Rhy.". An example of the new text is
"Rime Saber. Teaches Blizzard Ench., Spellweave.".

The rewrite keeps the same header, words (apart from the refreshed skill
names), line wrapping and terminator, and puts a native page break after every
second line. It changes no code, save data or AP. Earlier stages still encode
with `encodeHelp`; this stage pages their output, so source rebuilds follow the
same chain.

## Evidence

```powershell
& '.\Test Expansion.ps1' -Plan scripts/help-pages-test-plan.json -Only test-help-pages-ui
```

The plan is also the v0.7.2 release acceptance: it rebuilds the chain and runs
the equipment-revision and enchant-weapons checks as well. Release run
`20260925T010005.954289Z` passed all eleven steps and rebuilt identically to
enchant-weapons `2a93fa43` and help-pages
`cc9465277898509fda703b1163cad877fc694405`. An earlier six-step run
(`20260924T162107.663265Z`) used `FFTA_MIN_FREE_DISK_GB=10`, because free disk
space had dropped to 21 GB for reasons outside this work and the plan writes
about 1.5 GB. The release run used the default limit.

- [Native test](../scripts/test-help-pages.py), 4,755 checks, over every help
  ID `0..0xFFF`, read through the native router (`19A50`) and decoder (`13E9C`):
  - The 114 repaged entries keep the parent's lines and words, with at most
    two lines per page and at most 27 characters per line. Each has one native
    page break per extra page and unchanged header flags.
  - The 30 refreshed descriptions read exactly their declared new text, where
    the parent read the previous text.
  - All other entries decode byte-identically.
  - Only ID 1086 still has more than two lines on a page, and it is identical
    to the original game.
  - The only changed bytes are the new text and its table pointers.
- [Real core](../scripts/test-help-pages-ui.py), 88 checks. Uses a generated
  Giza battle with the enchant Sniper profile, the Holy Ench. row, and Select
  to open help, on both this build and its parent:
  - Page one is identical on both and stays unchanged for 600 frames.
  - On this build, A shows page two and a second A closes help. Both presses
    stay in the ability list with the same selection.
  - On the parent, the first A closed help, so the third line was never
    visible.

Playtest: `build/expansion/help-pages/playtest/frozen.gba` with
`saves/help-pages-2026-09-24/frozen.sav` (a copy of the suspended enchant
battle; the scripted resume reaches the Sniper's turn on this ROM). Both are
ignored.

The equipment Info panels were checked with
[the teaching-row real-core test](../scripts/test-teaching-rows-ui.py)
`--current build/expansion/help-pages/current.json` (28 checks, passed). That
test does not open item help text.

Not covered: help opened from other menus (shop/Info, job and equipment
lists). They use the same native decoder and page codes as original multi-page
item help, but were not played.
