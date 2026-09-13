# Online services

Where to browse this project's data online, from any device on the home network (or the
internet, where noted) — one place to look instead of scattering pointers across
`README.md`/`CLAUDE.md`/the NAS dashboard.

| Service | URL | What it's for |
|---|---|---|
| Parts inventory (`Component_database`) | [`192.168.1.2:8091`](http://192.168.1.2:8091/) (LAN) / [`parts.famvanderlinden.nl`](https://parts.famvanderlinden.nl/) (internet) | Browse/search/filter the physical parts inventory, QR labels, CSV export. A separate sibling project, not part of this repo — linked here rather than duplicated (see `CHANGES.md` for why a Datasette mirror was considered and rejected). |
| Wiring & knowledge wiki | *not yet deployed* | Planned: a git-synced [Wiki.js](https://github.com/requarks/wiki) instance mirroring this repo's `docs/`, `design/README.md`, and root docs for browsable/searchable access from a tablet at the bench. See the KM-overhaul `CHANGES.md` entries for the design. |
| NAS service dashboard | `192.168.1.2:8093` | Index of every Docker service running on the home NAS, this project's included once the wiki above is deployed. |

This page is git-synced into the wiki above once it exists, so it's reachable from inside the
wiki itself too, not just from this repo.
