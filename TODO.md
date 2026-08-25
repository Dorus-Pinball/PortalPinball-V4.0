# TODO

Rough items noticed while working, not necessarily in scope for the current task. Checked off
when fixed, not deleted, so resolution history stays visible.

- [ ] Flippers: mechs are installed and functioning (dual-wound coils, mechanical/self-contained
      EOS interrupter, no EOS switch back to the controller), but coil driver wiring to the OPP
      boards and the MPF `flippers:` config are still incomplete. Blocks real playtesting.
- [ ] Tilt is not configured at all — no tilt switch present in `hardware-switches.yaml`.
- [ ] `config.yaml`'s `modes:` list references `orbit` and `lanes` (commented out) but neither
      mode folder exists yet under `machinefolder/modes/`.
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
- [x] Repo hygiene: `machinefolder/logs/` was tracked in git (158 files) with no `.gitignore`
      entry, and a stray 126,607-line log file had been accidentally committed. Logs are now
      gitignored and untracked going forward (existing git history left intact).
