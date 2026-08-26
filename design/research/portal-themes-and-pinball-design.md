# Research: Portal 1 & 2 themes + pinball mechanism/mode design

Full findings from a research pass (2026-08-26), kept here as the backing reference for the
condensed, feature-specific points folded into `design/features/*.yaml`. If a `notes:` or
`story:` field in a feature file references "the theme research," this is that research.

This is reference material for a personal fan-built tribute machine — ideas/reference points
only, not copyrighted media.

---

## Part 1 — Portal 1 & 2: story arcs and mechanics, for animation/sound ideas

### Story arc summary

**Portal 1**: Chell wakes in a cryo-chamber inside the abandoned Aperture Science Enrichment
Center and is guided by **GLaDOS**, an AI that claims she's running a routine testing track for
"science" — 19 escalating test chambers using the Aperture Science Handheld Portal Device.
GLaDOS's dialogue is cheerful and encouraging at first, laced with deadpan threats and dangled
rewards (cake, a party) that never materialize. After Test Chamber 19, GLaDOS drops the pretense,
tries to incinerate Chell, and reveals she has already killed the facility's staff with
neurotoxin. Chell escapes through the facility's maintenance guts, fights her way into GLaDOS's
chamber, and destroys her personality cores one by one, causing GLaDOS's body to explode and drag
both of them out to the parking lot. Post-credits, a surviving fragment of GLaDOS sings "Still
Alive," revealing she's not fully destroyed.

**Portal 2**: Set years later. Chell is woken by **Wheatley**, a bumbling Personality Core who
wants her help escaping. They accidentally reboot GLaDOS, who resumes testing Chell out of spite
before Wheatley manages a "core transfer," swapping himself onto GLaDOS's body and dumping
GLaDOS's consciousness into a **potato battery** ("PotatOS"). Power-mad, Wheatley traps Chell in
dangerous test chambers and neglects the facility's failing reactors. Chell and potato-GLaDOS fall
into the **old 1950s-era Aperture facility**, hearing decades of archived PA recordings from
founder **Cave Johnson** and his assistant Caroline — recordings that reveal GLaDOS was created by
force-digitizing Caroline's mind. Chell restores GLaDOS to her body, defeats Wheatley, and GLaDOS
lets Chell go free aboveground, singing "Want You Gone" over the credits. A separate co-op
campaign has GLaDOS build two robots, **ATLAS and P-body**, to run a "Cooperative Testing
Initiative."

### Key recurring mechanics/motifs

- **Portal gun (ASHPD)** — fires linked blue and orange portals; walking through one exits the
  other instantly.
- **Momentum/flinging** — velocity is conserved through portals.
- **Weighted Storage Cube / Companion Cube** — used to hold buttons/block lasers/turrets; the
  "Companion Cube" (pink hearts) is a beloved pseudo-character GLaDOS forces you to incinerate.
- **Buttons / pressure plates** — floor switches, often held down by a cube.
- **Turrets** — small automated guns, bright red laser-sight, sweet sing-song voice, comedic
  "dying" wobble/cry when knocked over.
- **Emancipation Grill / Fizzler** — a shimmering field that destroys objects and cancels portals.
- **Aerial Faith Plate** — a springboard-like panel that launches Chell/objects ballistically.
- **Hard Light Bridge** — a solid, glowing blue energy platform/bridge.
- **Tractor Beam / Excursion Funnel** — a directional light/energy stream carrying objects along.
- **Three Gels (Portal 2)**: Propulsion (orange, frictionless speed boost), Repulsion (blue,
  bounces objects like a trampoline), Conversion (white, makes any surface portal-able).
- **Neurotoxin threat** — GLaDOS's kill-everyone fallback, PA-style countdown announcements.
- **"The cake is a lie"** — hidden graffiti warning; the game's signature "reward that never
  comes" symbol.
- **Potato battery / PotatOS** — GLaDOS reduced to a talking potato, powerless and mocked.
- **Turret Opera ("Cara Mia Addio")** — turrets sing an aria at the very end of Portal 2.
- **End-credit songs** — "Still Alive" (Portal 1) and "Want You Gone" (Portal 2).

### Animation ideas by machine structure

- **Attract**: GLaDOS eye/camera idling and "noticing" the screen; Aperture stencil/hazard-stripe
  UI framing; turret silhouettes emerging from wall panels.
- **Ball start**: portal-ring "burn open" animation for ball count; test-chamber door slide +
  chamber-number ticking up per ball.
- **Shot callouts**: portal "pop" flash per shot; cube icon bounce; button-depress thunk; turret
  pop-up-and-topple; gel splash matching color to shot type.
- **Multiball**: turret chorus, companion-cube rain, neurotoxin countdown vignette, faith-plate
  multi-launch arc.
- **Wizard mode finale**: GLaDOS chassis descending with cores detaching per sub-stage; escalating
  glitch/malfunction visuals; potato-GLaDOS loss gag; "cake is a lie" pre-victory beat; Turret
  Opera curtain call.

### Sound ideas by machine structure

- **Attract**: ambient Aperture facility hum/drone; sparse idle GLaDOS one-liners.
- **Ball start**: portal-fire whoosh (rising pitch sweep); deadpan PA-style per-ball announcement.
- **Shot callouts**: cube pickup/drop clunk-chime; button thunk+hiss; turret chirp/death-cry;
  gel-specific sounds (propulsion=zip, repulsion=boing, conversion=shimmer chime).
- **Multiball**: neurotoxin-alarm klaxon + PA evacuation-style announcement (repurposed as
  celebratory); overlapping turret voice snippets.
- **Wizard mode finale**: escalating GLaDOS dialogue barks; pitch-shifted "downgrade" loss gag; an
  *original* short motif evoking "Still Alive"/"Want You Gone" (not the copyrighted recordings);
  Turret Opera vocal flourish; fire/alarm-into-triumphant-PA mode-clear sting.
- **General callout style**: model all short game-event callouts (jackpot, extra ball, mode-start)
  on the deadpan, formally-worded Aperture-PA-announcer voice — flat corporate phrasing undercutting
  dramatic events, which is the games' signature comedic tone and translates well to pinball's need
  for short, distinct, repeatable callouts.

### Notable prior art

A real licensed **Multimorphic "Portal" pinball machine (2025)** exists, with an actual
**Aerial Faith Plate** mechanism, a "Momentum Jump Ramp," a companion-cube ball lock, a rotating
sentry turret, and RGB physical portals. Useful as prior art for how professionals solved this
exact translation problem — this build stays a distinct fan tribute, not a copy of their specific
implementation.

---

## Part 2 — Pinball design: mechanisms and mode patterns

### Common physical shot mechanisms not currently on this machine

| Mechanism | What it does |
|---|---|
| Spinner | Free-swinging vane, scores per rotation as the ball passes through |
| Captive ball | Trapped ball struck (not collected) repeatedly by the live ball |
| Subway/tunnel | Under-playfield channel, gravity-fed, entry/exit switches, no coil |
| VUK / scoop | Ball drops in, held briefly, then kicked back out — classic mode-start/lock trigger |
| Diverter | Solenoid/servo flap routing a ball between two paths at a fork |
| Magnet | Grabs/holds/redirects/flings a moving ball |
| Kickback | Fires a ball back into play from an outlane |
| Physical ball lock | Holds balls out of play until multiball release |
| Bash toy | A themed sculpt that reacts (spins/opens/lights) when struck |
| Mini-playfield | A secondary smaller playfield with its own flippers/targets |
| One-way gate | Passive wire gate preventing backward drain through orbits |

### Common mode/rule design patterns

- **Skill shot**: plunger-timing shot into a specific lane; **super skill shot** escalates it
  immediately after, only reachable from a completed base skill shot.
- **Mode qualifying vs. stacking**: qualify (light) and start (shoot) can be decoupled; modern
  machines let 2+ modes run concurrently for a stacking bonus.
- **Multiball**: lock N balls → release together; **add-a-ball** during multiball; **jackpot →
  super jackpot** escalation; **multiball restart** as a comeback mechanic.
- **Wizard modes** (MPF models this via `achievement_group`): gated by completing a defined set of
  features. Two dominant shapes — one big end-of-game wizard mode (linear), or several
  parallel mini-wizard modes feeding one final "super" wizard mode (tiered, e.g. JJP's Pirates of
  the Caribbean).
- **Combos**: chained shots within a time window, naturally an MPF `sequence` block.
- **Mystery/random award**: a dedicated shot granting a weighted random pick.
- **Extra ball**: earned via milestone, capped per game.
- **Ball save**: timed post-launch/post-multiball-start drain refund window.
- **Bonus multiplier**: built by spelling a word or repeat shots, applied once at ball-end.

### Applied ideas for this machine's undesigned/thin features

- **Aerial plate**: confirmed real mechanism (see Multimorphic prior art above). Switch-only now
  → use as a mode-qualifying step. If a coil is ever added → VUK-style upkicker feeding a
  ramp/lock, the standard real-machine use for this exact mechanism type.
- **Ramps** (2 switches, no diverter in this hardware): most likely entry+exit confirmation, not
  routing. Strongest fit: pair L/R into a `sequence` for ramp-to-ramp combos, or a repeat-ramp
  bonus-multiplier build. If a diverter/servo is ever added, standard use is alternating
  left/right routing to feed a physical ball lock.
- **Drop bank → insinerator**: textbook "bank completion unlocks a shot" pattern — MPF has a
  cookbook recipe for exactly this
  (`missionpinball.org/latest/cookbook/sequential_drop_banks/`), using a `sequence` block.
  Standard shape: escalating value per repeat completion (bank auto-resets via `c-drop`).
- **Wizard-mode structure**: wrap each of the 8 Phase 3 features in its own `achievement`, put all
  8 in one `achievement_group` — MPF fires the "all complete" event automatically, no custom event
  chain needed. Real machines pick one of the two dominant shapes deliberately (see above) — this
  is a genuine design fork worth deciding explicitly before Phase 5, not defaulting silently.
- **Skill shot**: current plunger-lane design already matches the standard pattern. Cheap
  additions: a super-skill-shot bonus window, and rotating which lane counts each ball
  (round-robin across the 3 top lanes already wired).

### Sources

Portal research: Combine OverWiki (Portal/Portal 2 storyline pages), Wikipedia (GLaDOS, Wheatley,
"The cake is a lie"), Portal Wiki (Turret Opera, Gels, Still Alive, GLaDOS, Mechanics, Aperture
Science Announcement System, Neurotoxin, List of Portal chambers, Multimorphic Portal Pinball
Machine), Valve Developer Community (Gel), Kineticist and TechEBlog (Multimorphic Portal pinball
coverage), Goodreads/GameSkinny (Cave Johnson quotes).

Pinball design research: missionpinball.org docs (scoops, diverters, wizard modes, achievement
groups, sequential drop target banks cookbook, feature list), Grokipedia and Kineticist (pinball
terms glossaries), Pinball FX Wiki (wizard mode, skill shot), TV Tropes (Wizard Mode, Score
Multiplier, Pirates of the Caribbean), Pinside forum (ramp diverter logic discussion), Pinball
Fandom (Jersey Jack Pinball), Pinball Castle (pop bumper mechanism).
