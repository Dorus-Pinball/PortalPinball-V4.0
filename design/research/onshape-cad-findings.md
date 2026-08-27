# Research: findings from the live Onshape CAD

Findings from connecting directly to the "Portal Playfield" Onshape document (2026-08-26) via
`onshape-mcp`, kept here as the backing reference for what's folded into
`design/features/*.yaml`. Unlike `portal-themes-and-pinball-design.md` (external research), this
is ground truth pulled directly from the user's own CAD.

Document: **Portal Playfield** (`8212fe3e618a0fe47cd2c238`), workspace `885dc9fd1c559656144e3042`.
179 elements total (61 Part Studios, 26 Assemblies, 26 BOMs, 12 Applications/drawings, 54 Blobs).

## Playfield schematic

A full top-down layout schematic, generated directly from real CAD bounding-box data (not
hand-drawn), is saved at `design/research/playfield-schematic.html` (open directly in a browser)
and was also published as a live artifact during the session that produced it. It covers all 79
solid bodies in the **Portal Playfield Parts** Part Studio (`a6bfd8eb17f87ad8bf47ca11`), scaled to
real inches (playfield is 21.26" x 43.31"), oriented with the shooter lane/trough at the bottom.

### Extraction method (worth keeping — has a real gotcha)

`get_parts` on this element reports 79 named parts. A naive FeatureScript query for
`evaluateQuery(context, qEverything(EntityType.BODY))` returns **3,925** bodies, not 79 — this
Part Studio has many unmerged/pattern sub-bodies (hardware, construction geometry) that don't
correspond 1:1 with the named parts list. Filtering to solids only —
`qBodyType(qEverything(EntityType.BODY), BodyType.SOLID)` — gives exactly 79, matching `get_parts`.
Verified the resulting order matches `get_parts`' order by checking 3 unambiguous cases before
trusting the rest: body #1 is a full-playfield-extent box (= "Playfield"), #2/#3 are thin edge
slivers (= "Rail_Left"/"Rail_Right").

Also worth knowing: `eval_featurescript` (via the `onshape-mcp` MCP tool) expects a single
function-literal **expression** (`function(context is Context, queries) { ... }`), not a bare
statement sequence — and returning a list of per-part maps serializes enormously (one attempt hit
10.6M characters / 330k lines for 79 parts). Returning one flat CSV-formatted **string** from the
script instead keeps the response small.

## Confirmed findings (folded into design/features/*.yaml)

- **Aerial Faith Plate is real, named CAD geometry**: a part literally called
  `Faithplate walls` (~4.7" x 8.3"), sitting mid-left of the playfield, roughly a third of the way
  up from the shooter lane end. Matches `aerial.yaml`'s theme-research finding exactly.
- **"Light bridge rail right" / "light bridge rail left"** are real named parts flanking the right
  ramp — independently confirms the Hard Light Bridge motif proposed for `ramps.yaml`.
- **The right ramp has a real diverter + subway system** — `Diverter_Rod`, `Diverter_Base`,
  `Bridge_Diverter_Cover-Base`/`_top`, and a `Subway` part sit right where `right ramp bottom` /
  `right ramp top base`/`_lid` meet. This **corrects** `ramps.yaml`'s earlier assumption of "no
  diverter hardware, just entry/exit confirmation" — that was wrong. **Not yet electrically
  wired**: no diverter coil or subway switches exist in `hardware-coils.yaml`/
  `hardware-switches.yaml` today (flagged in `TODO.md`).

## Corrected finding

Three **"Duplicate Exit1/2/3"** parts cluster near the top-left of the playfield. Initially
misread as three separate physical locations (a tempting but wrong guess at answering the
ball-lock hole-pairing question below) — **the user confirmed these are just one single Exit part
split into 3 pieces for 3D-printing purposes**, not three separate mechanisms or hole locations.
No signal about hole-pairing either way; this was a dead end, not a lead.

## Resolved: ball-lock hole-pairing question (2026-08-27)

The ball-lock "portal" hole-pairing mechanic the user described (a ball locked in hole A releases
instantly when hole B captures a new ball, giving a teleport effect) is now answered: **the CAD,
as built, does not support it.**

Opened all the previously-unexplored elements:

| Name | Type | Contents |
|---|---|---|
| `balldropper` | Part Studio | 21 parts: subway, bracket, playfield cutout, bottom_1/3, cylinder, top2, riserbase, risercylinder, motor holder cover, valve, + unnamed |
| `Simplified Balldropper` | Part Studio | 9 parts, same names as above — a simplified/derivative version of the *same* single mechanism |
| `VUK` / `VUK high` | Part Studio (each) | **1 part each: just a bracket** (height variant of the other) |
| `Exit` | Part Studio | **1 part: just "Exit Cover"** |
| `DropperAssy` | Assembly | 9 instances, all sourced from `balldropper`. One Revolute mate + one mate group — a single degree of freedom (one valve/riser actuator) |

Cross-checked against the actual top-level **Portal Pinball Assembly** (`d3f79d14fcaf02d7c5b00654`,
26 instances): it contains exactly **one** `DropperAssy` instance and **zero** instances of `VUK`,
`VUK high`, or `Exit` — those three are unused/orphaned concept stubs, never placed in the
machine. The real integrated path lives in **Portal Playfield Parts**: `Subway`, `Tube_Base`/
`Tube_Ramp`/`Tube_Tube`, and a single `Portal Vuk` part (one instance) — a straightforward single
entry (dropper) -> passive tube/subway -> single exit (`Portal Vuk`) path, with one actuator and
no see-saw/dual-solenoid/coupled-motion feature anywhere that could link two capture points.

**Conclusion**: this is a single linear ball-drop/VUK transfer, not a two-hole pairing mechanism.
The instant-teleport-via-pairing mechanic isn't latent in the existing geometry — it would need
new physical design work (a second capture point + a coordinating linkage) if still wanted. This
directly validates `design/features/portal.yaml`'s implemented `sequences:` rule (a strictly
ordered dropper -> portal-transfer -> exit-success path), which already matched this single-path
reality rather than assuming pairing.

## Other elements seen but not investigated

Confirmed to exist in the document (from `get_elements`), not yet explored: a `spinner` +
`spinner_bracket` (a spinner mechanism not in any current MPF hardware config or design doc), a
`popup post` assembly (WPC-style solenoid + plunger + bracket, position within the main assembly
not checked — worth a follow-up if `lanes.yaml`'s "turret gauntlet" hook is pursued), WPC-style
flipper hardware (`Flipper Assembly WPC`, `Flipper Bat 3inch`, `Coil SG-23 850-DC`, etc. — real
part numbers, relevant to Phase 1 flippers), and a `WPC_Trough` assembly matching `bd-trough`.
Worth a follow-up pass if flipper/hardware specifics are needed later.

## Follow-up findings: lanes, orbits, slings, skillshot, dropbank (2026-08-26)

Same document/workspace as above. Used `get_parts` on **Portal Playfield Parts**
(`a6bfd8eb17f87ad8bf47ca11`) again, plus `get_assembly`/`get_assembly_positions` on the top-level
**Portal Pinball Assembly** (`d3f79d14fcaf02d7c5b00654`, 26 instances) and a fuller nested listing
via `Assembly 2` (`4b3f38903ff83cb027552ca6`, 68 instances — effectively every named part in the
"Portal Playfield Parts" studio placed into the real assembly context), and cross-checked
positions against the existing `design/research/playfield-schematic.html` bounding-box data.

- **orbits — confirmed.** `right orbit` and `left orbit` are real, large named parts (not just
  switch numbers) spanning most of the upper third of the playfield — bounding sizes ~10.0" x
  13.6" (left) and ~2.1" x 12.9" (right) per the schematic's part table. Directly confirms
  `orbits.yaml`'s shots. Note the two sides are not the same shape/size — worth keeping in mind
  if the "clean left/right pair" framing in the story hook assumes visual symmetry.
- **slings — confirmed.** `Slingshot Rubber Left`/`Slingshot Rubber Right` are real named parts,
  ~2.05" x 4.45" each, sitting in the lower-middle of the playfield near the flipper zone (classic
  sling placement). Directly confirms `slings.yaml`'s shots with no ambiguity.
- **lanes — partial.** `toprail` is a large real part spanning nearly the full width of the top
  ~40% of the playfield (bounds x:4.7"-207.9", y:2.8"-183.9" in schematic space) — consistent with
  being the backing rail behind the 3 top lanes, though no individual per-lane-channel parts (top
  or bottom) are separately named anywhere in the document. A single `lane guide` part exists, but
  it sits mid-playfield next to an 8-instance `Small Post` standup-target grid (unrelated to
  either lane group), not near the top or bottom lanes. **No turret/rotating/pop-up mechanism was
  found positioned near the top lanes** — the `popup post` assembly noted above exists in the
  document but its position wasn't checked, so it neither confirms nor rules out the
  "turret gauntlet" story hook. Bottom lanes (5) still have zero identified CAD geometry — that
  open question from `lanes.yaml` stays open.
- **skillshot — partial.** `shooter ramp` sits directly beside `Rail_Shooterlane`/`Rail_Trough` at
  the very bottom of the playfield, confirming the physical geometry around `s-launch`/
  `s-plunger-lane` is exactly where expected. This doesn't resolve `skillshot.yaml`'s open "which
  lane counts as the skillshot" design question — that's a rules decision, not something CAD
  geometry can answer.
- **dropbank — unconfirmed, a genuine gap.** No part or assembly named for a 3-target drop bank or
  an "insinerator" mechanism exists anywhere in the document — not in the 79-part Part Studio, the
  fuller 68-instance assembly listing, or any of the 26 top-level assemblies. Two loose `Target 1`/
  `Target 2` parts exist on the right side of the playfield, but there's no `Target 3`, so they
  don't cleanly map onto `s-drop1/2/3` either — likely unrelated standup targets, not the drop
  bank. A dedicated `Button` assembly does exist and directly matches `s-button`. This is the same
  category of open question as the ball-lock hole-pairing question above — not yet resolved.
