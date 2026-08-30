# Changes

Numbered log of key decisions and milestones, with current status (active /
superseded-by-\<entry\> / rejected). Reconstructs *why* the project looks the way it does.

1. **Initial hardware bring-up** (Sept–Oct 2024, commits `ce51795`..`0afd57b`). Wired and
   configured the OPP `gen2` platform across 3 serial chains, mapped ~35 switches, 8 coils, and 40
   LEDs, built minimal `base`/`attract` modes with flat per-switch scoring, and play-tested on
   real hardware for 23 games (see `machinefolder/data/audits.yaml`). Flippers were never wired
   into this pass. — **Status: active**, this is the current baseline.
2. **~22-month dormancy** (Oct 2024 – Sept 2025). Only activity was an accidental commit
   (`d8e97eb`) that added a 126k-line stray log file with no real changes. — **Status:
   superseded-by-3**, project resumed.
3. **Resumption + repo hygiene** (2026-08-25). Assessed the dormant project, wrote a phased
   resumption roadmap (flippers → rules architecture → feature modes → display/audio), and did
   Phase 0 cleanup: stopped tracking `machinefolder/logs/` in git (kept existing history intact),
   added the standard project docs (`README.md`, `TODO.md`, `IDEAS.md`, this file) and a
   project-level `CLAUDE.md`. — **Status: active**.
4. **Story→shots→modes design docs, live Onshape research, and config naming cleanup**
   (2026-08-25 – 2026-08-26, commits `4b848f5`..`2ce9fd1`). Added the schema-tracked
   `design/features/*.yaml` workflow (one file per Phase 3 feature, validated by
   `tests/test_design_docs.py`) and `design/README.md`'s story→feature→shots→rules→presentation
   layer model, replacing `board Overviews.xlsx`'s "Modes" sheet as the living feature reference.
   Connected directly to the "Portal Playfield" Onshape document via `onshape-mcp` and folded
   real CAD findings into all 8 feature files (`design/research/onshape-cad-findings.md`),
   confirming aerial/ramps/portal/orbits/slings against real geometry and honestly flagging
   lanes/skillshot/dropbank's remaining gaps rather than forcing matches. Standardized every
   switch/coil/device name in `machinefolder/config/hardware-*.yaml` on hyphens (was a mix of
   underscore and hyphen), fixing the pre-existing `popbumber`/`popbumper` spelling mismatch
   along the way, verified via a clean `mpf -X -t -b` boot and a green test suite. Added
   `design/onshape-mpf-overview.md`, a single table cross-referencing every feature's Onshape
   CAD name(s) against its MPF switch/coil/LED names. — **Status: active**.
5. **Software-side gaps closed while flipper/tilt/diverter wiring stays hardware-blocked**
   (2026-08-27). With the physical cabinet unavailable, worked through every gap that's fixable
   in config/tests alone: enabled MPF's built-in `service` mode (found the installed 0.80.0
   hardcodes its nav switch names in `_get_key()`, ignoring its own `mode_settings:`
   config_spec — the `sw_service_*` switch names in `hardware-switches.yaml` are named to match
   that hardcoding, not this project's usual `s-` convention, deliberately) and `ball_search`
   (`playfields: enable_ball_search: true`); gave the sling combo a real time window via a
   `timers:` device that restarts on every hit (`logic_block_timeout` can't do this — it starts
   from mode enable, not the first hit); made dropbank's bank-completion score escalate per
   repeat within a ball; implemented portal's 5-stage `exit_open` achievement chain (both
   earlier "can't be done" findings for this were wrong — `achievements:` does default a clean
   per-stage completion event, and `achievement_group` turned out to be the wrong device type
   for a fixed chain); and electrically drafted the CAD-confirmed right ramp diverter/subway
   hardware (same draft-ahead-of-wiring pattern as the Phase 1 flippers). Root-caused a
   previously-unexplained stuck full-game test: not a bug, the test drained a ball before it was
   ever launched onto the playfield, desyncing `playfield.available_balls` and hanging every
   later `ball_starting`. See `plans/testing-strategy.md` for the reusable testing-methodology
   findings from this pass (trough-fill mismatch, plunger eject-confirm delay, etc.).
   — **Status: active**.
6. **Phase 5 stretch goals: bonus tally, multiball, tiered wizard mode** (2026-08-27), per two
   user decisions gathered mid-session: multiball's trigger ("complete a feature bank" →
   `db-dropbank`, the one Phase 3 feature that's literally a bank) and the wizard mode's shape
   (tiered mini-wizards — 3 feature tiers plus portal's own exit_open chain as the deliberate
   final required key, not one single gate). All scoring is explicitly DRAFT, and `super_wizard`
   mode implements the *gating* only, not real wizard-mode gameplay — both flagged as open
   design questions, not oversights. — **Status: active**.
7. **MPF config formatting unified on a 2-space indent** (2026-08-27). `hardware-devices.yaml`
   and `hardware-switches.yaml` were the last two files still using a 4-space step (inherited
   from before this project's Sept 2024 bring-up); reindented to match every other config/mode
   file, whitespace-only, no config values touched. No `mpf format`/lint tool exists to automate
   this (`plans/testing-strategy.md` Tier 3) — done by hand, boot-tested clean. — **Status:
   active**.
8. **Visual/audio polish pass: lane LEDs, LED shows for all 8 Phase 3 features, the multiball
   slide, and a first real-sound baseline** (2026-08-27). Drafted a 5th bottom-lane LED
   (`led-lane-b5`, a previously-unused LED chain) and wired simple hit feedback for all 8 lane
   shots; gave every Phase 3 feature a real MPF `shows:` LED flourish matching its design doc's
   described motif; built the multiball slide (user chose a dropbank fire tie-in over a
   feature-independent treatment, rendered and visually verified in Godot 4.3). Sound had been
   left untouched (no suitable assets existed) until the user located their own full Portal 2
   sound extract on this machine — picked one clip per feature from it, wired via
   `sound_player:`, explicitly as a DRAFT baseline pending the user's own listen-through and
   adjustment (tracked as an open manual action in `TODO.md`). — **Status: active**.
9. **Hardware bring-up console** (2026-08-30), ahead of starting real-hardware reconnection
   (boards first, then one component at a time). Built `tools/hw_console/` — a local Flask +
   vanilla-JS web tool tracking per-board and per-component wiring status (`planned`/`wired`/
   `tested`), a wiring checklist per component (flyback diode / common ground / same-board rule,
   from `TODO.md`'s OPP checklist), and a collision check against `hardware-switches.yaml`/
   `hardware-coils.yaml` before a new component's numbers get assigned. It's a separate tracking
   layer, not a replacement for MPF's own config — seeded from the current state of
   `hardware-*.yaml`/`TODO.md` (DRAFT items as `planned`, everything else as `wired`, reflecting
   the 23-real-games history from entry 1). `board Overviews.xlsx` is deliberately not
   auto-parsed — numbers are transcribed by hand as each component gets planned, same as before
   this tool existed. Found two real gaps while seeding it (recorded in the registry's notes, not
   fixed here): the VUK switches and the portal dropper switch have no matching eject coil
   configured anywhere. — **Status: active**.
10. **`tools/mpf-session.ps1` for running mpf from a non-interactive session** (2026-08-30),
    found while doing the first real-hardware bring-up test this laptop. Plain `mpf` (real
    hardware, full text UI) crashes immediately when run from a Claude Code tool session —
    `asciimatics` can't open a console screen buffer without a real console attached; MPF's own
    `-t` flag fixes that (confirmed working: connected cleanly to all 3 OPP chains, correctly
    read all 6 trough switches + jam as active). Separately, a backgrounded `mpf` process's PID
    as seen from a Bash/MSYS shell doesn't match its real Windows PID, so `kill` from Bash
    silently failed to find it — it was still running, undetected, until located via
    `Get-Process`/`Stop-Process` from PowerShell. `tools/mpf-session.ps1` wraps both fixes:
    always passes `-t`, tracks the real Windows PID via `Start-Process -PassThru`, and gives
    `Start`/`Stop`/`Status`/`Log` actions with log tailing and stale-state cleanup. Stop is a
    plain tracked `Stop-Process`, not a true graceful Ctrl+C — verified safe on this hardware
    (OPP boards de-energize drivers on serial disconnect, COM ports release cleanly, confirmed
    via `mpf hardware scan` immediately after a hard-stop); a true graceful shutdown was
    considered and deliberately deferred, see `TODO.md`. — **Status: active**.
