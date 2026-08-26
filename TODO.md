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
- [ ] Hardware wishlist, not blocking, no phase assigned: `design/features/aerial.yaml` notes that
      the "aerial plate" (`s-aerial`) is a confirmed reference to Portal 2's Aerial Faith Plate,
      and that adding an upkicker coil there (currently switch-only) would let it work as a
      real launch mechanism instead of just a mode-qualifying switch. See
      `design/research/portal-themes-and-pinball-design.md`.
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
