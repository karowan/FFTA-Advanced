# Expansion implementation journal

The active goal is the entire approved v0.7 expansion, followed by a council
review and correction cycle. The foundation is a working baseline, not the
finished expansion. The separate `build/expansion` area is under development.

## Confirmed contracts

- The clean USA ROM SHA1 is `4ac05441f4de70a4ec3dd932116346c61b8783d9`.
- `scripts/generate-expansion-registry.mjs` allocates 10 racial jobs, 129
  lessons, and 85 items from the approved ledgers. Its registry explicitly
  distinguishes allocated IDs from working effects.
- Native Human ability indices are 1..141. New Human indices 144..177 require
  34 bytes per unit outside the native AP array; indices 142/143 are reserved.
  Increasing the native loop bound alone overwrites live unit fields at +D0.
  Other races' expanded indices fit the existing AP array.
- Internal mission gates are 7 (Twisted Flow), 13 (Pale Company), and 19
  (Desert Patrol). The UI mission numbers 5/11/17 are not internal indices.
- The native inventory region is 0x02001940..0x02001F1C (1500 bytes).
  `scripts/probe-save-capacity.py` proved every byte survives actual game
  save, emulator restart, and Continue/Load, with roster and adjacent names
  intact. This is a serialization test, not an inventory port test.
- Candidate compressed layout: 512 count bytes, 24 x 34 Human AP bytes,
  and 172 metadata bytes. Do not enable until every surviving native inventory
  access and unit lifecycle is covered. Manual inventory sorting also needs
  an explicit preservation decision; upstream removes it.
- Battle unit lookup 0x0802DE58 can return original party records at
  0x02000080 or 12 enemy records at 0x02002FC4, matched by +104 battle ID.
  Save/load staging copies also exist, so pointer subtraction is not a
  universal AP identity mapping.

## Council findings to resolve

The upstream newInventory installer is incomplete and must not be installed
unchanged. Verified issues include quantity underflow and ignored quantity in
loseItem, incorrect overflow return from giveItem, party list index overwrite,
early false return in Throw eligibility, omitted special shop stock pass, and
many surviving native four-byte inventory readers. Native getter addresses
include CB2B4, CB320, 388C8; other remaining paths include 61DFE, 6807C,
CB210 callers, and weapon predicate CB1F4. Keep exact further findings in the
council report when delivered.

The selective job installer also needs a hook allowlist: preserve native AP
labels, equipment learning, special-character redirects, Blue Mage Learning,
Red Mage shared cures, names, story/dismissal rules, combos, and Alchemist Item.
Do not import the master installer or its default options.

The foundation Morpher size hook checks the old command ID 0x1E in command
slots. A job-ID command migration must update this check to Morpher job 0x1A
and test secondary Morpher and unrelated Red Mage. Large sprite allocation
without active morph may be intentional; rendering tests are needed before
changing it. The generic-character hook has separate untested callers.

Sorting swaps 264-byte records; AP sidecars must follow the same identity.
Native save/reload of sorting already passed in the fast lab. Active dispatch,
jail, dismissal/recruitment, and new sidecar persistence still need coverage.

## Toolchain

Installed official Arm GNU 14.3.Rel1, GCC 14.3.1, under `tools/arm-gnu`.
Archive SHA256: `864c0c8815857d68a1bbba2e5e2782255bb922845c71c97636004a3d74f60986`.
Compile for ARM7TDMI Thumb, freestanding. The original game's standalone F800
call-tail convention requires explicit treatment in Unicorn tests; ARM7 has
no Thumb-2/BLX instruction support.

## Next integration gates

1. Resolve inventory and AP persistence without corrupting original state.
2. Install expanded data and selective job/lesson/gear UI with real native
   save, shop, learning, prerequisites, and job-change tests.
3. Implement each approved action/support/reaction/combination contract with
   native battle routing, cost, law, immunity, and cross-class behavior.
4. Finish remaining vanilla+ recovery/audits and acquisition tests.
5. Council review the integrated result, fix findings, repeat relevant checks,
   package reproducibly, and report coverage honestly.

## Implemented component checkpoint

`Build Engine.ps1` now compiles `src/engine/` with the installed ARM compiler.
The engine is linked at **0x09100000** (ROM offset0x1100000), leaving the
foundation at0x1000000 and the disposable intro fixture at0x1010000 intact.
Earlier probe hashes at the old engine address are superseded by rebuilt
artifacts; check report hashes against the current binary.

- `persistent.c`: validated/idempotent inventory migration, owned/give/lose,
  atomic recipe spending, party/staging AP address mapping, sidecar swap/clear.
- `inventory.c`: equipped/free counts, a stable 446-equipment plus14-consumable
  compatibility view at **0x02033000..0x02033730**, native scalar wrappers,
  retained-view owned-count refresh, equipment count events, transferable-item
  predicate, and type-based weapon predicate.
- `load-hooks.s`: council rejection-atomicity finding fixed. Hooks are now
  **before CpuSet at0x13AA48 and0x13AAD8**. They migrate r5's staging block,
  then resume0x13AA50/0x13AAE0 to commit only on success. Invalid formats take
  the original error paths0x13AA30/0x13AACA, leaving live state untouched.
- `inventory-hooks.s`: persistent sale at0x6C942, feeding at0x5B872, and only
  the equipment branch of typed reward-capacity checking at0x61DFE. Do not
  modify the original quest/recruit branches or375 namespace thresholds.
- `inventory-menus.c`: party/equip lists with full-width counts and native
  legality/grey entries, shop sell list, and original shop buy stock including
  its appended special-stock pass. New85 stock/gates are not inserted yet.

`scripts/build-storage-probe.mjs` builds TEST-ONLY variants: storage-only,
inventory-core, inventory-menus (`--inventory-core --menus`), and a disposable
inventory-startup (`--setup --inventory-core`). These are **not** the finished
expansion and must not be copied into the user's play directories. Menu buffers
move to0x02030000 using27 guarded native shop pointer updates; old inventory
sorting writes are disabled. The old on-screen Sort Items hint still needs a
matching UI change. Item ordering is currently ascending ID, with tab filters.

Verification now includes:

- `scripts/test-persistent-engine.py`: 56,656 direct ARM cases at the last full
  run, including native give/lose comparison for375items, AP bounds,24x24swaps,
  recipes, compatibility view, original weapon classification, and both load
  shim success/error branches before commit. Re-run after current code changes.
- `scripts/test-storage-in-game.py`: actual normal native migration/save/cold
  load preserves816AP bytes, item460count,24preferences, roster/names/questitems.
- `scripts/test-inventory-startup.py`: actual new-game grants and24starting unit
  headers match vanilla; lazy CA900 migration safely initializes the format.
- `scripts/test-inventory-in-game.py`: **actual shop buy → equipment → native
  save → cold load** passed. Bronze Helm265 costs500; sale branch refunds250;
  equip preserves total-owned count; all816AP bytes and other inventory survive.
  Screenshots in `build/expansion/probes/test-*.png` were visually inspected for
  the manually explored equivalent screens. The scripted flow is repeatable.

The native menu exploration snapshots under `build/expansion/probes/` use the
current menu probe. Do not mix snapshot versions after a rebuild. Native SRAM
seeds are portable; emulator states are build-specific.

Useful controls/addresses from this flow:

- Fresh seed: Start,A opens Party; Party Start opens Item List; Right from the
  initial armor tab selects weapons. Item list header0x02030000, entries+0x230,
  stride20, countu32 atheader0, IDu32 atentry+4.
- World A240 opens Sprohm menu; Down,A enters Shop; A enters Buy. Buying uses
  A(selection),A(quantity),A(confirmation); anotherA closes Thanks; B returns
  shop main. MainDown selectsSell. Leave is twoDown fromBuy, thenA andBworld.
- PartyA unit, AEquip, threeDown selects empty slot3, A selects item, A equips.
  Marche's slot3 is halfword0x02000080+0x30. Clan gil is u32 at0x02001F64.
- ThreeB from equipped gear returnsworld. Native save sequence is Start,Up,A,
  A,A,Left,A (overwrite), then300frames.

Council artifacts: `notes/council-engine-review.md`,
`notes/council-inventory-review.md`, and `notes/job-record-layout.md`.
The job-layout report verified paired12-bit stats, growth×10, neutral fields,
free-ability+2C=0, equipment table0x51D0F4, both required shield legality paths,
and same-race visual donors. Its initial stale prerequisite concern was
withdrawn; the registry matches the approved current specification.

Still required: full native battle inventory consumers/expanded list capacity,
special stock differential tests, actual feeding, suspend/rejection/retry,
all AP consumers and unit lifecycle/sorting integration, all job/lesson/item
tables and UI, every approved effect and synergy, acquisition gates, remaining
vanilla+ recovery, final council and packaging. No new job/effect is yet claimed
as playable. The goal remains active.

## Integrated data, equipment and shipments checkpoint

The later checkpoint supersedes the component-only limitations above where
specific tests now establish behavior. `Build Engine.ps1` builds and verifies
the content/inventory probe as well as the isolated original-data probes.
The last complete run passed; content/inventory SHA1 was
`a66bafe40a4a551140f31a647f962d40623a9432`, engine SHA1
`20aef5112f918826115639a01248330b4908fca0`. These remain test artifacts,
not a finished playable expansion. No user play ROM/save was replaced.

- `src/rom-builder.mjs`, `scripts/build-job-data-probe.mjs`: bounded data
  allocation, all10 native job records, paired12-bit stat/growth encoding,
  prerequisites and individual permission masks. Native originals preserved.
- `scripts/build-content-data-probe.mjs`: 85equipment records,129race lessons,
  names,85teaching sets, equipment help and native help-bank compatibility.
  Native item0..375/teaching0..224/racial lessons remain intact. Soldier and
  Gladiator get individual extended masks; no shared native mask is changed.
- `src/engine/text-hooks.s`: pointer-bank adapter at13EA2; teaching-index
  getter selectorCA814 plus four direct byte-reader replacements at48FFC,
  6717A,6FC5C,8C822. All safely combine bytes+1D/+1E (unalignedu16 onARM7 is
  unsuitable). The council found and the implementation fixed all truncations.
- Correct equipment fields: +0D is a weapon graphics parameter; +0E is a
  u16graphics identifier, not Nono. Both retain family donor values. +18 is
  actual Nono category and is zero for our shop-only weapons. New axes still
  use Barong donor artwork; dedicated Axe battle graphics remain required.
- `equipment.c`/`equipment-hooks.s`: preserve native full-layout behavior,
  extend inline weapon classification atCAD04, allow new shield jobs through
  CAD54 and alignedCADC4 paths, reject an Axe with any second weapon/shield
  even underMonkeyGrip. Native error-slot/cleanup conventions preserved.
  Dynamic stack alignment bridges both native SP residues to compiled C.
- Icon wrappers remap only proven equipment caller contexts to native family
  donors; shared shop6796E maps only mode4. Generic quest icons and shop
  modes5/6 remain unchanged in native pixel/palette tests. A real Mission
  Items panel comparison is still being obtained by the council.
- Throw/Draw Weapon descriptor capacities at3914F8/39150C are446, retaining
  native heap allocation/free and wide menu indices. Negative252controls
  reproduce the former overflow. Busy battle heap/rendering remain to test.
- Generated `stock.h` adds exactly the approved town/stage stock after both
  native stock passes. Town identities:2Cyril,3Sprohm,4Muscadet,5Cadoan,
  6BagubaPort. Gates use native persistent flags `internalMission+0x2FF`:
  7→306,13→30C,19→312, RAM1FD0bit6/1FD1bit4/1FD2bit2.
  The council traced actual success writers and native pub predicates.
- The real checkout test caught the old absolute CBDC0 entry jump destroying
  r3's town argument. Its12-byte entry now saves/restores r3 and aligns the C
  stack. Acquisition tests must enter installed080CBDC0, not only the C symbol.

New repeatable evidence:

- `test-job-data.py`:183,542native ARM calls, original116jobs and all10new
  profiles/aliases/categories. Council `council-job-data-review.md`.
- `test-content-data.py`:14,959checks, original/new records, all5teaching
  index readers, actual native routing/decoding of1,616original+85newhelp.
- `test-equipment-icons.py`:6,915native pixel/palette/context checks.
- `test-equipment-legality.py`:46,151native calls;20,052original comparisons,
  new owners,all17axes×3jobs×5supports,bothhandorders,realcleanup,ABIalignment.
- `test-battle-inventory.py`:real nativeheap/init/free,446entries inboth
  builders,84wide-index/navigation/usability/selected-item checks.
- `test-new-equipment-in-game.py`:actual Sprohm opening stock, purchase
  RecruitAxe453 for300gil, normal equipment menu, native save/coldload,
  unrelated inventory/AP unchanged. Disposable fixture removes Marche's
  starting shield. The legality test separately requires its rejection.
- Acquisition council reports2,160installed-shop cases across alltowns/tabs/
  8gate combinations/tiers/turf, no duplicates, maximum182entries;1,275native
  price cases and170native purchase commits. See its generated report and
  `notes/acquisition-engine.md` when finalized, rather than treating a message
  as a replacement for the saved evidence.

Important remaining work: AP read/write/equipment-learning consumers, cloned
unit ownership and lifecycle/sorting sidecars; custom noncontiguous job lists,
job selection/commands/visuals; every custom action/support/reaction/combo and
cross-class effect; Axe artwork/battle consumers; populated battle list and
suspend tests; remaining vanilla+ recovery routes/audits; final integrated
council, iteration and packaging. New ability help currently0 intentionally
until their effects are integrated. Existing native CD560 checks availability
bit7 alone; do not replace it with a mastery calculation blindly. Native
CD2C4 checks lower7AP against lesson cost for job mastery. Vendor prerequisite
code uses global2AD0flags; preserve native per-unit prerequisites, not an
unexamined global unlock shortcut. The goal is still active.

## AP, commands and memory ownership checkpoint

The complete Build Engine suite passed on ability-core SHA1
`0a53a2fffd2c69c1cfb06ec862a09a121c086fc6`, content-inventory
`e2c7f9eacbc76362034149d6fb5b74c116ee5cc4`, command-data
`1b34dbf7d75040b683dfb04deff644bd8170921c`. This includes170 actual
quest-icon screenshots, purchase/equip/native-save/coldload of Recruit Axe,
equipment AP availability/removal at0/90/100 AP, original native comparisons,
and real generic-character manual sorting with34 AP bytes and potion choice.

`abilities.c` and `ability-hooks.s` now provide central AP accessors, explicit
lesson lists for the ten jobs plus Soldier/Gladiator, per-unit new job gates,
new command reverse mapping and native-prefix-preserving command discovery.
`command-data` appends command IDs116..125 and Other names896..905. Native
callers have256-byte command output capacity. First9 interior AP hooks passed
3,265 independent council cases; the8 newer party/menu hooks are undergoing
independent review. Missing party preview AP read7C4D8 is not yet enabled.
Neither new command availability nor data records enables the new jobs/effects.

Native clear pointer36D4B8 wraps the original IWRAM03005E79 helper; exact264
byte roster clears reset the slot AP and potion choice. Manual sort calls its
sidecar swap after the three native record-copy loops at foundation1000530.
14224C/142250 are only BX dispatch trampolines, not the underlying clear/copy.

The council demonstrated that upper EWRAM is live heap memory. Global heap
end is now0203F800 in all three constructors227E8/4CA00/13C078; view occupies
3F800..3FF30, and party/equipment workspace3C000 is borrowed only in those
known lower-heap scenes. Reserving16KiB caused a blank name-entry keyboard;
2KiB passed actual opening and Snowball comparisons with3,484 free bytes at
name entry. Shop uses the battle heap too and now owns its appended list at
context+9C08, rather than borrowing3C000. The current shop council is widening
native sell count/absolute indices/saved scroll while retaining signed relative
rows, and fixing two derived selected-item stores affected by list relocation.

Current in-progress copy implementation is `unit-copies.c`: a16-byte root at
0203FF30 tracks live, explicitly enlarged owners. Snapshot allocation FF8 keeps
the original E1C bytes and appends next/magic plus13×36-byte AP/potion tails.
Manager allocation3FC appends two36-byte tails and its parent budget grows96.
Selection allocation3824 appends36 bytes after the original3800/nested heap.
Native copy pointer36D4BC wraps03005EE9 only for exact264-byte copies; generic
free7170 retires owners before freeing. The three whole heap clears reset the
root. Native record strides and snapshot rollback fields remain unchanged.
`test-unit-copies.py` passed6,613 checks on frozen ability-core
`10ca5ae2bd69885be81513b931d120c1ee92f884`, including native copy/free dispatch,
all owner-pair copies, unknown sources, exact memory isolation, nested rollback,
non-LIFO frees and reused allocations. Constructor wiring has its own pending
council review. Party command preview ownership remains to implement.

Still required: copied party preview, remaining AP consumers and count
normalization without template bitmap overread; noncontiguous action lists and
Human job wheel paging; all129 battle effects/supports/reactions/combos,
animations, cross-class tests, remaining vanilla+ gates, actual populated
battle/suspend/end-to-end acceptance, final council and packaging. No user
play ROM/save was replaced. The active goal is not complete.

### Further integrated checkpoint: native UI, copies, AP effects and counts

Full `Build Engine.ps1` passed again on ability-core
`9b5eb534860cb7189f23decc13309ccbca4ddfcd`, content-inventory
`70b42d93d8e72623649bb152ca4881bc2d288a77`, engine
`88d882317f37b9146a01bdcd3e32eb00616fafa1`. No test process from this run
remains active. Additional council tests below are being added to this suite.

- Party owner was added: both native7109C allocations7240→7264, exact preview
  atowner+1BE4,36-byte tail7240. Root is now20bytes0203FF30..0203FF44.
  Native71234 teardown reaches the shared7170 retirement. Both copy routines
  are hooked: IWRAM dispatch36D4BC and library memcpy1443FC. The latter is used
  for party previews; matching by character identity is never used.
- `test-unit-copies.py` now passes13,693 cases across both copy routines and
  live roster/snapshot/battle-temp/selection/party owners. Council constructor
  test supports `--current`, freezes per hash, and passed808 assertions on
  900201d5 with both party modes, native snapshot rollback/free, all owners and
  root boundaries. It is in the full build.
- Ten newer AP/UI hooks are accepted in addition to the initial9. Primary
  preview7C392 and secondary7C4D8 use exact party preview ownership. Latest
  AP/UI test4,465cases/18,466 aligned helper entries passed on9b5eb534.
- `ffta_command_browse` preserves original command behavior and adds the
  complete new/axe job lists. Native nonzero-AP browse semantics remain
  separate from battle action availability. Command-data tests5,032 pass.
- Eight AP effect/prerequisite hooks are installed: C8B26 counts explicit
  type1 action lessons;1291AC/129224/129264 handle scripted AP loss;
  132E62/132FC6/132FF8/133D30 handle ability theft. Native CD1FC and later
  availability/equipment/Viera-Cure continuations remain. Council test
  `test-ap-writers.py` passed2,315cases/11,198 aligned C entries on8dd238a1.
- `ability-counts.c` now publishes unit+34 only after original C9F88 import;
  C9ED8 remains native. Normal/suspend successful staging load wrappers and
  CA900 lazy new-game grants publish roster counts too. First native-format
  conversion clears only the formerly-unused nonhuman AP additions; format1
  retains prototype-earned AP even if its old count remained. Unknown Human
  copies retain native count because no AP tail is owned. Council count test
  currently passes1,055 assertions on9b5eb534, with load-shim review ongoing.
- Shop context growsA360; list9C08, u16 countA338, u16selectedA33A, six u16
  savedscrollsA33C..A347. Native visible cursor remains byte44F7;17B68 signed
  relative-row behavior retained. Derived selected-item stores and renderer
  absolute-index truncations corrected. Actual337-row sell navigation, last
  item460 sale3250gil, tab/Info restoration, clamp/save/coldload all pass.
  15 native state/image comparisons pass. Both shop tests are in full build.
- Fifteen approved names exceeded native11-tile columns and caused padding
  underflow/VRAM corruption. `src/equipment-display-names.mjs` contains compact
  menu labels; approved full names stay in registry/design and now precede
  teaching text in equipment help. Original names unchanged. Exact shop icon
  callers6E6A4/6E81E added, native icon tests7,837pass. Name/font/help audit
  `test-equipment-name-widths.py`3,738checks pass; all460 names<=11tiles,
  max decoded help121bytes (native output510), max23tile line/3lines. Actual
  third-line help readability remains to check. Reward popup39EEE/39EF0 still
  needs separate typed equipment/quest routing before new equipment rewards.
- `create-battle-fixture.py` now reaches real Herb Picking at Giza with6 party
  and12 total native actors, no injected mission flags or placements. The
  earlier supposed mission-points refusal was introductory dialogue. World
  cursor needs held direction input, not8-frame taps. Native world locations
  already includeCyril18/Sprohm13/Giza20. Old8dd238a1 fixture deployment free
  heap minimum54,052; first turn free78,868/largest56,040. It freezes a matching
  ROM/state/RAM/IWRAM in probes/battle-fixture. Council is now testing actual
  preview/action/suspend lifecycle on current9b5eb534.

Next implementation: `notes/noncontiguous-command-consumers.md` maps all12
direct CCE60 users. Only Soldier2 and Gladiator16 need discontinuous lists;
ten new jobs already have contiguous records. Resolve primary job aliases via
record+5/FFfallback correctly. Pure next-member helpers plus paired loop hooks
must keep actual lesson IDs and recompute record pointers; never use global
iterator state or fake first/last. Native recruitment reconciliation620EC also
still misses new axe prerequisite credit (original-range loop, not count-driven).
New job wheel paging/selection and all129 combat effects are still not enabled;
action-data/dispatch council audit is underway. Do not mark the goal complete.

## Command integration and job wheel checkpoint

The latest source chain is job-data -> content-data -> content-inventory ->
ability-core -> command-data -> command-core -> action-data -> job-ui.
`Build Engine.ps1` compiles command-lists.c/command-hooks.s and
job-wheel.c/job-hooks.s and builds every stage, then statically rejects explicit
assembly continuation addresses that enter another hook's displaced bytes.
The normal test pipeline now includes command predicates/iteration, action
records, native battle lifecycle and actual Human job-wheel lifecycle. Council
party-list and low-level wheel tests are finishing; add them after acceptance.
No player-facing ROM or save has been replaced. Every129newcombat effect is
still UNIMPLEMENTED / NOT ENABLED; the newjobUI is a test-only stage.

- AP migration C-entry alignment fixed for all4normal/suspend variants;1121
  AP-count checks passed5dcc9329; firstconversion clears onlyadded nonhumanAP,
  template imports retain20-byte bitmap and publishexpandedcounts afterward.
- Four short command predicates and14paired native iterator hooks now cover
  all12directCCE60callers. OnlySoldier2/Gladiator16 custommembership; native
  bodies retaintype/AP/MP/status/special/AI rules. Pure successor stores no
  globalcursor; descriptorbuilders matchunitcommand+nativebank+first/last.
  Realindices1..11+172..177 and33..43+105..110, no intervening lessons.
- Council predicate13,306checks passed62ffec19. Fullbattleiterator11,918checks
  passedcurrent command-core37243bba6f38ba298e436d516d7b266fd837c3b9,
  engine3745b4400cc71e1c871b6cbf048a241e895819a0. See
  notes/command-iteration-review.md. Found/fixed27918backedge pointinginto
  displacedinit27A04: nowrecomputesr4=bank+8*lesson andresumes27A0A.
  Ordinary/restricted22rowcapacity,special85,AI40halfwords: actualSoldier+
  BlueMagic+Item33; artificial17actionSoldier+20Blue+2Items39,guardsintact.
- Party7Bselected unit is *(*03002818+1D0C), notinline; slotbyte+BF9. Fixed
  missingdereference. 7Cprimary/secondary useinlinepreview+1BE4. Secondary
  r10==1 bypass meansItemcommand, notindependenteditmode. Council had784
  originalnativecomparisons+40customcases passingf14496fd beforeactualUI.
- Action-data relocates431x28byte table to0902F4E4..09032407. It preserves346
  originalrows andzeros85newrows, repoints17exactnativeusers includingdirect
  menu/AI accesses. Allocation highwater includescommand-data, notcontent
  alone. Tests44,935assertions/67,854nativegettercalls passedpriorc7cffe25.
  Builder/testfreezeinput; currentjob-ui baseline isd81b8966b7373029b4e2fbd9a6c14d11b5603cc7.
  Fullaudit notes/action-dispatch-engine-review.md maps4callbackstages,
  context0200F3F0, HPcommitA2210,MPdebitA45B0,andlawsimulationcopies.
- Newjobwheel scopesC8A24extension to85C90; global12byteABI unchanged.
  Candidates16bytelocal; originalnativeordering sortedlow7 beforepaging
  (native89BA4sortsvisiblepage). Human13split7+6; othercounts<=12onepage.
  Currentjobchoosesinitialpage. L/R inwheelstate4 usesfirstvisibleID to
  deriveotherpage, destroysnativeicons0..oldcount-1 andcursor1A, thenrebuilds
  usingoriginal85C98continuation. Noextraheap orpersistentpage state.
  Nativeconfirmrechecksneweligibility; nativeC8C24changeoperation preserved.
  Nativezerojobcount retainsprotectedcharacters9/10/94. Donorwrappers for
  CB9E0/CBA14 onlymap116..125, preservingspecialoriginal77 behavior.
- ActualmGBA caughtwheelinputjump85C94 enteringinitialhookliteralC90..98.
  Fixed to replayr2=count/r0=context thenresume85C98. All13pages, repeatedL/R,
  confirmationcancel, Samurai116change, reopencurrentpage, save/freshload
  passed onjob-ui2d39c3fb6f0076df976cebc98bf3ed14c180bd85. See
  scripts/test-job-wheel-in-game.py and probes/job-wheel-in-game/report.json.
  This usesdisposable100APfixture, noAPprogressionclaim. NativeMarcheart
  remainsnamedcharacter, genericSamuraiwheelartisNinjadonor. Pagehintstill
  pending, asareeachothernewjob'sfullrender/equipment/battlevalidation.
- Temporarynewreactionstagingguard at12E6A4 returns0forglobal128+ before
  nativecompatibilitymaskcanindexpast16rows. Explicitlyinactiveuntilproper
  newreactionrulesareimplemented. Originalreactionflowtrampolineretained.
- Actualnativebattlelifecycle test passed d505e1ff:12actors,previewcancel,
  Fight18HP/12EXP,Wait,nextunit,SaveNow,coldResumeBattle.816AP+24potionprefs,
  sixpublishedcounts,inventory/equipment,and3FF44guard survive. Peakdeployed
  heapfree54,052; turnfree78,868, preview74,408restoresaftercancel/commit.

Next: council low-levelwheel/partyactualUI acceptance; buildfullsuite once
those finish. Combatcouncil tracingChop423axes/eligibility/accuracy/procs and
formula1300E2unclampedr5, plusaxevisualcategory31routes. KeepnativePformula,
combinecustomrationalmodifiersbeforerounding/finalcap, noFight/crit/offhand/
weaponstatusprocs. Reactionmaskguard is not animplementedreaction. Law
1343C8uses264-byteheapcopiesandcanexecuteapplicationcallbacks; futurecustom
state mustisolateevaluationandcommit, neverresolvepreviewcopiestoliveunits.

## Real axes, job lifecycle and first Chop integration checkpoint (2026-09-14)

The full pre-combat suite passed on engine3745b440/job-ui2d39c3fb. Subsequent
council tests accepted all four axe visual switches (64,512 checks), and real
mGBA Fight tests executed each of eight axes453..460 with Jona. Native hits
removed10,13,17,22,24,28,35,40 HP and awarded12EXP; frames show usable native
heavy-blade donor assets. This is not bespoke axe art or new-action acceptance.

All ten new jobs passed native selection/cancel/confirmation/gear cleanup,
reopening and exact264-byte unit cold save/load, plus paired secondary commands.
The council found and fixed native74C34 command labels truncating new text IDs
to one byte. command-label-hooks.s re-reads the full new-command name only for
116..125, preserving original byte behavior. 1,024 label boundary checks and
70 donor getters pass; immutable accepted command-label98c0a4fa/enginefca13898.

combat.c and combat-hooks.s now stage the first Chop action only. Ordered
primary weapon lookup matches native12E4F4 rather than stronger-weapon12E55C.
The native formula retains element, defense, accuracy and signed healing;
Chop applies11/10 once before the native +/-999 clamp. New-only drain3D and
Doom-cleansing3E exclusions preserve healing3F. The first clamp shim usedMOVS
where nativeADDS updatedcarry; fixed following council differential finding.
481,592 physical-final checks and20,229 installedformula/proc checks passed.

Native Charm flips only acting allegiance; targetCharm keeps its base side.
Confused direct custom invocation fails closed withoutRNG. Crucially callback
eligibility cannot use unitF6/F7 for adjacency: those hold old coordinates
during uncommittedMove. Removed that erroneous predicate after realbattle
failure; range/height stay in nativeA0014/9FEF0/12E1A8, whose explicit evaluated
coordinates enforceManhattan1 andheightdelta-3..+2. 21,867 eligibility/geometry
checks include stale coordinates and copied units; 4,265 nativeControl/Charm
checks document semantics. No committed-law completeness claim.

Real Chop targetpreview exposed a separate serious preexistingdata regression:
content-data relocated only7 racial ability pointers. Native has24 banks0..23
endingexactly51BAE4; monsters indexed into followinghelp data. Monsterreaction
preview18/index0 selectedtextFFFFFFFF and corruptedgraphics/DMA. Fixed
build-content-data-probe.mjs to preserveall24 andpatchonlyplayableraces1..5.
Actual failure frozen dc02c7b6 underchop-game-lab; fixed freshcombat5a11553b
underchop-in-game. The fresh native route now reaches a preview19damage/40%.

CURRENT UNRESOLVED: that preview unexpectedly saysKnockback, and committed
Chop stalls in gray casting animation after1320+frames, withtargetHP27 and
EXP0. Do NOT callChopimplemented/accepted yet. Councilengine tracinganimation,
councilinventory tracingKnockbackbanner. Frozenstateandfilmstrips retained.
Parent diagnosticvariants replaycompletefreshbattle route toseparate newID
fromdonoranimation behavior. Other128effects are stillunimplemented.

NEW councilcontent domain finding: original actiontablehas347rows, not346:
row346 isrealBlankCard at553E54, ending553E70 descriptor table. Agentowns
registrygenerator/build-action-data/test-action-data migration to reserve346
and shiftnewaction IDs347..431 (Chop424). Parentmustupdatecombatconstant423,
buildertests andfreeze/rebuild aftercurrent423debug; do notrunsharedbuild
untilmigration coordinated. Other relocated-table original-domain audit runs.

BuildEngine now includes acceptedaxe,physical-final,Chopnative,eligibility,
partycommand andall10job tests, but a full rerun after these latestchanges is
pending. test-chop-in-game.py is currently only a preview checkpoint and NOT
in fullpipeline. Completecancel/commit/persistence/AI/law/no-proc tests before
acceptance. Player-facing ROM/save/window have not been replaced by probes.

Correction and migration continuation: The apparent Chop animation stall was
native automatic facing confirmation after using Move+Action, coupled with a
miss. ExtraA correctlyadvancesMontblanc; no animationdonor change wasmade.
Native RNG fixtureseed0 gives18damage/8EXP,seed1gives0damage/0EXP. Targettile
stays5,14onhit: no gameplayknockback. The topbanner camefromactionrecord+22
preview-message A5. Settingonly+22to0removesit;A8showsAimedattack. Builder
nowzerosChop'spreviewhint, preservingnativeeffects/animation.

OriginalBlankCard346 nowpreserved;registrynewActionIDs347..431,Chop424,
actiontable432records. Cusesgeneratedregistry.h andASMgeneratedability-ids.inc
instead ofduplicatedChopnumber. Freshactiondatatests45,127/domain14,530/
eligibility21,883 pass. combat9f773e96/engine58c534a8passedformalrealChop
Move/preview/cancel/reopen/hit/miss/facing/SaveNow/coldResumeBattle lifecycle,
withAP/inventory/gear/MP/guardsunchanged. Lateactionobjectsarefreed; committed
resultmustbeinspectedbeforeA3762return (councilseed0count1,HPdelta18).

Latestsourcealsofixestwocanonical-rulegaps: newChopouterA0014wrapper uses
explicitevaluatedcoords torequireabsoluteheightdifference<=2 (nativeRush
retains-3..+2); andcustomprimary3Frestorativeweapon cannotbecomepositive
damageafterelementabsorb double-negation. Zero stayszero; nativeactions
unchanged. Geometry/Healerfollow-up testsrunning. Fullsuiteafterthesefixes
stillpending. BuildEngine includesfreshcombatbattlefixture thenall8native
axeFighttestsandChopgameplaylifecycle. UI/coldsave proofisnotall129effects;
onlyfirstChopcombatimplementationexists;128lessonsremainunimplemented.

Full Build Engine.ps1 passed on combat62c848bc42e92fd7652075b235c49347c6b23862,
engine485c65b5, including all component/game tests, fresh combat battle fixture,
all8 Fight axe filmstrips, Chop hit/miss/cancel/facing/native SaveNow/coldResume.
Log frozen build/expansion/full-suite-62c848bc.log. Geometry30257 checks,
newracialbank192 nativegetter/name cases, restorative20344 nativecombat and
481952 finalmultiplier checks accepted. This remains first1effect, not129.
New work in progress:8 combo profiles/weapon gates andTomahawkLOS.

Continuation: combat5b90d5fb /engine5959a348 accepted full Tomahawk native
range4 target/cancel/reopen/hit/miss/4MP once/Wait/facing/SaveNow/coldResume.
Throw animation145 reads correct454 axe; missing equipment icon callersD601A
andD6614 caused quest-icon rectangle. Scoped mapping fixed,3856 native
icon/ABI and570 reward checks pass, physical steelblade seen in freshframes.
Eight combo profiles128..135 copy named native donors15/2/7/17/23/32/6/11
with legalorderedprimary categories; original0..33 preserved. Actualcombo
council tests initiation/participation/native-donor outcomes/coldload all10
owners. NuMouChemist knife animationhang discovered; scoped native staffpose
mapping in axe-visual-hooks.s is in currentbuild, freshverificationpending.

427Shatter and428Armor integrated214e6722 /engine69dcde5c. Native tests:
final613757, native28026, commit21212, installedriders17544; all347 original
outer1343C8 law comparisons exact. Shatter successA3072 clears actualrecipient
ProtectEB02/timerDE beforeP; private264bytepreviewcopy avoids live mutation.
Armor12FEA8 changes capped effectiveWDef to3/4, storedstatsuntouched. Lawphase
13434C sees copiedrecipient; status-removal25/mode1 contract works, butnative
existingoutertypes15/16 callmode0 and21harmful-statuslist excludesProtect:
no fabricated Protect/harmful-law violation. Actual427/428UI testsongoing.

Currentb6866d6e9fc5dab8b0cf97e7ada8cc42ebda635d /enginefe7135952ebeb1474b70391a37814103dd113ea5
adds426Overpower0.9P and429ReapingArc1.1P, anyunits exceptcaster,MP4/8.
EarthRender103 directional metadataarea6/range40 routesAI toBFDB0, native
B4A1C bothmodes overridden by threefronttiles, each heightdifference<=2,
valid positive-height endpoints andtargetterrainflags1/8 excluded.
A0014 custom8-neighbor eligibility usesexplicitcoords, notstaleunitF6/F7.
No newcritical/offhand/proc/drain routes. Isolated realUI all4facings confirms
threeactualexecutor members; blockedcenter retains2flanks; diagonal cursor
selectseastnativefacing. Parenttest-combat-area.py --current passesoriginal347
mode0/1,geometryheight/flags/copiedunit/Move matrices. Freshb686fixturebuilt.
Full newarc battleacceptance being written. No playerROM/save/window changed.
Executioner430 primitive reviewcaught maxHP incorrectlyread+1C (currentMP),
councilcorrectingto+1A andindependentnativegetteroraclebeforeintegration.
Fell431 Exposed stillrequires ownedbattle/copy/turn/suspendstate infrastructure.

### Arc direction and evaluated-state integration — 69a844ae

Current combat SHA1 69a844aee6a536f29e2b00959acce62de1658e27, engine ff193e511745d83c3c945cd819bd98687e925f35. Seven axe actions424..430; no431 or remaining job actions/supports/reactions enabled. Player ROM/save unchanged.

Executioner actual d658 suite passed300 checks, actual display60% vs40%, native P43→77/47, execution HP flips,10MP/cancel/turn/SaveNow/coldresume. Installed preview35292 and finisher4118 passed. Both Chemist staff-pose and Dancer rapier-pose knife fixes included. Exposed saved storage is36bytes state+1E98, standalone storage212567 checks plus actual sort/save/cold and preview/suspend/cold passed d658. Temporary law allocations and Shatter stack scopes now explicit276bytecontainers; current69a844ae test-evaluated-units11245 assertions passed, all347original law outcomes/RNG bothSP. See evaluated-unit-ownership-review.md. No Exposed gameplay events/effects yet.

Arc debugging: native UI confirmation B6FB6 takes actor wrapper1F; chosen center may be invalid so native9D6BC diagonal vector reorients. Hook must startB6FB6 (B6F86 branches there); initial B6FB2 span was invalid and crashed, replaced. Shared actual launch additionally recomputed vector96A3C and storedmanager88 at96A44; native9D3A8 writeswrapperbeforeactionbuilder. New96A40..4Chook keepsrequestedwrapperface for426/429. A3ABA..C4 corrects actionobject8 before native recipient build A3EC4. All347others delegate/replay. AI BFDB0 selectednode atdirect020101F8+5290=02015488, field1B0facing/1B1success. AIsetup93A66..70 copieschosenfaceonlyifnodeactorwrapper/action/successmatch. AIendturnface54BA is unrelated and preserved.

Isolated actual thirteen arc cases now correct: fourclear directions3members, fourhighcenters2, fourholecenters2, RightthenUp yieldsnorthsingleflank. Fresh formal test updatedsame13cases, independentnativeP controls, perrecipienthit/miss,MPonce,cancel,repreview,Move,turn,coldsave running on69a844ae. Native AI evaluator512fixtures5632checks passed d658 with controlledscore/path providers, actual native inversegeometry/all4directions. FullautonomousAIturn notclaimed. Native facing hook ABI council pending; fullBuildEngine regression latest complete still62c848bc.


### Current69 arc acceptance and next private families

Fresh test-arcs-in-game.py passed846 checks on69a844ae:13Reapingcases,2seedexecutions plus independentPcontrol each, clear/high/hole/diagonalrecipientsets, friendlyfire, cancel/repreview/noheapgrowth,8MPonce, nativeWait/facing, OverpowerafterMove0/22damage and4MP, nativeSaveNow/coldResumeinteractive. Council installed4facinghooks1146112checks and512 nativeBFDB0search→C0B46publication→93A66AIsetup→96A40launch→A39F8constructor chains12800checks. The AI scoring providers remain controlled. All10combos410checks and39weaponmatrix156checks passedfrozend658; bothknifeanimationreturns accepted.

FullBuildEngine69 firstattempt stoppedat test-copy-constructors9F850 because existing50000instructionbudget. Measured complete native13-unit snapshot/rollback51584instructions atbothSP; raisingboundedharnessbudgetto500000 permits all808 assertions to pass withAP/prefs/heap/ownership rollback unchanged. No productioncodechange was needed. Full69retry running full-suite-69a844ae-retry.log; nofinalfullsuiteclaimyet.

Parentprivate LightFoot: mobility-supports.c/.s getterCA394..CA3A0→ffta_move_support_entry, originalnativebase/equipment/Moveabilityformula then+1 ifassignedsupport141, saturatesnative127signedbyteboundary. NativeCA3EC usesresult×10forpathbudget, noMoveactiongrant. Private7d4039b55bf0b304403f4e485ddb92281dd69f59 over69a844ae passed18696nativechecks and28actualArcherColettecasesassertions: five north tiles reachableonlywithS95, uncommittedMovecancelreturnsorigin, reselectionandnativeWait/facingadvancesLeonard, coldSaveNowretainsposition/AP/S/gear. Script test-mobility-supports-in-game.py, privatefixturemobility-supports/battle. Independentenginecouncilcode/ABIreviewfoundnodefect. Notcompiledmainyet. Graceinprogressincouncil, editingonlyGraceportionssamemobilitysources; newGracetests/patchhelperindependent.

DarkSwordagentprivatelyaccepted357/358 overlaye3193a7e639d935e4c722011975029dc26177776 over69a844ae:45427nativechecks124actualbothraces+80actualresourceedgeassertions includingundeadreversalKO. Source dark-sword.c/dark-sword-hooks.s; sharedintegrationlistednotes/dark-sword-integration-review.md. Notcompiledmainyet. Waitfull69regressionfinishbeforecomposenextmain. Exposedagentownsnewexposed-effects.c/.s/patchhelper; lifecycleexpiryprivate13596checks, application/incomingdamagepending. Explicitcustomimmunitypolicyaccepted: assignedImmunity11blocksFellavailability/paidcommit; InoculationnevercancelsExposed; nofakevanillastatusIDalias. Contentagentownspropermissioncompletion/refund/Quinretry; reservedmetadata1E79bits0everaccepted/legacyblocked,1initialized, initializationonload/newmigrationpending. LegacycompletedMissingProf+absentQuinunknownhistorymustconservativelyblockaddedretry; nofabricateddeathdetection. Actualvictoryfixturefound:6knownenemyHPzero plusnativeWait thenendingdialogue; correctdispatchrouteforCaravanrequired.



### Full69 accepted; main9 + Light Foot + help accepted
Full Build Engine69a844 retry exited0, retained full-suite-69a844ae-retry.log.
Only retry fix was constructor-test instruction budget for native13-unit rollback
(51,584 instructions, raised from50,000 to500,000); production unchanged.
Main1587503e86d1fc9285ebb70ab6f04c01c40fe00e composes357/358 +141 with
all seven axes and eight combos. Current Dark Sword native45,427, actual124,
resource-edge80; Light Foot native18,696, actual28; help3,496 passed.
Help bank19 uses guarded raw10E0000 arena without moving earlier data tables,
18 lesson descriptions. No player files changed.
Next composition adds accepted Grace and recruit620AC list reconciliation.
Private recruit2e083de3... first3,521 checks passed; expanded axes-only AP case
added afterward. Native aliases80..115 require pointer-form C8570 and are not
valid ordinary job IDs for this reconciliation harness; playable original
jobs and all10 new jobs are covered. Shared packed state allocation agreed:
Exposed bit0; Centered bits1..3; explicit owner/copy paths carry fullbyte.
Inventory council updates Exposed gameplay masks and tests before composition.

### Accepted main composition and deterministic testing workflow

Full `Build Engine.ps1` run on `ad1767f8b4c78276e711d7e89e669f6b0b272097`
finished with exit0. Its log is `build/expansion/full-suite-ad1767f8.log`.
Main engine is `d250be482d9fdf504b2e2f0b8183ad16533c901f`. Accepted contents are
nine physical actions, two supports (Grace/Light Foot), eight combos, nineteen
help descriptions, expanded equipment/AP/storage/menus, corrected recruitment
prerequisite counts and Quin history/prepare. No Samurai or Exposed gameplay
hooks or custom icons are installed in this accepted main ROM.

The earlier Quin swap span6200A..14 overwrote the native62010 loop landing.
The corrected62004..10 span delegates the native name conversion and leaves
the loop intact. Quin current native1,831, actual results/new-game22, and actual
normal/suspend/legacy62 checks passed. The first deterministic runner's complete
Quin suite passed on the same ROM in
`test-runs/20260914T210535.570443Z/report.json`. A later single-step current Quin
check verified the added ROM/engine consistency preflight as well.

User explicitly requires non-agentic testing to reduce usage. `AGENTS.md` now
records this. `Test Expansion.ps1` invokes `run-expansion-tests.py` and an explicit
80-step JSON plan; the default Build Engine test phase now invokes that runner.
It uses sequential subprocesses, bounded timeouts, fixed Python hashing,
assertions enabled, an OS-held workspace lock, full per-step logs, JSON/JUnit,
and source/ROM/harness fingerprints. It stops on failure and labels unexecuted
steps. A subset is not reported as full coverage. No automatic cache yet, because
older tests have retained/generated fixture dependencies beyond the ROM hash.
Seven runner contract tests passed, covering actual process failure, timeout,
dependency order and source-change invalidation. Use inherited workspace ACLs
for scratch directories; Python TemporaryDirectory's private mode produced
inaccessible Windows sandbox directories. The self-tests now use validated
ordinary child directories and remove only those exact scratch paths.

All three council agents stopped with an account-usage-limit error. They must
not be resumed to run or monitor tests; final implementation review remains
authorized after scripted checks. Their completed code/evidence are retained.

Pending source edits: inventory council added Fell431, its availability, and
single-division Exposed factors to `combat.c`; these reference exposed-effects
functions not yet added to the main compile list. Do not treat the current
unassembled source as the accepted ad ROM or rebuild it before finishing
composition. Samurai private sources retain four direct attacks and Centered
state/payment work; its old private builder's literal source replacement no
longer matches the modified combat.c and needs composition-aware updating.
Both families must share the corrected paid spanA45C6..D4, preserving native
Fight/no-cost branches directly toA45D4. Esuna/broad-remedy admission, Samurai
Dispel/weapon-change events and Guarding Draw law prediction remain unfinished.

### Status display component and ready-state observation

Private display `de421e6eeb26d694e607fb45d77951650461864c` over ad passes13,884
native checks and24 actual-game assertions. Shared `patch-status-display.mjs`
produces the exact same private bytes as the accepted initial patch. It reserves
four OBJ tiles by changing only the battle graphics constructor's upper dynamic
pool from1E0 to1E4. Visual25Exposed and26Centered use two8x16 glyphs and the
original status sprite/cycler. Zero-slot reuse was rejected because original
descriptor3915B8 uses tile143 elsewhere. Full details and test scope are in
`notes/status-display-review.md`; no main UI integration yet.

Actual tests compare fixed native graphics/HUD, real Move/Fight/facing/next turn,
and native suspend/fresh-emulator Resume. Baseline, overlay, and active-icon
cases each deal24damage with actor47HP/14MP. The apparent attack mismatch was a
fixture that still showed the introduction: private code needs150 more frames
before the first menu. `battle-menu-observation.py` now checks native Wait/Status
text plus dark outlines without input, with a bounded budget. Its12 checks and
a new private `fixture-observed` full generation passed. `create-battle-fixture`
records readiness frames and anchor hash, rather than assuming a fixed delay.

### Fell/Exposed assembled candidate and deterministic regression

Subsequent work completes the previously pending Fell composition. Candidate
`d1565a7ee341621e58bd2bb791b065144fe51aec`, engine
`60d2d6a0375219a7f4916cab3e26e37d4cc56e67`, links Exposed and status display,
enables431, and adds its twentieth lesson-help entry. All eight axe actions
are now enabled in this engineering candidate. The approved Samurai direct
actions are still private and incomplete.

The native Fell suite passes24,351 checks on the composed image; complete
original-executor replay passes357 cases. The restored weapon-effect oracle
passes after asserting/normalizing its native callerSP+4 scratch destination.
Native status display passes13,884 checks. Its composed graphics-only attack
oracle fixes two random-return functions in recorded disposable variants;
original status atlas, native attack graphics, both new icons and native cold
resume pass. Ordinary combat hit/miss tests retain native randomness.

The full runner now has91 steps, with9 additional private Fell steps in their
own optional suite. Main-ROM acceptance remains pending the complete composed
regression. Old arithmetic/proc oracles that classified431 as unused have been
updated to its approved18/10 factor and exclusion behavior. Passing prefixes
are retained rather than repeatedly rerun. See the detailed integration note
and the per-run JSON/JUnit reports for exact coverage and remaining work.

Samurai's next integration must preserve the now-live shared Fell payment hook
and avoid applying Exposed twice to Samurai physical attacks. Concrete source
review points are saved in `notes/samurai-composition-next.md`.
