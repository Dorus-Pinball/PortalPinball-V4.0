# Ideas

 - Explicit list of feautures for future shared reference

 - A high level story file for shared collaboration, linking feautures to stuf that happens (shots, modes, etc.)

 - A clear overvie of features and what they are called in onshape & mpf config

 - clean up config with standard naming

## Shot-pattern & mode ideas from outside MPF/pinball research (2026-08-27)

Raw ideas surfaced from `plans/OutsidePerspective.md`'s community research plus standard
real-machine design patterns, checked against what's already in `design/features/*.yaml` so
nothing here duplicates an already-tracked mechanic (the skillshot rotate-lane question, the
ramp-to-ramp combo `sequence`, the dropbank escalating-value gap, and the diverter/subway
routing decision are already tracked there and in `TODO.md` — not repeated below). None of
these are confirmed designs; each still needs a story pass and the usual sign-off before moving
into `design/features/` per `design/README.md`'s workflow.

 - **Orbit loop combo**: a `sequence` device across `orbits.yaml`'s existing shot_group,
   rewarding alternating left→right→left orbit shots (the classic "loop combo" pattern, e.g.
   Twilight Zone/T3) with escalating value per leg. The orbits already carry a blue/orange
   portal-pair motif, so an alternating loop reads as "shooting back and forth through both
   portals" — a natural thematic fit, not just a scoring bolt-on.
 - **Diverter → subway → multiball lock**: flesh out `ramps.yaml`'s already-noted diverter/subway
   routing decision into a concrete pattern — route the ball through the subway to build "locks"
   (2-3), then release into multiball. This is the standard real-machine use for exactly this
   diverter+subway shape and turns an open routing question into a defined feature.
 - **Aerial plate as a timed "Conversion Gel" mode**: `aerial.yaml`'s own notes say it has "no
   natural repeat-and-build pattern" as a standalone shot. Instead, use it as a mode-qualifying
   step that arms a short timed window (e.g. 10-15s) of doubled/boosted scoring on all other
   shots — thematically it's "coating the playfield in Conversion Gel" (the exact motif already
   assigned to `portal.yaml`'s story hook), mechanically it's the classic timed-value-boost mode
   used across many real machines.
 - **Rotating award via bottom lanes**: `lanes.yaml`'s 5 bottom lanes have no proposed hook yet.
   A genuine `achievement_group` use case (pick-one/cycle-the-selection semantics — the device
   type `portal.yaml` correctly ruled *out* for its own fixed chain) — each bottom-lane hit
   advances which award is "lit" next, collected by hitting a qualifying shot while it's lit.
   Classic pop-bumper-style rotator (e.g. Addams Family mansion awards), repurposed onto the
   bottom lanes.
 - **Hurry-up shot off top-lane completion**: once the lanes "spell" mechanic is confirmed,
   completing it could light a `timers:`-backed hurry-up on a chosen shot (aerial or insinerator
   are good candidates — both currently flat-scored with no time pressure) with decaying value.
   Standard tension-building mechanic, cheap to add once the lanes spell itself is designed.
 - **Wizard-mode jackpot tour**: a concrete answer to `super_wizard`'s open payoff question — a
   3-phase structure: (1) collect a jackpot once at each of the 8 Phase 3 feature shots, (2) a
   center/major shot lights as "super jackpot" once all 8 are collected, (3) time-limited, with
   a Lawlor-style sensory shift (music layer change, LED show change) marking the phase
   transition. Reuses shots that already exist rather than needing new hardware.
 - **Extra ball/special via dropbank finisher repeats**: `dropbank.yaml`'s
   `insinerator_finisher` sequence already repeats (bank auto-resets via `c-drop`); a real-machine
   convention (also used in `BENETNATH/mpf_dealers_choice`'s ruleset, per
   `plans/OutsidePerspective.md`) is lighting an extra ball or special award after N repeat
   finisher completions rather than just escalating points — worth considering alongside the
   already-open "should repeat completion during multiball extend/restack it" question.

