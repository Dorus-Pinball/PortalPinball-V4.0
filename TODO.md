# TODO

Rough items noticed while working, not necessarily in scope for the current task. Checked off
when fixed, not deleted, so resolution history stays visible — except where a cleanup pass has
explicitly moved that history into `CHANGES.md`/`plans/testing-strategy.md`/`design/features/*.yaml`
instead (last done 2026-09-13; see `CHANGES.md` entries 5-8 for the 2026-08-27 software-gaps
sweep, entries 11-14 for the flipper→start/launch→plunger/trough→sling/ball-saver real-hardware
bring-up sequence, and `plans/testing-strategy.md`'s Tier 2 addendum for the reusable
MPF/testing findings from that work).

## Blocked on physical hardware work

Flippers, start/launch buttons, the plunger-lane/trough-eject coil migration to the Cobra board,
and the sling/ball-saver bring-up (including the pin swaps found, pulse tuning, and the
ball-saver's weak-spring root cause) are all done — see `CHANGES.md` entries 11-14 for the full
history, or `docs/wiring-pin-map.md` for current pin numbers/status per component.

- [ ] **Tilt**: no tilt switch exists at all yet — needs a physical switch installed before any
      config can follow. Per `plans/OutsidePerspective.md`, MPF ships a complete built-in `tilt`
      mode — once the switch exists, the MPF-side work is `modes: [tilt]` plus tagging the
      tilt-bob switch `tilt_warning` and slam-tilt switch `slam_tilt` (gets warnings-to-tilt,
      settle_time, multiple_hit_window for free), not a from-scratch design like the Phase 3
      features.
- [ ] **Right ramp diverter + subway**: CAD-confirmed real mechanism, electrically drafted
      (`d-ramp-diverter`, `c-ramp-diverter` coil, `s-subway-entry`/`s-subway-exit` switches, all
      DRAFT numbers) but not wired for real.
- [ ] **Service mode nav switches** (`sw_service_enter/esc/up/down`): electrically drafted, not
      wired for real.
- [ ] **VUK eject coils missing**: `s-vukmid`/`s-vuktop` are wired switches, but no eject coil is
      configured anywhere for either (`bd-vukmid`/`bd-vuktop` are commented out in
      `hardware-devices.yaml` with no `eject_coil`) — a ball reaching either VUK currently has no
      way to be ejected. Found while seeding `tools/hw_console/`'s registry (2026-08-30).
- [ ] **Portal dropper coil missing**: `s-dropper` has no matching coil anywhere in
      `hardware-coils.yaml` — the dropper's release mechanism (if any) isn't wired/configured.
      Found while seeding `tools/hw_console/`'s registry (2026-08-30).
- [ ] **OPP wiring checklist** (from `plans/OutsidePerspective.md`'s community research, apply
      before any DRAFT item above gets wired for real): confirm every driver + the switch that
      triggers it via a hardware rule (flipper EOS now, autofire coils already wired) land on the
      *same* physical OPP board/CPU — OPP/CobraPin hardware rules don't cross board boundaries, so
      a switch and its coil on different boards in the chain silently fail to produce a working
      rule. Also run the grounding/flyback-diode checklist from pinballmakers.com's OPP wiki page
      (all grounds tied together at the power supplies; 4004-type flyback diodes across every
      coil) — a floating ground can damage boards.
- [ ] **Aerial upkicker** (wishlist, not scheduled): would turn the aerial plate from a
      mode-qualifying switch into a real launch mechanism. No physical coil exists there today —
      this is a "should we add hardware" decision, not "wire up what's already there."
- [ ] **Trough→plunger ball transfer not confirming** (found 2026-09-06 during the first live
      real-hardware game start): `bd-trough`'s eject to `bd-plunger` pulses `c-trough-eject` and
      then fails/retries every ~10s (`balldevice_bd-trough_ball_eject_failed`) indefinitely — the
      plunger-lane eject-confirm switch likely isn't registering the ball's arrival. Not
      investigated further yet; separate from the flipper work above.
- [ ] **Trough opto board wiring damaged** (found 2026-09-11 while re-verifying trough
      switches on real hardware): `s-trough2/3/4` and `s-trough-jam` (all on chain2-0x21, the
      PSOC opto board) read intermittently/incorrectly-active with the trough empty and no
      obstruction — traced to physical wiring damage at that opto board, not a config or
      addressing problem. **Switch numbers are confirmed correct and unchanged**
      (`s-trough1..6` on `2-1-16..21`, `s-trough-jam` on `2-1-22`, all `type: NC`) — don't
      renumber these when resuming, just fix the physical damage and re-run the same test.
      Also confirmed live: **`s-trough-jam`'s active state means a CLEAR path, not a jam** —
      opposite of what the name suggests at a glance (documented inline in
      `hardware-switches.yaml`). Mid-repair ball test got partway through (1-2 balls placed,
      `s-trough3` then also `s-trough5`/`s-trough6` went active — consistent with balls rolling
      across multiple sensors before settling, not itself a fault) before the damage was found;
      re-run the full empty + ball-by-ball test once the opto board wiring is fixed.
      **Update (2026-09-11, `read-opto` branch, merged to main):** rather than re-patching the
      same fragile per-leg taps, `plans/read-opto.md` designs a proper fix — bridge the Stern
      opto board's own `VCC`/`RCK`/`SCK`/`MISO`/`GND` connector (it's a plain 74HC165 shift
      register, not a proprietary Spike bus — see `docs/stern-spike-trough-opto.md`) through a
      bare ATmega328P-PU that mirrors the 7 channels onto OPP exactly as today.
      **Update (2026-09-11, bench test):** built and bench-tested the bridge — found the board's
      **U1 (74HCT165 shift register) is dead**, not a wiring/firmware issue (see
      `plans/read-opto.md`'s "Bench findings" section for the full elimination process: power,
      ground, wiring, the Uno's own SPI pipeline, and `RCK`/`SCK` reaching the board were all
      proven correct down to waveform level with a logic analyzer; U1's inputs carry good live
      sensor data, but its serial output never responds). Two remaining paths, either is a valid
      next action:
      - [ ] **Hardwire U2's/U1's buffered per-channel legs directly into OPP**, skipping the dead
        shift register and the SPI-bridge approach entirely — no chip repair or bridge firmware
        needed, just calibrate which physical leg is which trough position, then wire into the
        cabinet and re-run the empty + ball-by-ball test above.
      - [ ] **Replace U1** (exact match: Nexperia 74HCT165D, SOIC-16 — confirmed source sinuss.nl;
        a plain non-`T` 74HC165 in the same package also works in this circuit, cheaper via
        AliExpress) and continue the original SPI-bridge plan: flash a chip via
        `tools/flash-atmega328p.ps1`, breadboard per
        `design/physical-checklists/trough-opto-bridge.html`, calibrate
        `BIT_CHANNEL`/`BIT_INVERT` in `tools/atmega328p-trough-bridge/atmega328p-trough-bridge.ino`
        against the repaired board, then wire in and re-test.

## Dev tooling

- [x] **`wiring-guide.html` status vocabulary out of sync** — fixed 2026-09-13:
      `wiring-guide.html` and `docs/wiring-pin-map.md` are now generated by
      `tools/hw_console/generate_docs.py` from `components.yaml`'s 1-6 scale directly (via a
      `_badge()` mapping: `status >= 5` → `wired`, notes containing `GAP:` → `gap`, else
      `planned`) instead of being hand-transcribed — the vocabulary can't drift out of sync again
      since there's no longer a hand-edit step to skip. See `CHANGES.md` for the full decision.
- [ ] **`tools/atmega328p-trough-bridge/`'s `.ino` firmware has no dedicated conventions doc**,
      unlike the rest of the project's documented subsystems (surfaced during the KM-overhaul
      planning pass, 2026-09-13 — not in that plan's own scope, flagged for later).
- [ ] **True graceful Ctrl+C shutdown for `tools/mpf-session.ps1`**: current `-Action Stop` is a
      tracked `Stop-Process` (hard-stop), not a real SIGINT to MPF's own signal handler —
      deliberately deferred in favor of simplicity, since a hard-stop was verified safe on this
      hardware (OPP boards de-energize drivers on serial disconnect, COM ports release cleanly).
      A true graceful stop would need a small Win32 helper (`AttachConsole`/
      `GenerateConsoleCtrlEvent`) to deliver a real CTRL_C to the child process. Revisit only if
      MPF's own clean-shutdown logic (e.g. flushing something mid-write) ever actually matters
      for a session.
- [ ] **Windows USB selective suspend fix isn't repo-level**: idle OPP COM ports crashed a live
      `mpf` session twice during real-hardware bring-up (2026-09-06), fixed via a `powercfg`
      change on this laptop's power plan (see `CHANGES.md` entries 11-12 for the incident/fix
      detail) — not something version control preserves, so it would need reapplying if this
      laptop is reimaged or the power plan gets reset.

## Needs a design decision from the user

- [ ] **Flipper coil pulse/hold tuning**: `hardware-coils.yaml`'s `c-flipper-left/right` ship
      with `default_pulse_ms: 25`/`default_hold_power: 1.0`. Real-hardware testing (2026-09-06)
      found 25ms produces no visible travel with 50V on; `pulse_ms: 200` (an untuned test value,
      not a recommendation) did move the flipper correctly. Since there's no EOS switch to cut
      power once the flipper reaches end-of-stroke, the real pulse_ms needs picking with the
      coil's actual specs/heat tolerance in mind, not just "whatever felt fine in one manual
      test" — a user decision, not something to guess into the committed config.
- [ ] `board Overviews.xlsx`'s ramps notes are just "right ramp" and a bare "?" — needs a real
      design pass before the right ramp diverter's routing logic (what a diverted shot actually
      awards/does) can be built. `plans/OutsidePerspective.md` flags "flow" (shots that feed back
      into a comboable position vs. routing to a dead stop) as the design axis worth weighing
      explicitly here, not just "what does it award" — see also the diverter→subway→multiball-lock
      idea added to `IDEAS.md`.
- [ ] `super_wizard` mode currently just awards a flat score on start — what the wizard-mode
      payoff should actually involve (a jackpot shot sequence, its own rules) is still open. See
      the jackpot-tour wizard-mode idea added to `IDEAS.md`, and `plans/OutsidePerspective.md`'s
      note on Pat Lawlor-style thematic tie-ins (mode-specific sensory changes) as what tends to
      make a payoff feel designed rather than generic.
- [ ] Lanes' "spell"/2x-hit lit-orange-blinking mechanic and the turret-gauntlet story hook are
      proposed but unconfirmed (current lane hit-feedback is a plain "hit it yet" indicator
      instead).
- [ ] Skillshot's exact rule ("any of the 3 top lanes, once per ball" is the shipped baseline) —
      a "rotate which lane counts each ball" version was proposed but never signed off. Note:
      `plans/OutsidePerspective.md` found this is MPF's own documented skillshot idiom
      (`docs/game_logic/skill_shot.md`'s worked example rotates the lit lane via the flipper
      buttons) — a known-good pattern to adopt, not a novel mechanic to design from scratch.
- [ ] Dropbank/insinerator's Companion Cube incineration story hook is inferred from the
      `s-insinerator` hardware name, not confirmed with the user. Also a genuine CAD gap: no
      drop-bank/insinerator geometry found in the Onshape document at all.
- [ ] Multiball's repeat-completion behavior: a repeat dropbank completion while a multiball is
      already active is currently a no-op (MPF's own guard) — decide if it should
      extend/restack the multiball instead. `plans/OutsidePerspective.md` notes MPF's own logic
      blocks "Common Issues" doc covers the same reset/disable-on-complete interaction one level
      down (the "my block only works once" gotcha) — same mental model, worth reading before
      deciding.

## Needs a game-balance pass

All scoring implemented this project is DRAFT placeholder values, not tuned. In particular:
bonus tally (100/shot), multiball start bonus (+3000), the 3 wizard-mode tier groupings and their
scores, portal's per-stage exit_open bonuses, dropbank's bank-completion escalation
(+500/repeat), and the sling combo window length (3s sliding).

## Follow-ups from outside MPF research (`plans/OutsidePerspective.md`)

- [ ] Add a GitHub Actions workflow running `python -m unittest discover tests` on every
      push/PR — this project has a real test suite but nothing runs it automatically.
      `deathsave/grand-prix`'s `.github/workflows/python-app.yml` is a usable template, simplified
      since this project doesn't need mpf-mc's Kivy/SDL2 system deps.
- [ ] Spike `mpf-ls` (official MPF language server — lint/autocomplete/diagnostics for MPF YAML)
      against `machinefolder/config/*.yaml` and `machinefolder/modes/*/config/*.yaml` to see what
      it flags — a candidate answer to the "no `mpf format`/lint tool exists" gap noted in
      `CHANGES.md` entry 7.
- [ ] Consider adding a single Mermaid flowchart to `design/README.md` showing how the 8 Phase 3
      features and `super_wizard` connect — `deathsave/grand-prix` keeps one in `docs/logic/
      index.md` and it's a cheap, high-value addition; that relationship currently only lives in
      scattered mode configs and `CHANGES.md` prose.
- [ ] Consider `MpfFakeGameTestCase` (overrides `start_game()`/`drain_ball()`, no ball devices
      needed) for fast, hardware-independent tests of pure rules logic — e.g. the sling combo
      window or dropbank escalation — once those are implemented, as an alternative to routing
      through the real trough-fill machinery `plans/testing-strategy.md` had to work around.
- [ ] Once physical multiball is wired and playtested for real: MPF's own "Common Issues" doc
      says a ~10s pause when adding a ball during multiball is expected — the launcher waits for
      the ball device's `eject_timeouts` config, not a playfield-switch confirm (that method
      doesn't work with >1 ball in play). Worth remembering so a slow multiball ball-add reads as
      an `eject_timeouts` tuning task, not a bug hunt.

## Manual action for the user

- [ ] Review the 1-6 statuses seeded into `tools/hw_console/data/components.yaml`'s Status tab
      (2026-09-06 migration from `planned`/`wired`/`tested`): `wired` components were seeded as
      `6`, `planned` ones as `4` — a reasonable default, not a precise per-element audit. Walk
      through each element in the Status tab and correct any that don't actually match reality.
- [ ] Review/adjust the DRAFT sound allocation in `machinefolder/sounds/sfx/` (9 files, one per
      feature + multiball, picked from the user's own Portal 2 sound extract — see `CHANGES.md`
      entry 8). `slings_hit.wav` (a generic synth blip standing in for a "springy boing" that
      doesn't exist in the pack) and `dropbank_incinerator.wav`/`lanes_turret_chirp.wav` (single
      takes picked from several near-identical alternatives) are the most likely to be worth
      swapping.
- [ ] Confirm on a real playtest (or a proper in-editor Godot check) that the `sound_player:`
      filenames actually resolve inside Godot — this wasn't independently verified (see
      `plans/testing-strategy.md`'s `GMCMedia` finding for why).
