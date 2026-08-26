# Story

Free-form space for the machine's narrative — overall arc, beats, tone, anything that doesn't
belong to one specific feature yet. Not maintained or pruned automatically, same as `IDEAS.md`.

Once a piece of this is confirmed and attached to a specific mechanic, copy it into that
feature's `story.hook`/`story.beats` in `design/features/<id>.yaml` (see `design/README.md`'s
layer model) — this file is the staging area, the feature files are the tracked destination.

## Playfield description

Cleaned up (typos fixed, Portal terminology corrected) and cross-checked against
`design/research/onshape-cad-findings.md` (real CAD) and `machinefolder/config/hardware-switches.yaml`
(real wiring). Where something doesn't yet line up with hardware/CAD, it's flagged inline as
**(needs confirmation)** rather than silently guessed — see "Open questions" below for the full list.

### Bottom

- The flippers are hard-wired directly via buttons to the power supply. This might move onto the
  controller eventually, but it's not needed for the game to work — it does mean any
  flipper-based rules/awards are harder to build until that happens.
- The shooter lane has a manual and an automatic shooter; the automatic shooter can be used for
  refires, extra balls, etc.
- There's also a pop-up ball saver that pops up between the flippers to bounce the ball back
  **(confirmed as a distinct mechanism from the top-loop pop-up blocker below, not the same
  part reused twice — but no matching switch/coil exists in hardware config yet, still needs a
  hardware plan)**.
- There are two slingshots in the normal locations.
- There are inner and outer lanes on both sides **(needs confirmation: hardware only has 5
  generic `s-bottomlane1..5` switches — which are inner vs. outer, left vs. right? see
  "Switches to physically locate" below)**.

### Right side, middle

- The right side has a Companion Cube dropper, mimicking the cube dropper mechanic from the
  Portal games. It's fed a ball using a diverter at the right ramp's exit. CAD confirms this
  diverter is real (`Diverter_Rod`/`Diverter_Base` on the right ramp, per
  `design/research/onshape-cad-findings.md`) — this description matches that finding directly.
- In front of that diverter are a few stand-up button targets.
- The right orbit entrance sits between the right ramp and the Companion Cube dropper.
- Further up is the entrance to the right ramp.
- The up-ramp is 3D-printed and houses a secret path feeding Portal A.
- The fly-over is shaped like a Portal **Hard Light Bridge**, built from side-lit blue plexiglass
  — matches CAD's `light bridge rail right`/`light bridge rail left` parts exactly.
- Next to the ramp is a ball lock, **Portal A**, which can be fed via the secret path from the top
  (between the pop bumpers) or from the front.
- This ramp drops above the right inlane.

### Right side, top

- Behind Portal A and the ramp are the pop bumpers.
- Next to the portal (hidden in that plastic) is a third flipper, used to hit the ball leaving the
  top loop via the middle **(confirmed as a real intended mechanism, still to be wired — no
  switch or coil exists for it in hardware config yet)**.
- Above the pop bumpers are the standard (top) lanes.

### Top (the loop)

- There's a loop around the whole top, fed from the shooter lane or from the left/right loop
  entrances, next to (on the outside of) the two ramps.
- There's a spinner in the loop **(needs confirmation: CAD confirms a real `spinner` assembly
  exists, but there's no dedicated switch for it in hardware-switches.yaml yet — also worth
  noting this corrects `design/research/portal-themes-and-pinball-design.md`, which assumed no
  spinner existed on this machine at all)**.
- There's a pop-up blocker in the loop that routes the ball into the top lanes on launch
  **(confirmed as a distinct mechanism from the bottom pop-up ball saver above — possibly the
  CAD `popup post` assembly, though its position wasn't checked during the CAD pass, and it
  isn't wired in hardware config yet)**.
- In the middle part of the top section is an "exit" ball lock, behind a set of drop-down
  targets — a reference to the exit of a Test Chamber in Portal, once you've solved the puzzle;
  perhaps a way to end a mode **(likely `s-exit-success` by name — "exit" + "success" fits a
  completed ball lock well — but still needs your confirmation)**.
- The exit also houses a complex mechanism: the **Aerial Faith Plate**, an existing Portal puzzle
  element. Here a ball is caught on the playfield (**confirmed: `s-vuktop`, "VUK Left Top" — a
  vertical up-kicker fits "caught, then later fired" exactly**) and, at a later moment, fired
  onto a platform (on the exit tool); that platform has a button the ball would hit, and the
  ball then rolls (via a secret path) to **Portal B** (**confirmed: `s-vukmid`, "VUK Mid
  Field"**), on the side of the left ramp's up-ramp. Note this means the existing `s-aerial`
  switch in `aerial.yaml` isn't the whole mechanism — it may be the platform button stage, or a
  separate simpler switch that predates this fuller description; worth reconciling once
  `aerial.yaml` gets revisited.

### Left side, top — under the up-ramp

- The up-ramp hides the area of the **Aerial Faith Plate** (`s-vuktop`) and Portal B
  (`s-vukmid`).
- This ramp drops at the left inlane.
- This lines up with CAD: `Faithplate walls` is confirmed sitting mid-left of the playfield (see
  `design/research/onshape-cad-findings.md`) — consistent with the Aerial Faith Plate being on
  the left side, not the right as the very first draft of this doc assumed.

### Left side

- The left orbit entrance sits between the left ramp and the incinerator ball lock.
- The left ramp starts between the left orbit and the Aerial Faith Plate area. Its fly-over is
  tubular, with LED tubes around it to look like a **Tractor Beam** (the directional light/energy
  stream from the Portal games, also known as an Excursion Funnel) — mirroring the right ramp's
  Hard Light Bridge fly-over with a distinct Portal motif rather than a matching one. This ramp
  drops at the left inlane.
- An incinerator ball lock, modeled after the Companion Cube incinerator from Portal
  **(needs confirmation: likely `s-insinerator` — this may be the same mechanism as the
  top-middle "exit" ball lock bullet above described from a different angle, or a genuinely
  separate one; please confirm which)**.
- A big rollover button *(read "puper-super" as "super-duper" — please correct if that's wrong)*
  — matches `s-button`.
- A ball saver in the left-most outlane **(not in hardware config yet, no kickback coil exists)**.
- The left sling sits just above the flippers, standard placement, same as the right sling.
- Two of the 5 bottom lanes sit to the left of the left sling **(partial answer to the
  inner/outer lane mapping open question below — 2 of `s-bottomlane1..5` are on the left; exact
  switch numbers still need confirming)**.

*(Still open: left ramp fly-over/exit detail. Please fill in.)*

## Open questions for you to confirm

1. The top-middle "exit" ball lock behind the drop-down targets — likely `s-exit-success` by
   name, but please confirm (could still be a different switch entirely).
2. Is the left-side "incinerator ball lock" the same mechanism as the top-middle "exit" ball
   lock, or a second, separate one?
3. Now that Portal B is confirmed as `s-vukmid`, what is `s-portal-m` actually? It's no longer
   assumed to be Portal B — its role needs revisiting in `portal.yaml`, which currently labels
   it just "portal transfer switch (middle)."
4. Inner/outer lane mapping — 2 of `s-bottomlane1..5` are now confirmed on the left (left of the
   left sling); which exact switches, and how do the remaining 3 split (inner/outer, which side)?
5. Spinner — confirmed physically present (per CAD); does it need its own switch added to
   hardware config?

## Switches to physically locate

For you to check against the real cabinet. Split into what's not described here at all yet vs.
what has a suspected match still needing confirmation — and a reminder list of mechanisms with
no switch at all yet, so you don't go hunting for hardware that doesn't exist.

**Not described yet — no location guess at all:**

- [ ] `s-target-e1`
- [ ] `s-target-e2`
- [ ] `s-target-r1`
- [ ] `s-target-r2`
- [ ] `s-target-m1`
- [ ] `s-target-m2`
- [ ] `s-target-m3`
- [ ] `s-target-m4`
- [ ] `s-target-l1`
- [ ] `s-ramp-l1` (left ramp exists in the story, but not its switch-by-switch detail)
- [ ] `s-ramp-l2`
- [ ] `s-orbit-top` (hardware config comment calls it "right switch bank" — where exactly in the
      top loop?)

**Suspected match — please confirm on the machine:**

- [ ] `s-exit-success` — guessed as the top-middle "exit" ball lock behind the drop-down targets
- [ ] `s-insinerator` — guessed as the left-side Companion Cube incinerator ball lock
- [ ] `s-portal-m` — role unclear now that Portal B is confirmed as `s-vukmid`; what is this
      switch actually?
- [ ] `s-aerial` — role unclear now that `s-vuktop`/`s-vukmid` cover the catch/Portal-B stages of
      the Aerial Faith Plate; is this the platform-button stage, or something else?
- [ ] `s-bottomlane1`..`s-bottomlane5` — 2 are confirmed left of the left sling; which switch
      numbers are those, and how do the remaining 3 split (inner/outer, which side)?

**Not wired at all yet — nothing to physically find, these need new hardware:**

- Third flipper (near Portal A)
- Pop-up ball saver (bottom, between flippers)
- Pop-up blocker (top loop)
- Left outlane ball saver / kickback
- Spinner (physically present per CAD, but no switch assigned)

## Ideas

Pulled from `design/research/portal-themes-and-pinball-design.md` plus what this description
newly reveals — suggestions, not commitments:

- The pop-up blocker routing launched balls into the top lanes may directly answer `lanes.yaml`'s
  open "turret gauntlet" question — it reads as an actual routing mechanism, not a turret. Worth
  updating that feature file once the open questions above are confirmed.
- This description places Portal A and Portal B as two genuinely separate physical locations
  (right-side ball lock vs. left-side area reached via the Aerial Faith Plate's secret path),
  rather than two holes that release each other. Worth checking against `portal.yaml`'s open
  "ball-lock hole-pairing" question — this may resolve it rather than needing more CAD digging.
- Portal A (right) / Portal B (left) line up cleanly with the blue/orange motif already
  established for the left/right orbits in `orbits.yaml` — Portal B/left = blue, Portal A/right
  = orange would keep both pairings consistent across the machine.
- The two ramps now have distinct, deliberately different Portal light motifs rather than a
  mirrored pair: right = Hard Light Bridge (solid blue platform), left = Tractor Beam/Excursion
  Funnel (directional carrying stream). Worth carrying that distinction into `ramps.yaml`'s
  show/light design rather than treating the ramps as visually symmetric.
- The spinner (now confirmed real) fits the "momentum conservation through portals" motif already
  used for the orbits — score-per-rotation is the standard mechanism for a spinner, and pairs
  well thematically with speed/momentum framing.
- The third flipper, hitting balls leaving the top loop via the middle, could double as a rare
  "save" mechanic feeding the Aerial Faith Plate — a ball caught there and later launched is
  already a two-stage mechanic, and a flipper-assisted entry adds a skill element to it.
- The manual/automatic shooter and mode-start callouts are a natural fit for the deadpan Aperture
  Science PA-announcer voice already suggested for general callouts in the theme research.
