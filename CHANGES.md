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
