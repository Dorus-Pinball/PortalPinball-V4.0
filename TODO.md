# TODO

Rough items noticed while working, not necessarily in scope for the current task. Checked off
when fixed, not deleted, so resolution history stays visible.

- [ ] Flippers: mechs are installed and functioning (dual-wound coils, mechanical/self-contained
      EOS interrupter, no EOS switch back to the controller), but coil driver wiring to the OPP
      boards is still incomplete (real physical task, board assignment unconfirmed against
      `board Overviews.xlsx`) - blocks real playtesting. The MPF `flippers:` config itself is now
      drafted and boot/game-flow tested against `smart_virtual`
      (`hardware-coils.yaml`/`hardware-switches.yaml`/`hardware-devices.yaml`, all marked DRAFT).
      Real finding along the way: the roadmap's original assumption that no hold config is
      needed (mechanical EOS handles it invisibly) was wrong at the MPF-config level - the
      flipper device always builds a pulse+hold hardware rule and asserts if `hold_power` is
      0.0, even with no `hold_coil`/`eos_switch`. Fixed with `default_hold_power: 1.0` on each
      flipper coil (correct here specifically because this hardware's hold winding shares the
      same activation signal as the power winding - no separate PWM-reduced hold path for the
      controller to under-power). See the coil comments for the full explanation.
- [ ] Tilt is not configured at all — no tilt switch present in `hardware-switches.yaml`.
- [x] `config.yaml`'s `modes:` list references `orbit` and `lanes` (commented out) but neither
      mode folder exists yet under `machinefolder/modes/`. Fixed: all 8 Phase 3 feature modes
      (`lanes, orbits, slings, skillshot, dropbank, aerial, portal, ramps`) are now implemented
      and listed. See the "Not blocked by hardware access" section below for what's still
      draft/deferred within each.
- [ ] `hardware-coils.yaml` has a large commented-out block of unassigned coil numbers on the
      `2-1-x` chain and the Cobra `0-0-x`/`1-0-x` chains — worth confirming what's actually free
      vs. reserved before assigning new features (e.g. flippers) to specific numbers.
- [x] Placeholder audio in `machinefolder/sounds/` is ripped from Left 4 Dead 2
      (`mp_coop_lobby_2_*`, `sp_a4_finale4_*`) — not licensed/final. **Accepted as a keeper
      (2026-08-27)**: same licensing category as `mainscreen.jpg` below, and the user confirmed
      reuse is fine for this private, non-commercial project. No longer "needs replacing" unless
      the project's status changes (e.g. any public-facing use).
- [x] Placeholder art: both `base` and `attract` slides reuse the single `images/mainscreen.jpg`
      background. **Resolved (2026-08-27)**: the 8 feature-hit overlays now have dedicated
      original art (see the graphics item below); `base`/`attract` deliberately kept
      `mainscreen.jpg` instead of dedicated art — same accepted-keeper reasoning as the audio
      above.
- [ ] `board Overviews.xlsx` "Modes" sheet has several under-specified feature notes (e.g. the
      ramps section is just "right ramp" and a bare "?") that need a design pass with the user
      before they can be implemented.
- [ ] Hardware wishlist, not blocking, no phase assigned: `design/features/aerial.yaml` notes that
      the "aerial plate" (`s-aerial`) is a confirmed reference to Portal 2's Aerial Faith Plate,
      and that adding an upkicker coil there (currently switch-only) would let it work as a
      real launch mechanism instead of just a mode-qualifying switch. See
      `design/research/portal-themes-and-pinball-design.md`.
- [ ] Right ramp diverter + subway: confirmed by CAD (`Diverter_Rod`, `Diverter_Base`,
      `Bridge_Diverter_Cover`, `Subway` — see `design/research/onshape-cad-findings.md`) to be a
      real physical mechanism feeding the right ramp, but it has no electrical wiring yet — no
      diverter coil or subway entry/exit switches exist in `hardware-coils.yaml`/
      `hardware-switches.yaml`. Needs board assignment before `design/features/ramps.yaml` can be
      implemented with real diverter logic (same kind of gate as Phase 1 flippers).
- [x] Repo hygiene: `machinefolder/logs/` was tracked in git (158 files) with no `.gitignore`
      entry, and a stray 126,607-line log file had been accidentally committed. Logs are now
      gitignored and untracked going forward (existing git history left intact).
- [x] The local MPF install was completely broken (`mpf.exe` on PATH was a 0-byte stub, `pip show
      mpf` found nothing) — no form of `mpf`, virtual or real hardware, actually worked. Fixed via
      `install.ps1` (`.venv` + `mpf==0.80.0`). See `plans/testing-strategy.md`.
- [x] Corrected two things doc research got wrong for the actually-installed MPF 0.80.0 (both
      found by running the real thing, not just reading about it): `mpf test` requires
      `kivy`/legacy `mpf-mc` and fails without it — use `python -m unittest discover tests`
      instead; there is no `mpf format`/lint command in 0.80.0 at all — a clean `mpf -X -t -b` boot
      is the fast config-validation check instead. Full detail in `plans/testing-strategy.md`.

- [x] **Service mode was never enabled** - MPF ships a built-in `service` mode
      (`mpf/modes/service/code/service.py`) but it wasn't in `config.yaml`'s `modes:` list, so it
      never ran. **Fixed (2026-08-27)**: added `service` to `modes:`. Real finding along the way:
      the installed MPF 0.80.0 service mode's config_spec advertises configurable
      `enter_events`/`esc_events`/`up_events`/`down_events`/`door_opened_events`/
      `door_closed_events` (a `mode_settings:` section), but the actual `_get_key()`
      implementation hardcodes the literal switch names `sw_service_enter`/`sw_service_esc`/
      `sw_service_up`/`sw_service_down` instead of ever reading that config, and
      `door_opened_events`/`door_closed_events` aren't consumed anywhere in the code at all in
      this version (real entry is the enter switch, not a door-open event) - confirmed by reading
      the installed source after a config-only override attempt had no effect. Added DRAFT
      `sw_service_enter/esc/up/down` switches to `hardware-switches.yaml` (named against this
      project's usual `s-` convention for that reason specifically - numbers are placeholders
      pending real board assignment, same status as the Phase 1 flipper switches). The mpf-gmc
      addon already ships a default `service.tscn` slide (`addons/mpf-gmc/slides/service.tscn`),
      so no Godot-side work was needed. Verified with 2 new tests in `tests/test_service.py`:
      entering the menu posts `service_mode_entered`, and each nav switch posts the
      `service_button` event a connected MC (Godot) would act on - full menu navigation/exit is
      driven by the MC over BCP from there and isn't reproducible in a headless test.
- [x] Ball search is not configured anywhere - a real gap, not previously flagged: without it, a
      ball stuck on a switchless part of the playfield stalls the machine instead of
      self-recovering. **Fixed (2026-08-27)**: added `enable_ball_search: true` to the
      `playfields: playfield:` device in `hardware-devices.yaml`, using MPF's stock timing (15s
      idle, 3 escalating search phases). `autofire_coils` (popbumpers, slings) and
      `drop_target_banks` register for ball search unconditionally - no `include_in_ball_search`
      toggle exists for those device types in MPF's `config_spec.yaml` (confirmed by reading it
      directly) - so no other per-device config was needed. Flippers keep MPF's own default
      (`include_in_ball_search: false`) since a repeatedly-pulsing flipper rarely helps free a
      ball stuck elsewhere on the field. Verified with 2 new tests in `tests/test_ball_search.py`:
      one confirms `ball_search_started` fires after 15s of no playfield switch activity once a
      ball is in play, one confirms hitting a playfield switch (sling) postpones it rather than
      just delaying it once. Real finding along the way: `bd-plunger`'s eject onto the
      (switchless, from its own perspective) playfield has no confirming switch, so
      `confirm_eject_type: target` falls back to its ~10s default eject timeout before
      `playfield.balls` actually updates - worth remembering for any future test that checks
      playfield ball count right after a launch.

## Not blocked by hardware access

- [x] All 8 `design/features/*.yaml` files (`lanes, orbits, slings, skillshot, dropbank, aerial,
      portal, ramps`) have `scoring: TBD` — needs a scoring-values pass, doesn't require the
      cabinet. Fixed: each now has DRAFT point values (clearly marked needs-review, not final
      game balance) implemented in its `modes/<name>/config/<name>.yaml`.
- [x] The "standard pinball moments" every game needs — `ball_start`/match, `tilt_warning`,
      `ball_over`, `multiball_start`/jackpot, `game_over`, `high_score_entry` — have no owning
      design doc yet; they aren't playfield "features" in the shots/hardware sense so don't fit
      `design/features/` cleanly. Fixed: see `design/GAME_MOMENTS.md` — most turned out to be
      MPF built-in modes (`match`, `high_score`) needing only `config.yaml` registration (now
      done); `tilt_warning` and `multiball_start` remain genuinely blocked (hardware / open
      design fork respectively), not just undesigned.
- [x] Could not fully verify `match`/`high_score` trigger correctly at a real game-over in an
      automated test — draining a full 3-ball game via `smart_virtual` in a scratch test got
      stuck after ball 1 (ball 2 never advanced past `bd-plunger` across repeated
      `drain_all_balls()` + `hit_and_release_switch("s-launch")` calls, for reasons not yet
      root-caused; possibly `mechanical_eject`/`player_controlled_eject_event` interaction with
      the test harness rather than a real bug). Boot is clean and the existing 24-test suite
      (all single-ball scenarios) still passes with both modes active. Needs follow-up before
      trusting `match`/`high_score` behavior beyond "loads without erroring." **Root-caused and
      fixed (2026-08-27)**: not a real bug - the scratch test called `drain_all_balls()`
      immediately after `start_game()`, before ball 1 was ever launched onto the playfield.
      Since `bd-plunger` uses `mechanical_eject` (the player must hit `s-launch` - MPF doesn't
      auto-plunge), ball 1 was still parked in the plunger lane; draining "it" desyncs
      `playfield.available_balls`, and every later `ball_starting` hangs forever in MPF's
      `BallController.wait_until_playfields_are_empty()` (confirmed via
      `machine.playfields["playfield"].balls`/`available_balls` and the repeating "Playfields
      still contain balls" log line - reading `mpf/modes/game/code/game.py` and
      `mpf/core/ball_controller.py` directly pinpointed the wait). Launching each ball before
      draining it (the same order a real player experiences) fixes it completely. Also found
      along the way: `MpfGameTestCase.fill_troughs()` activates *every* `ball_switch` configured
      on a trough device (7 here: `s-trough1-6` + `s-trough-jam`, a trough capacity larger than
      `balls_installed: 4` - normal for the real cabinet), which conflicts with
      `balls_installed: 4` and inflates the ball controller's known-ball count; a full-game test
      needs a trimmed fill matching `hardware-basic.yaml`'s
      `virtual_platform_start_active_switches` instead. New passing test:
      `tests/test_full_game.py::test_full_3ball_game_reaches_game_over` - drains all 3 balls in
      order and asserts the game actually ends (`match`/`high_score` run as part of teardown,
      confirmed clean in the log: `match_no_match`, `mode_high_score_started/stopped`, no
      errors).
- [x] Build out the 8 designed-but-unimplemented feature modes (`lanes, orbits, slings,
      skillshot, dropbank, aerial, portal, ramps`) against `smart_virtual` — see
      `plans/resumption-roadmap.md` Phase 3 and each feature's Rules layer in
      `design/features/*.yaml`. Done: all 8 implemented, boot-tested clean, and covered by a
      passing `tests/test_<name>.py` each (24 tests total). Two design-doc device-type choices
      were corrected along the way (`accrual` -> `sequences` for dropbank/portal's ordered
      finishers - accruals complete in any order, verified against MPF's own
      `logic_blocks.py`). Several nuances deliberately deferred rather than shipped unverified -
      see the new items below.
- [x] Draft/validate the `flippers:` MPF config skeleton against `smart_virtual` — the real
      coil-driver wiring is hardware-blocked (see the flippers item above), but the config
      itself can be written and boot-tested virtually first. Done - see the flippers item above
      for a real bug this surfaced (hold_power can't be 0.0) and its fix.
- [x] Build real `base`/`attract` Godot slide art, plus the bespoke feature-hit overlays
      cataloged in `design/SCREENS.md`. Fixed: all 10 slides now carry original vector
      iconography (an aperture-iris mark for `attract`, a lit terminal frame for `base`, and a
      distinct line-art icon per feature tying back to its `presentation.show` motif) on a
      dark, per-feature-tinted background, replacing the shared `mainscreen.jpg` and the flat
      `ColorRect` placeholders. Proposal reviewed and approved first as a published Artifact
      ("Aperture Display Signage") before touching any `.tscn` file — see that artifact for the
      full palette/rationale per screen. `images/mainscreen.jpg` is no longer referenced by any
      slide but was left in place, not deleted.
      **Now visually verified**: found Godot 4.3 actually installed on this machine
      (`C:\Program Files (x86)\Godot\`), so all 10 slides were rendered for real (headless
      `--script` capture, real Vulkan rendering — `--headless` alone forces a null/dummy
      renderer and produces blank textures, worth remembering next time) and reviewed as
      screenshots. Caught one real bug this way: the dropbank drop-target rectangles, built as
      closed-loop `Line2D` shapes, rendered as broken glyph-like boxes (a triangulation edge
      case for an axis-aligned closed rectangle) — fixed by switching to plain `ColorRect`
      nodes. The other 9 slides matched the approved proposal on the first render. `base.tscn`'s
      score readout doesn't show in an isolated screenshot since there's no live MPF game
      supplying the `score` player variable in that test — expected, not a bug.
      **Follow-up (2026-08-27)**: `attract`/`base` had their original `mainscreen.jpg` background
      restored in place of the new aperture-iris/terminal-frame icon treatment — the user
      specifically liked that image's moody atmosphere and, after being flagged that it reads as
      Portal-themed fan art (same licensing category as the placeholder audio), confirmed reuse
      is fine for this private, non-commercial project. The 8 feature-hit overlays keep their
      new original icons (unaffected, never used `mainscreen.jpg`). Title/score `Label` color
      accents (blue/orange) were kept over the restored image.
- [x] Resolve `design/features/portal.yaml`'s open ball-lock hole-pairing mechanic question via
      Onshape CAD (open `balldropper`/`VUK`/`Exit`/`DropperAssy` directly) rather than on the
      physical machine. Resolved: the CAD does NOT support hole-pairing - `VUK`/`VUK high`/
      `Exit` are unused orphaned stub part studios never instanced in the real assembly; the
      built machine has exactly one `DropperAssy` feeding a single linear path to one `Portal
      Vuk` exit, no second capture point or coordinating linkage anywhere. This validates the
      already-implemented `sequences:`-based portal mode (a strictly ordered single path) rather
      than requiring a rework. See `design/research/onshape-cad-findings.md`.
- [x] `modes/slings/config/slings.yaml`'s sling combo has no real time window yet - MPF's
      `logic_block_timeout` starts ticking from mode/logic-block enable (ball start), not from
      the first hit, so it can't implement "back-to-back within N seconds" as configured today.
      Needs a real "start a timer on first hit" mechanism (e.g. enable the timeout only via an
      event posted on the first sling hit) before this is a genuine time-limited combo. **Fixed
      (2026-08-27)**: added a `timers:` device (`sling_combo_window`, 3s, direction up) that
      `restart()`s on every sling hit - `restart()` starts the timer if not already running, so
      the first hit both arms the window and registers as sequence step 0, no separate "arm"
      event needed - and resets the sequence's progress via `reset_events` if the timer ever
      completes (3+ seconds with no further hit). This is a sliding window (extends on each hit)
      rather than a fixed deadline from the first hit. Verified with 2 new tests in
      `tests/test_slings.py`: one confirming a slow gap resets progress, one confirming the
      window correctly extends across hits spaced up to 2.5s apart.
- [x] `modes/portal/config/portal.yaml`'s 5-stage "exit open" achievement_group progression
      (`led-exit-open-1..5`, the Phase 5 wizard-mode gate) is not implemented - MPF's
      `achievements:` device only posts a generic `achievement_(name)_changed_state` event by
      default, with no clean way (found so far) to chain stage N's enable off stage N-1's
      completion via plain config. Needs more research into `achievements:`/`achievement_groups:`
      before this can be built and tested properly. The core dropper->portal->exit sequence
      scoring is implemented independently of this. **Fixed (2026-08-27)**: both earlier findings
      were wrong on re-verification against the installed source. `achievements:` DOES default
      `events_when_completed` to a clean `achievement_<name>_state_completed` event - the earlier
      pass only checked the generic `changed_state` event. And `achievement_group` turned out to
      be the wrong device type entirely (built for player-selectable "pick one" mechanics, not a
      fixed linear chain) - used 5 plain `achievements:` chained by their own default completion
      events instead, see `design/features/portal.yaml` for the full corrected reasoning. Real bug
      found and fixed along the way: `disable_on_complete` defaults to `true` for every
      `logic_block` (`counters`/`accruals`/`sequences`) - `portal_sequence` needed
      `disable_on_complete: false` explicitly or it would only ever complete once per ball,
      capping the chain at stage 1 forever. Verified with 2 new tests in `tests/test_portal.py`.
- [x] `modes/dropbank/config/dropbank.yaml`'s insinerator shot scores flat, not the "escalating
      value per repeat completion" pattern from MPF's sequential-drop-banks cookbook recipe
      referenced in `design/features/dropbank.yaml` - deferred pending a real game-balance pass.
      **Fixed (2026-08-27)**: the *bank-completion* award (not the insinerator shot itself, which
      stays flat - the design note was about the bank) now escalates +500 per repeat completion
      within a ball, via a plain `dropbank_completions` player var read into the score template
      (`1000 + 500 * current_player.dropbank_completions`) and incremented after. Values are still
      DRAFT pending a real balance pass. Verified with a new test in `tests/test_dropbank.py`
      covering 3 repeat completions (1000/1500/2000).
