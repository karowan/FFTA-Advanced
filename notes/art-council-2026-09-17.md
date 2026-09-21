# Art council review — September 17, 2026

The user explicitly requested this three-reviewer council and Sites sharing of the drafts after review. This is bounded authorization for this art gallery; it does not authorize publishing game binaries or launching the game.

Suitable for a draft gallery. No class is production accepted.

All three reviewers inspected all ten generated source sheets. The native reviewer inspected all ten game-size conversions and a Samurai battle capture. The identity reviewer also inspected both Samurai walking drafts. This was a visual review; no new game tests were run.

## Per-class findings

### 116: Samurai

- Identity: The kabuto, red layered armor and katana clearly read as Samurai, rather than Ninja.
- Design/continuity: Chunky eyes and body shapes differ from the finer Dark Knight and Viera designs. Lock hand placement and body volume.
- Conversion: The strongest conversion, but one eye and armor separation disappear. The battle proof covers idle only; the stance still needs a stronger isometric read.

### 117: Human Dark Knight

- Identity: Closed helm, amber visor, torn mantle and broad sword establish a strong identity.
- Design/continuity: Front columns 1–2 repeat the same facing while shoulder and cape presentation change. Fine trim and narrow limbs use a different level of detail from Samurai.
- Conversion: The visor disappears and arms blend into a thin, dark body. Enlarge the visor and separate the torso and limbs.

### 118: Bangaa Viking

- Identity: Fur, teal cloth, axe and exposed tail give a clear Viking silhouette.
- Design/continuity: The rounded snout reads more like a friendly dragon. Check Bangaa muzzle and neck proportions; the idle rows barely differ.
- Conversion: Costume cues survive fairly well, but eyes and hands vanish. Strengthen those shapes before extending the animation.

### 119: Bangaa Dark Knight

- Identity: Armored muzzle, low crest and plated tail distinguish it from the Human Dark Knight.
- Design/continuity: The silver shoulder dominates the face and changes apparent size between rows. Clarify the sword silhouette.
- Conversion: The bright eye and helmet structure disappear; highlights fragment into disconnected patches and body bulk shifts between rows.

### 120: Nu Mou Chemist

- Identity: Long muzzle, drooping ears, goggles, apron and colored bottles communicate race and role.
- Design/continuity: Bottle harness and satchel proportions vary between poses. Simplify tiny buckles and goggles into larger identity cues.
- Conversion: The silhouette and three reagent colors survive, but eye, hand and bottle outlines merge.

### 121: Nu Mou Geomancer

- Identity: Earth-colored mantle, stones and staff suggest earth magic.
- Design/continuity: The short, puppy-like muzzle conflicts with the long Nu Mou muzzle in the Chemist and original references. Correct the racial anatomy first.
- Conversion: The staff gem loses its green separation; earth patterns become noisy brown pixels.

### 122: Moogle Chemist

- Identity: Pompom, goggles, coat and bottles create a clear profession and race.
- Design/continuity: Lock the face, bottle positions and wing silhouette; its facial proportions differ from Bard.
- Conversion: Rejected conversion: pale fur shifts green/cyan, goggles merge, and wings become purple tabs. The body is crowded by the ears and pompom.

### 123: Moogle Bard

- Identity: Feathered cap, scarf and lute give one of the clearest class silhouettes.
- Design/continuity: Unify its large nose and head proportions with Moogle Chemist. The second-row head tilt is too large for a simple breathing frame.
- Conversion: The lute loses definition and the feather merges with ears. Use a larger, simpler instrument shape.

### 124: Viera Dancer

- Identity: Raised hands, open sleeves and flowing sash convey dance clearly.
- Design/continuity: The lower-row crouch is a substantial motion; define a sequence so hands and clothing do not pop. Thin details need stronger shapes.
- Conversion: The face becomes blank, fingers disappear and ankle ornaments become stray pixels. Sleeves and sash are the strongest remaining cues.

### 125: Viera Mystic Knight

- Identity: Silver-violet armor, saber and split mantle communicate a distinct knight.
- Design/continuity: The magical identity is weak beyond a small gem. The design is too slender and finely shaded for the current native footprint.
- Conversion: Among the weakest conversions: narrow torso, absent eyes, disconnected armor highlights and a barely legible weapon.

## Priorities

- Use consistent proportions and detail density for each race.
- Revise faces, hands and key costume shapes with imagegen for the actual game-size footprint.
- Fix the Moogle Chemist palette shift before producing more frames.
- Lock facing, equipment side and body volume; correct Samurai gait and the Human Dark Knight turn sheet.
- Keep each graphics consumer's acceptance separate. An idle proof does not establish complete sprites.

## Animation limitations

Samurai walk-v1 mixes facings. Walk-v2 improves the facing but repeats the same leading leg; both animation reviewers identify a sheath-side error at row 2, column 3 (one-based). Neither walking draft is accepted or imported.

The earlier catalog note used a zero-based cell index for the same sheath issue; gallery review coordinates are explicitly one-based.

## Evidence and publication boundary

Source paths and SHA-256 identities are in `src/art/imagegen/catalog.json`. The gallery builder verifies every source hash and copies only those generated sheets and their existing technical conversions. No original extracted graphics, game screenshots, ROMs, saves or local tools are included in the hosted gallery. Independent site checkout: `the separate local art-gallery checkout`.

All G01–G04 gates remain open. Samurai has only a partial idle import proof. Other actions, water, menu, portrait, equipment, effect and status consumers remain separate acceptance work.

## Published gallery

- Private Sites URL: https://ffta-expansion-art-drafts.krowan.chatgpt.site
- Publication verified succeeded; version 1.
- Site project: appgprj_6aac3ffa6fd08191b7a570030f4a4edc
- Site source commit: c72964a7e8ff9995ad33ebb11552e020af92ac49
- Saved version: appgprj_6aac3ffa6fd08191b7a570030f4a4edc~appgver_64a39398a6788191807c59ed39df1114
- Deployment: appgdep_6aac413633b88191ad357ef48fd72552
- Validation: 10 class cards, 10 conversion panels, all local asset references, 20 image hashes, JavaScript syntax. No browser visual QA or new game runtime tests were performed for this gallery.
