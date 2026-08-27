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
- [ ] Placeholder audio in `machinefolder/sounds/` is ripped from Left 4 Dead 2
      (`mp_coop_lobby_2_*`, `sp_a4_finale4_*`) — not licensed/final, needs replacing with real
      Portal-themed assets before any public-facing use.
- [ ] Placeholder art: both `base` and `attract` slides reuse the single `images/mainscreen.jpg`
      background — no dedicated art per mode yet.
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

## Not blocked by hardware access

- [x] All 8 `design/features/*.yaml` files (`lanes, orbits, slings, skillshot, dropbank, aerial,
      portal, ramps`) have `scoring: TBD` — needs a scoring-values pass, doesn't require the
      cabinet. Fixed: each now has DRAFT point values (clearly marked needs-review, not final
      game balance) implemented in its `modes/<name>/config/<name>.yaml`.
- [ ] The "standard pinball moments" every game needs — `ball_start`/match, `tilt_warning`,
      `ball_over`, `multiball_start`/jackpot, `game_over`, `high_score_entry` — have no owning
      design doc yet; they aren't playfield "features" in the shots/hardware sense so don't fit
      `design/features/` cleanly. Flagged in `design/SCREENS.md`'s Open items.
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
- [ ] Build real `base`/`attract` Godot slide art — still using the shared `mainscreen.jpg`
      placeholder. The bespoke feature-hit overlays cataloged in `design/SCREENS.md` are now
      implemented as placeholder colored panels (one per feature, in each mode's `slides/`
      folder) — not real art, and NOT visually verified in the Godot editor (no Godot
      executable available in this environment to check headlessly); structurally they match
      the proven `base.tscn`/`attract.tscn` format exactly (same `MPFSlide` root script,
      built-in `ColorRect`/`Label` node types only).
- [ ] Resolve `design/features/portal.yaml`'s open ball-lock hole-pairing mechanic question via
      Onshape CAD (open `balldropper`/`VUK`/`Exit`/`DropperAssy` directly) rather than on the
      physical machine.
- [ ] `modes/slings/config/slings.yaml`'s sling combo has no real time window yet - MPF's
      `logic_block_timeout` starts ticking from mode/logic-block enable (ball start), not from
      the first hit, so it can't implement "back-to-back within N seconds" as configured today.
      Needs a real "start a timer on first hit" mechanism (e.g. enable the timeout only via an
      event posted on the first sling hit) before this is a genuine time-limited combo.
- [ ] `modes/portal/config/portal.yaml`'s 5-stage "exit open" achievement_group progression
      (`led-exit-open-1..5`, the Phase 5 wizard-mode gate) is not implemented - MPF's
      `achievements:` device only posts a generic `achievement_(name)_changed_state` event by
      default, with no clean way (found so far) to chain stage N's enable off stage N-1's
      completion via plain config. Needs more research into `achievements:`/`achievement_groups:`
      before this can be built and tested properly. The core dropper->portal->exit sequence
      scoring is implemented independently of this.
- [ ] `modes/dropbank/config/dropbank.yaml`'s insinerator shot scores flat, not the "escalating
      value per repeat completion" pattern from MPF's sequential-drop-banks cookbook recipe
      referenced in `design/features/dropbank.yaml` - deferred pending a real game-balance pass.
