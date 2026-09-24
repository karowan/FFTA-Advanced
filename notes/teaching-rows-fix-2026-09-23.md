# Equipment help lesson rows

Status: built and tested; not packaged or promoted to **Play Mod.cmd**.

## Defects

The native equipment-help row builder (`C8D14`) fills a 28-byte buffer: a
count and three 8-byte rows. Original multi-race classes (jobs 5..22) merge
consecutive racial entries into one row with cycling badges, so original items
never exceed three rows. Expansion items teach each lesson to every racial job
in turn. The ten Dark Knight swords and Chemist knives with two lessons for two
races produced four rows. The fourth row overwrote adjacent pointers and UI
state. Symptoms: missing first row title, garbled badges and, in shop R Info,
badge-like garbage over the Clan Funds pill that persists on later items.

Three consumers look up each row's AP by the first entry for the row's job
(`8067236` shop list, `806FC8C` shop info, `808C842` party/Item List help).
Every item teaching two lessons to one job showed the first lesson's AP on
both rows, for example Desperation 150 instead of 300 and Sea Legs 100
instead of 150.

## Fix

[Builder](../scripts/build-teaching-rows.py) authenticates the job-visibility
release `267fd273bffe2c26a7ed3507d236af80a29b74a8`, its unchanged native
builder and consumer instructions and each replaced byte range. It compiles
[C](../src/engine/teaching-rows.c) and [Thumb hooks](../src/engine/teaching-rows.s)
into blank ROM `0x1FF1000..0x1FF1FFF` (806 bytes used). This reservation is
now owned by the teaching-row fix. Six trampolines are the only other changes:

- `C8DC0`: native row grouping for jobs 5..22; expansion jobs in one registry
  job group (DRK 117/119, CHM 120/122) merge consecutive entries teaching one
  lesson, up to three badges. The builder stops at three rows.
- `8067236`, `806FC8C`, `808C842`: AP lookup matches job and lesson name.
- `808C8A8`, `806FD10`: the single type icon uses the first row, as the shop
  list already does. No original item mixes lesson types.

The family table is generated from `build/expansion/registry.json`. No save
data, item, lesson, AP or teaching-set records change.

## Evidence

```powershell
& '.\Test Expansion.ps1' -Plan scripts/teaching-rows-test-plan.json -Only test-teaching-rows-ui
```

Run `20260924T052253.940556Z` passed all three steps on candidate
`3447490fb33524d62c502b145f3f1d9306c3dfa6` (a rebuild reproduced the hash).

- Native ARM, 1864 checks over item records 0..460: the parent overflows on
  exactly items 385..389 and 409..413; the candidate never exceeds three
  guarded rows; all original items build identical rows and keep their AP;
  every expansion row shows its own lesson's AP; type icons use row zero.
- Real core, 28 checks with fixed inputs from `build/test-lab/early-town.sav`
  on shop R Info, Item List and Equip Items (Gloom Sword, Sanguine Edge, Storm
  Axe, Raider Axe): row counts, equal/distinct AP rendering, one Action icon,
  clean panel bottom after Sanguine Edge and cycling Human/Bangaa badges.
- The same UI script with `--parent` fails 15 checks on the release, including
  the persistent shop-panel garbage.

Not covered: packaging, cold saves, battle results and the equipment preview
grid, which do not use this builder. Clipped long lesson names are fixed by
the later [equipment revision](equipment-revision-2026-09-24.md).
