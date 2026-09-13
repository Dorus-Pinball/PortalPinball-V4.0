# Portal Pinball Wiki (Wiki.js) — NAS deployment

A git-synced [Wiki.js](https://github.com/requarks/wiki) instance mirroring this repo's `docs/`,
`design/README.md`, `design/features/`, and root `README.md`/`TODO.md`/`IDEAS.md`/`CHANGES.md`
into a browsable, searchable, always-on site reachable from any device on the home network — see
the km-overhaul `CHANGES.md` entries for the full design rationale (Postgres backend, the
`wiki-sync` branch, why Datasette/BookStack/Obsidian weren't used instead).

## Status

**Containers deployed and running** (2026-09-13): `docker compose up -d` on
`weather-reader-nas:/volume1/docker/portal-pinball-wikijs/`, reachable at
`http://192.168.1.2:8095/` (confirmed from a separate LAN device, not just the NAS itself), added
to `nas-dashboard`. `CREATE EXTENSION pg_trgm;` already run against the `wikijs` Postgres
database.

**Still needs manual completion** — none of these can be scripted from a Claude Code session:

1. **Wiki.js's first-run setup wizard** — open `http://192.168.1.2:8095/` in a browser, create
   the admin account. Wiki.js has no headless/API bootstrap for this in the stable release.
2. **Configure the Git storage module** (Admin → Storage → add a Git target):
   - Repository URL: `git@github.com:Dorus-Pinball/PortalPinball-V4.0.git`
   - Branch: `wiki-sync` (not `main` — see `CHANGES.md`/`.github/workflows/sync-wiki-branch.yml`
     for why).
   - Sync mode: two-way (push local edits back to `wiki-sync`, pull `main`'s ongoing work via the
     `sync-wiki-branch.yml` Action that keeps `wiki-sync` fed).
   - Path scope: `README.md`, `TODO.md`, `IDEAS.md`, `CHANGES.md`, `docs/`, `design/README.md`,
     `design/features/`.
   - SSH deploy key: a dedicated keypair was generated for this
     (`portal-pinball-wikijs-deploy`, ed25519) — **the public half still needs adding to the
     GitHub repo as a deploy key with write access** (blocked by the permission system as a new
     persistent credential grant, needs explicit authorization — see the session's own note to
     Dorus). The private half needs pasting into this Git storage module's SSH key field.
3. **Search Engine** (Admin → Search): select "DB - PostgreSQL", pick a dictionary language,
   Apply, then **Rebuild Index**.
4. **DSM Reverse Proxy** (only if/when public internet access is wanted, mirroring
   `Component_database`'s `parts.famvanderlinden.nl` pattern) — Control Panel → Login/Application
   Portal → Advanced → Reverse Proxy, a manual GUI-only step per DSM's own design (not driveable
   over SSH). Not required for LAN-only use, which is the default scope here.

## Files

- `docker-compose.yml` — Postgres (`wikijs-db`) + Wiki.js (`wikijs`), port `8095`.
- `.env.example` — copy to `.env` on the NAS (gitignored there, not committed), same convention
  as `Component_database`/`nas-dashboard`.

## Redeploying after a compose-file change

No git/rsync on this NAS — push via tar over SSH, same pattern as the sibling projects:

```bash
tar -czf - docker-compose.yml | ssh weather-reader-nas "tar -xzf - -C /volume1/docker/portal-pinball-wikijs"
ssh weather-reader-nas "cd /volume1/docker/portal-pinball-wikijs && \
  sudo /var/packages/ContainerManager/target/usr/bin/docker compose up -d"
```

Two gotchas already hit deploying this (see `Component_database`/`nas-dashboard` for the same):
bind-mounted data directories need to exist and be `chmod 777` before first start (containers run
as a different uid than the host), and Docker Compose on this NAS is invoked as
`sudo /var/packages/ContainerManager/target/usr/bin/docker compose`, not a bare `docker compose`.
