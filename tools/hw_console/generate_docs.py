"""Generate design/physical-checklists/wiring-guide.html, docs/wiring-guide.md, and
docs/wiring-pin-map.md from tools/hw_console/data/components.yaml +
machinefolder/config/hardware-*.yaml.

This is the project's single "docs generated from data" entrypoint - the natural place for any
future derived-doc need, not just these files (docs/references/index.md, generated from
docs/references/index.yaml, is another one - see that template). Never hand-edit the output
files below; update the source data and re-run this script instead:

    python tools/hw_console/generate_docs.py

Also fires automatically via the PostToolUse hook (post_edit_hook.py) after Claude Code edits
components.yaml or any hardware-*.yaml.

Failure mode: every output is rendered to a temp file first and only replaces the real target if
every template/harness render succeeds - a partial WireViz failure (bad connector reference,
missing Graphviz) leaves previously-committed files untouched rather than half-overwritten.
"""
import datetime
import os
import shutil
import sys
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registry

TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = registry.REPO_ROOT
TEMPLATES_DIR = TOOL_DIR / "templates"
HARNESSES_DIR = TOOL_DIR / "data" / "harnesses"
REFERENCES_INDEX_YAML = REPO_ROOT / "docs" / "references" / "index.yaml"

WIRING_GUIDE_OUT = REPO_ROOT / "design" / "physical-checklists" / "wiring-guide.html"
PIN_MAP_OUT = REPO_ROOT / "docs" / "wiring-pin-map.md"
REFERENCES_INDEX_OUT = REPO_ROOT / "docs" / "references" / "index.md"
WIRING_GUIDE_MD_OUT = REPO_ROOT / "docs" / "wiring-guide.md"
WIRING_DIAGRAMS_DIR = REPO_ROOT / "docs" / "wiring-diagrams"

STATUS_TEXT = {
    1: "1 — idea, no hardware yet",
    2: "2 — hardware, no purpose yet",
    3: "3 — hardware with a purpose, not renovated",
    4: "4 — renovated, not wired",
    5: "5 — wired, not tested",
    6: "6 — wired & tested",
}


def _badge(component):
    """Map a component's 1-6 status + notes to the wired/planned/gap badge vocabulary.

    A component counts as "gap" if its own notes flag one explicitly (missing coil, blocked
    switches, etc.) regardless of status number, else "wired" once status reaches 5 (physically
    connected, tested or not), else "planned". This mapping is what closes TODO.md's "badge
    vocabulary drifted from the 1-6 scale" item - defined once, here, instead of by hand per row.
    """
    if "GAP:" in (component.get("notes") or ""):
        return "gap"
    return "wired" if (component.get("status") or 1) >= 5 else "planned"


# CobraPin HV bank feed per coil number - docs/opp-hardware-reference.md's "Full per-pin bank /
# HV-feed / color reference" table. A coil not in any of these sets is on a red board, which has
# no wired coil yet to confirm that board family's own HV-feed convention against - _coil_other_pin
# returns None for those rather than guessing.
_COBRAPIN_BANK_A = {"0-0-0", "0-0-8", "0-0-9", "0-0-10", "0-0-11", "0-0-12", "0-0-13", "0-0-14"}
_COBRAPIN_BANK_B = {"0-0-1", "0-0-2", "0-0-3", "0-0-4", "0-0-5", "0-0-6", "0-0-7", "0-0-15"}
_COBRAPIN_BANK_C = {"1-0-0", "1-0-1", "1-0-2", "1-0-3", "1-0-4", "1-0-5", "1-0-6", "1-0-7"}


def _coil_other_pin(number):
    if number in _COBRAPIN_BANK_A:
        return "HV-A"
    if number in _COBRAPIN_BANK_B:
        return "HV-B"
    if number in _COBRAPIN_BANK_C:
        return "HV-C"
    return None


def _pin_rows(components):
    """Flatten each component's switches/coils into one row per pin, for the row-per-pin wiring
    table (docs/wiring-pin-map.md, docs/wiring-guide.md, wiring-guide.html section 04).

    Switch/coil order within a component: interleaved pairwise (switch, coil, switch, coil...)
    when the counts match - a natural per-unit pairing (e.g. left/right flipper switch+coil) -
    else every switch then every coil, since an uneven count has no obvious positional
    correspondence to fabricate (e.g. the trough's 7 switches vs. its 1 eject coil).
    """
    rows = []
    for comp in components:
        switches, coils = comp["switches"], comp["coils"]
        if switches and coils and len(switches) == len(coils):
            entries = [pair for sc in zip(switches, coils) for pair in (
                (sc[0], "Switch"), (sc[1], "Coil"))]
        else:
            entries = [(e, "Switch") for e in switches] + [(e, "Coil") for e in coils]

        for i, (e, kind) in enumerate(entries):
            other_pin = "GND" if kind == "Switch" else (_coil_other_pin(e["number"]) or "")
            rows.append({
                "component": comp["display_name"] if i == 0 else "",
                "name": e["name"],
                "type": kind,
                "board": e["board"],
                "silkscreen": e.get("silkscreen") or "",
                "other_pin": other_pin,
                "mpf": e["number"],
                "status_text": comp["status_text"] if i == 0 else "",
                "badge": comp["badge"] if i == 0 else "",
            })
    return rows


def _board_middle_index(board):
    return int(board["address"], 16) - 0x20


def _board_summary(reg):
    """Real, derivable per-board usage - no capacity/free-count claims (not reliably known
    structured data anywhere in this repo, see docs/opp-hardware-reference.md and TODO.md)."""
    switch_numbers = registry.mpf_switch_numbers()
    coil_numbers = registry.mpf_coil_numbers()
    led_numbers = registry.mpf_led_numbers()
    reserved_switches = registry.RESERVED_NUMBERS.get("switches", {})
    reserved_coils = registry.RESERVED_NUMBERS.get("coils", {})

    boards = []
    for board_id, board in (reg.get("boards") or {}).items():
        prefix = f"{board['chain']}-{_board_middle_index(board)}-"
        boards.append({
            "id": board_id,
            "display_name": board["display_name"],
            "port": board["port"],
            "role": board["role"],
            "status": board.get("status", "?"),
            "switches_used": sum(1 for n in switch_numbers if n.startswith(prefix)),
            "coils_used": sum(1 for n in coil_numbers if n.startswith(prefix)),
            "leds_used": sum(1 for n in led_numbers if n.startswith(prefix)),
            "reserved": (
                sum(1 for n in reserved_switches if n.startswith(prefix))
                + sum(1 for n in reserved_coils if n.startswith(prefix))
            ),
        })
    return boards


def _components_summary(reg):
    components = []
    for comp_id, comp in (reg.get("components") or {}).items():
        switches = comp.get("switches") or []
        coils = comp.get("coils") or []
        boards = sorted({e["board"] for e in list(switches) + list(coils)})
        status = comp.get("status") or 1
        components.append({
            "id": comp_id,
            "display_name": comp["display_name"],
            "switches": switches,
            "coils": coils,
            "boards": boards,
            "status": status,
            "status_text": STATUS_TEXT.get(status, "?"),
            "badge": _badge(comp),
        })
    return components


def _render_harnesses():
    """Render every harness YAML under data/harnesses/ to SVG via WireViz. Returns {name: svg}.

    Raises on any error (bad connector reference, missing Graphviz `dot` on PATH, etc.) rather
    than silently degrading, since generate_all()'s atomic-write wrapper is what decides whether
    a WireViz failure blocks the whole run (see its own docstring / the plan this implements).
    """
    if not HARNESSES_DIR.exists():
        return {}
    from wireviz import wireviz  # optional dependency - see README prerequisite

    svgs = {}
    for harness_path in sorted(HARNESSES_DIR.glob("*.yaml")):
        svgs[harness_path.stem] = wireviz.parse(harness_path, return_types="svg")
    return svgs


def _load_references_index():
    if not REFERENCES_INDEX_YAML.exists():
        return []
    data = registry._yaml.load(REFERENCES_INDEX_YAML.read_text(encoding="utf-8"))
    return data.get("sources") or []


def _atomic_write(path, content):
    """Write `content` to `path` atomically - a crashed/partial render never leaves `path`
    half-written. Temp file lives next to the target so os.replace stays on the same volume."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        os.replace(tmp_name, path)
    except BaseException:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise


def generate_all():
    reg = registry.load_registry()
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), keep_trailing_newline=True)
    generated_at = datetime.date.today().isoformat()

    boards = _board_summary(reg)
    components = _components_summary(reg)
    pin_rows = _pin_rows(components)
    led_numbers = registry.mpf_led_numbers()
    led_count = sum(1 for n in led_numbers if n.startswith("0-0-"))

    # Render everything into memory first - if any template/harness fails, nothing on disk
    # changes (see this module's docstring on failure mode).
    harness_svgs = _render_harnesses()

    pin_map_content = env.get_template("wiring_pin_map.md.j2").render(
        generated_at=generated_at, boards=boards, components=components, pin_rows=pin_rows,
        led_count=led_count,
    )
    wiring_guide_content = env.get_template("wiring_guide.html.j2").render(
        generated_at=generated_at, boards=boards, pin_rows=pin_rows,
        harness_svgs=harness_svgs,
    )
    # Markdown diagrams reference a real .svg file (docs/wiring-diagrams/<name>.svg), not inline
    # SVG XML - Wiki.js (and Markdown generally) serves a real image file far more reliably than
    # raw SVG passed through a Markdown renderer's HTML sanitizer.
    wiring_guide_md_content = env.get_template("wiring_guide.md.j2").render(
        generated_at=generated_at, boards=boards, pin_rows=pin_rows,
        harness_names=list(harness_svgs),
    )
    references_index_content = None
    if REFERENCES_INDEX_YAML.exists():
        references_index_content = env.get_template("references_index.md.j2").render(
            generated_at=generated_at, sources=_load_references_index(),
        )

    # Only now, with every render already succeeded, touch the real files.
    _atomic_write(PIN_MAP_OUT, pin_map_content)
    _atomic_write(WIRING_GUIDE_OUT, wiring_guide_content)
    _atomic_write(WIRING_GUIDE_MD_OUT, wiring_guide_md_content)
    for name, svg in harness_svgs.items():
        _atomic_write(WIRING_DIAGRAMS_DIR / f"{name}.svg", svg)
    if references_index_content is not None:
        _atomic_write(REFERENCES_INDEX_OUT, references_index_content)

    return {
        "wiring_guide": WIRING_GUIDE_OUT,
        "wiring_guide_md": WIRING_GUIDE_MD_OUT,
        "pin_map": PIN_MAP_OUT,
        "references_index": REFERENCES_INDEX_OUT if references_index_content is not None else None,
        "harnesses_rendered": list(harness_svgs),
    }


if __name__ == "__main__":
    result = generate_all()
    print(f"Wrote {result['pin_map']}")
    print(f"Wrote {result['wiring_guide']}")
    print(f"Wrote {result['wiring_guide_md']}")
    if result["references_index"]:
        print(f"Wrote {result['references_index']}")
    if result["harnesses_rendered"]:
        print(f"Rendered harnesses: {', '.join(result['harnesses_rendered'])}"
              f" (SVG files under {WIRING_DIAGRAMS_DIR})")
    else:
        print("No harness YAML files found under tools/hw_console/data/harnesses/")
