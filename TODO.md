# TODO

Rough items noticed while working, not necessarily in scope for the current task. Checked off
when fixed, not deleted, so resolution history stays visible — except where a cleanup pass has
explicitly moved that history into `CHANGES.md`/`plans/testing-strategy.md`/`design/features/*.yaml`
instead (last done 2026-08-27; see `CHANGES.md` entries 5-8 for what closed out and why, and
`plans/testing-strategy.md`'s Tier 2 addendum for the reusable MPF/testing findings from that
work).

## Blocked on physical hardware work

- [ ] **Flippers**: mechs are installed and functioning (dual-wound coils, mechanical EOS
      interrupter, no EOS switch back to the controller), but coil driver wiring to the OPP
      boards is still incomplete — the real physical task, board assignment unconfirmed against
      `board Overviews.xlsx`. Blocks real playtesting. MPF config is already drafted and
      boot/game-flow tested (`hardware-coils.yaml`/`hardware-switches.yaml`/
      `hardware-devices.yaml`, all marked DRAFT).
- [ ] **Tilt**: no tilt switch exists at all yet — needs a physical switch installed before any
      config can follow.
- [ ] **Right ramp diverter + subway**: CAD-confirmed real mechanism, electrically drafted
      (`d-ramp-diverter`, `c-ramp-diverter` coil, `s-subway-entry`/`s-subway-exit` switches, all
      DRAFT numbers) but not wired for real.
- [ ] **Service mode nav switches** (`sw_service_enter/esc/up/down`): electrically drafted, not
      wired for real.
- [ ] **Board number confirmation**: `hardware-coils.yaml` has a large commented-out block of
      unassigned numbers on the `2-1-x` chain and the Cobra `0-0-x`/`1-0-x` chains — confirm
      what's actually free vs. reserved against `board Overviews.xlsx` before any of the DRAFT
      items above get wired for real, so nothing collides.
- [ ] **Aerial upkicker** (wishlist, not scheduled): would turn the aerial plate from a
      mode-qualifying switch into a real launch mechanism. No physical coil exists there today —
      this is a "should we add hardware" decision, not "wire up what's already there."

## Needs a design decision from the user

- [ ] `board Overviews.xlsx`'s ramps notes are just "right ramp" and a bare "?" — needs a real
      design pass before the right ramp diverter's routing logic (what a diverted shot actually
      awards/does) can be built.
- [ ] `super_wizard` mode currently just awards a flat score on start — what the wizard-mode
      payoff should actually involve (a jackpot shot sequence, its own rules) is still open.
- [ ] Lanes' "spell"/2x-hit lit-orange-blinking mechanic and the turret-gauntlet story hook are
      proposed but unconfirmed (current lane hit-feedback is a plain "hit it yet" indicator
      instead).
- [ ] Skillshot's exact rule ("any of the 3 top lanes, once per ball" is the shipped baseline) —
      a "rotate which lane counts each ball" version was proposed but never signed off.
- [ ] Dropbank/insinerator's Companion Cube incineration story hook is inferred from the
      `s-insinerator` hardware name, not confirmed with the user. Also a genuine CAD gap: no
      drop-bank/insinerator geometry found in the Onshape document at all.
- [ ] Multiball's repeat-completion behavior: a repeat dropbank completion while a multiball is
      already active is currently a no-op (MPF's own guard) — decide if it should
      extend/restack the multiball instead.

## Needs a game-balance pass

All scoring implemented this project is DRAFT placeholder values, not tuned. In particular:
bonus tally (100/shot), multiball start bonus (+3000), the 3 wizard-mode tier groupings and their
scores, portal's per-stage exit_open bonuses, dropbank's bank-completion escalation
(+500/repeat), and the sling combo window length (3s sliding).

## Manual action for the user

- [ ] Review/adjust the DRAFT sound allocation in `machinefolder/sounds/sfx/` (9 files, one per
      feature + multiball, picked from the user's own Portal 2 sound extract — see `CHANGES.md`
      entry 8). `slings_hit.wav` (a generic synth blip standing in for a "springy boing" that
      doesn't exist in the pack) and `dropbank_incinerator.wav`/`lanes_turret_chirp.wav` (single
      takes picked from several near-identical alternatives) are the most likely to be worth
      swapping.
- [ ] Confirm on a real playtest (or a proper in-editor Godot check) that the `sound_player:`
      filenames actually resolve inside Godot — this wasn't independently verified (see
      `plans/testing-strategy.md`'s `GMCMedia` finding for why).
