"""Load/save the hardware bring-up registry and cross-check it against the real MPF config.

The registry (data/components.yaml) is a separate tracking layer, not a replacement for
machinefolder/config/hardware-switches.yaml / hardware-coils.yaml. Those two MPF files stay the
authoritative source for what MPF actually loads; this module only reads them to catch a
registry entry that would collide with a number already in use.
"""
from pathlib import Path

from ruamel.yaml import YAML

TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOL_DIR.parent.parent
DATA_PATH = TOOL_DIR / "data" / "components.yaml"
MPF_SWITCHES_PATH = REPO_ROOT / "machinefolder" / "config" / "hardware-switches.yaml"
MPF_COILS_PATH = REPO_ROOT / "machinefolder" / "config" / "hardware-coils.yaml"

VALID_COMPONENT_STATUSES = ("planned", "wired", "tested")
VALID_BOARD_STATUSES = ("scanned", "connected", "verified")

_yaml = YAML()
_yaml.preserve_quotes = True
_yaml.indent(mapping=2, sequence=4, offset=2)


def load_registry():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = _yaml.load(f)
    return data


def save_registry(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        _yaml.dump(data, f)


def _load_mpf_numbers(path):
    """Return {number: device_name} for every entry with a `number:` key in an MPF hardware file."""
    with open(path, "r", encoding="utf-8") as f:
        data = _yaml.load(f)
    numbers = {}
    top_key = next(iter(data))
    for name, cfg in (data.get(top_key) or {}).items():
        if isinstance(cfg, dict) and "number" in cfg:
            numbers[str(cfg["number"])] = name
    return numbers


def mpf_switch_numbers():
    return _load_mpf_numbers(MPF_SWITCHES_PATH)


def mpf_coil_numbers():
    return _load_mpf_numbers(MPF_COILS_PATH)


def _registry_numbers(registry, kind, exclude_component=None):
    """Return {number: (component_name, entry_name)} for every switch/coil already in the registry."""
    numbers = {}
    for comp_name, comp in (registry.get("components") or {}).items():
        if comp_name == exclude_component:
            continue
        for entry in comp.get(kind, []) or []:
            numbers[str(entry["number"])] = (comp_name, entry["name"])
    return numbers


def check_collision(registry, kind, number, exclude_component=None):
    """Check a proposed switch/coil number against MPF config and the rest of the registry.

    `kind` is "switches" or "coils". Returns a conflict description string, or None if free.
    """
    number = str(number)
    mpf_numbers = mpf_switch_numbers() if kind == "switches" else mpf_coil_numbers()
    if number in mpf_numbers:
        return f"{number} is already used by {mpf_numbers[number]} in hardware-{kind}.yaml"

    reg_numbers = _registry_numbers(registry, kind, exclude_component=exclude_component)
    if number in reg_numbers:
        comp_name, entry_name = reg_numbers[number]
        return f"{number} is already registered to {entry_name} on component '{comp_name}'"

    return None


def checklist_template():
    registry = load_registry()
    return [dict(item) for item in registry.get("checklist_template", [])]
