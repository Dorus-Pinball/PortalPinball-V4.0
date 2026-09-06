# TODO

Rough items noticed while working, not necessarily in scope for the current task. Checked off
when fixed, not deleted, so resolution history stays visible — except where a cleanup pass has
explicitly moved that history into `CHANGES.md`/`plans/testing-strategy.md`/`design/features/*.yaml`
instead (last done 2026-08-27; see `CHANGES.md` entries 5-8 for what closed out and why, and
`plans/testing-strategy.md`'s Tier 2 addendum for the reusable MPF/testing findings from that
work).

## Blocked on physical hardware work

- [x] **Flippers**: mechs are installed and functioning (dual-wound coils, mechanical EOS
      interrupter, no EOS switch back to the controller). Routed via the **Cobra board** (chain
      0, board `0x20`) instead of the PSOC chain, so the flipper switch and coil share a physical
      STM32 board per CobraPin's same-board guidance for timing-critical devices —
      `c-flipper-left/right` on `0-0-8`/`0-0-9` (both Bank A, HV_A brown — the actual pins used
      for real physical wiring, 2026-09-06, superseding an earlier `0-0-2`/`0-0-3` guess read off
      `board Overviews.xlsx`), `s-left/right-flipper` on `0-0-1`/`0-0-2` (also the actual pins
      used for real physical wiring, 2026-09-06, superseding an earlier `0-0-9`/`0-0-10` guess).
      See `design/physical-checklists/wiring-guide.html` for the visual reference. **Wiring
      confirmed 2026-09-06** via `tools/wiring_test.py`: both switches PASS (open→closed→open),
      both coils PASS (activation LED with 50V off, then real mechanical travel with 50V on),
      and confirmed live in a real game (`ball_started` enables the `flippers:` device; held
      correctly on physical button press/release). Remaining open item: `default_pulse_ms: 25`
      in `hardware-coils.yaml` was too weak for real travel with HV on (`pulse_ms: 200` worked in
      testing) — real tuning still needed, see the "Needs a design decision" flipper pulse entry
      below.
- [x] **Start/launch switches**: wired onto the same Cobra chain 0 board (0x20) as the flippers
      during the 2026-09-06 session (moved from the earlier DRAFT `2-0-17`/`2-0-18` PSOC-chain
      placeholders). `s-launch` on `0-0-3` PASSED first try (OPEN→CLOSED→OPEN). `s-start` was
      first wired to `0-0-8` and read stuck CLOSED regardless of press/release (suspected: that
      channel had been reassigned to servo/PWM use on the board itself, per the user, rather than
      a wiring fault) — moved to `0-0-27` (confirmed free/valid on that board's input card) and
      **PASSED** (OPEN→CLOSED→OPEN). Both confirmed live via `bcp_step.py` (same BCP mechanism as
      `tools/wiring_test.py`). Along the way, hit a real USB-serial incident: all 3 OPP boards'
      COM ports (COM4/5/6) dropped into `Status: Unknown` in Device Manager after a mid-session
      `ClearCommError` on COM5 (same signature as the earlier flipper-bringup USB-suspend issue,
      but this time all 3 chains wedged, not just one — the earlier `powercfg` selective-suspend
      fix didn't fully prevent it) — recovered only by physically unplugging/replugging the USB
      cables at the PC end (a board-side reseat alone did not clear it; a software PnP
      disable/enable also failed, needs admin elevation this session doesn't have). Worth
      revisiting the USB power-management fix if this recurs.
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
- [ ] **Board number confirmation**: `hardware-coils.yaml` has a large commented-out block of
      unassigned numbers on the `2-1-x` chain and the Cobra `0-0-x`/`1-0-x` chains — confirm
      what's actually free vs. reserved against `board Overviews.xlsx` before any of the DRAFT
      items above get wired for real, so nothing collides. Now tracked live in
      `tools/hw_console/`'s registry (per-board/per-component status, collision check against
      `hardware-*.yaml`) rather than only here.
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

## Dev tooling

- [ ] **`wiring-guide.html` status vocabulary out of sync**: `tools/hw_console`'s Status tab
      (2026-09-06) replaced `components.yaml`'s `planned`/`wired`/`tested` status with a 1-6
      build-lifecycle scale (`registry.COMPONENT_STATUSES`), but
      `design/physical-checklists/wiring-guide.html`'s "04 Known components" table still uses the
      old `wired`/`planned`/`gap` badge vocabulary — it's a hand-maintained static document with
      no generator script, so it wasn't rewritten as part of that change. Re-label its status
      badges to match next time it's touched for a real wiring pass.
- [ ] **True graceful Ctrl+C shutdown for `tools/mpf-session.ps1`**: current `-Action Stop` is a
      tracked `Stop-Process` (hard-stop), not a real SIGINT to MPF's own signal handler —
      deliberately deferred in favor of simplicity, since a hard-stop was verified safe on this
      hardware (OPP boards de-energize drivers on serial disconnect, COM ports release cleanly).
      A true graceful stop would need a small Win32 helper (`AttachConsole`/
      `GenerateConsoleCtrlEvent`) to deliver a real CTRL_C to the child process. Revisit only if
      MPF's own clean-shutdown logic (e.g. flushing something mid-write) ever actually matters
      for a session.
- [x] **`tools/wiring_test.py` added** (2026-09-06): no-HV switch continuity + LED-based coil
      check, reusing MPF's own service-mode BCP commands. See `plans/wiring-test-tool.md`.
- [ ] **Windows USB selective suspend caused a live serial disconnect** (found 2026-09-06): an
      idle OPP COM port (Cobra board, USB-serial CDC) threw `ClearCommError failed ... device
      does not recognize the command` after ~70s idle, crashing the running `mpf` session — a
      classic USB-selective-suspend-on-idle symptom, unrelated to any coil pulse (it happened
      well after the last one). Fixed by disabling USB selective suspend (AC + battery) on this
      laptop's active power plan via `powercfg` (subgroup `2a737441-1930-4402-8d77-b2bebba308a3`,
      setting `48e6b7a6-50f5-4782-a5d4-53bb8f07e226`, both set to `0`/Disabled). Not a repo-level
      fix — would need reapplying if this laptop is reimaged or the power plan gets reset.

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
