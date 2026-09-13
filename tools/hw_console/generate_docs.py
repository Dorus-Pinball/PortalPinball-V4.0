"""Generate design/physical-checklists/wiring-guide.html and docs/wiring-pin-map.md from
tools/hw_console/data/components.yaml + machinefolder/config/hardware-*.yaml.

This is the project's single "docs generated from data" entrypoint - the natural place for any
future derived-doc need, not just these two files (docs/references/index.md, generated from
docs/references/index.yaml, is the next one - see that template). Never hand-edit the output
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


def _pin_str(entries):
    if not entries:
        return "—"
    return ", ".join(f"{e['name']} {e['number']}" for e in entries)


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
            "switches_str": _pin_str(switches),
            "coils_str": _pin_str(coils),
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
    led_numbers = registry.mpf_led_numbers()
    led_count = sum(1 for n in led_numbers if n.startswith("0-0-"))

    # Render everything into memory first - if any template/harness fails, nothing on disk
    # changes (see this module's docstring on failure mode).
    harness_svgs = _render_harnesses()

    pin_map_content = env.get_template("wiring_pin_map.md.j2").render(
        generated_at=generated_at, boards=boards, components=components, led_count=led_count,
    )
    wiring_guide_content = env.get_template("wiring_guide.html.j2").render(
        generated_at=generated_at, boards=boards, components=components,
        harness_svgs=harness_svgs,
    )
    references_index_content = None
    if REFERENCES_INDEX_YAML.exists():
        references_index_content = env.get_template("references_index.md.j2").render(
            generated_at=generated_at, sources=_load_references_index(),
        )

    # Only now, with every render already succeeded, touch the real files.
    _atomic_write(PIN_MAP_OUT, pin_map_content)
    _atomic_write(WIRING_GUIDE_OUT, wiring_guide_content)
    if references_index_content is not None:
        _atomic_write(REFERENCES_INDEX_OUT, references_index_content)

    return {
        "wiring_guide": WIRING_GUIDE_OUT,
        "pin_map": PIN_MAP_OUT,
        "references_index": REFERENCES_INDEX_OUT if references_index_content is not None else None,
        "harnesses_rendered": list(harness_svgs),
    }


if __name__ == "__main__":
    result = generate_all()
    print(f"Wrote {result['pin_map']}")
    print(f"Wrote {result['wiring_guide']}")
    if result["references_index"]:
        print(f"Wrote {result['references_index']}")
    if result["harnesses_rendered"]:
        print(f"Rendered harnesses: {', '.join(result['harnesses_rendered'])}")
    else:
        print("No harness YAML files found under tools/hw_console/data/harnesses/")
