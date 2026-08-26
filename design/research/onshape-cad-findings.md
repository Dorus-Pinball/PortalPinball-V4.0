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

## Open question (still unresolved)

The ball-lock "portal" hole-pairing mechanic the user described (a ball locked in hole A releases
instantly when hole B captures a new ball, giving a teleport effect) is still unresolved. The
document has separate `balldropper` / `Simplified Balldropper` / `DropperAssy` / `VUK` / `VUK high`
/ `Exit` elements not yet opened — that's still the most direct next step, now that the
Duplicate-Exit red herring above is ruled out.

## Other elements seen but not investigated

Confirmed to exist in the document (from `get_elements`), not yet explored: a `spinner` +
`spinner_bracket` (a spinner mechanism not in any current MPF hardware config or design doc), a
`popup post` assembly, WPC-style flipper hardware (`Flipper Assembly WPC`, `Flipper Bat 3inch`,
`Coil SG-23 850-DC`, etc. — real part numbers, relevant to Phase 1 flippers), and a `WPC_Trough`
assembly matching `bd_trough`. Worth a follow-up pass if flipper/hardware specifics are needed
later.
