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
MPF_LEDS_PATH = REPO_ROOT / "machinefolder" / "config" / "hardware-leds.yaml"
MPF_DEVICES_PATH = REPO_ROOT / "machinefolder" / "config" / "hardware-devices.yaml"

# Board-family pairing rules for hardware-autofire devices (flippers, slings, pop bumpers -
# switch and coil linked as a hardware rule, not software-triggered). See
# docs/opp-hardware-reference.md for the full explanation and sources.
#
# CobraPin (chain 0 or 1): switch and coil just need the same leading chain digit.
# Red boards (chain 2+): switch and coil need the same chain AND board, and the switch must fall
# in the coil's wing's own dedicated range - a coil in wing N (numbers 4N..4N+3) pairs only with
# a switch in 8N..8N+3, not just "anywhere on the same board."
COBRA_CHAINS = (0, 1)

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


def _parse_number(number):
    """Split a 'chain-board-index' number string into an (chain, board, index) int tuple."""
    parts = str(number).split("-")
    return tuple(int(p) for p in parts)


def check_pairing(switch_number, coil_number):
    """Validate a hardware-autofire switch/coil pair against the rule for its board family.

    Returns a violation description string, or None if the pairing is valid. See
    docs/opp-hardware-reference.md for the rules this encodes.
    """
    s_chain, _s_board, s_idx = _parse_number(switch_number)
    c_chain, c_board, c_idx = _parse_number(coil_number)

    if c_chain in COBRA_CHAINS:
        if s_chain != c_chain:
            return (
                f"CobraPin same-controller rule violated: coil {coil_number} is on chain "
                f"{c_chain}, but switch {switch_number} is on chain {s_chain} - they must match"
            )
        return None

    # Red board (chain 2+): same chain and board, plus the wing-range rule.
    if s_chain != c_chain or _s_board != c_board:
        return (
            f"Red-board same-board rule violated: coil {coil_number} and switch "
            f"{switch_number} must be on the same chain and board"
        )
    wing = c_idx // 4
    lo, hi = 8 * wing, 8 * wing + 3
    if not (lo <= s_idx <= hi):
        return (
            f"Red-board wing-pairing rule violated: coil {coil_number} is in wing {wing} "
            f"(coils {4 * wing}-{4 * wing + 3}), so its switch must be numbered {lo}-{hi}, "
            f"but switch {switch_number} is index {s_idx}"
        )
    return None


def _load_yaml_top(path):
    with open(path, "r", encoding="utf-8") as f:
        return _yaml.load(f)


def find_duplicate_numbers(path):
    """Return {number: [names]} for any number used by more than one entry in an MPF hardware
    file (hardware-switches.yaml, hardware-coils.yaml, or hardware-leds.yaml)."""
    data = _load_yaml_top(path)
    top_key = next(iter(data))
    seen = {}
    for name, cfg in (data.get(top_key) or {}).items():
        if isinstance(cfg, dict) and "number" in cfg:
            seen.setdefault(str(cfg["number"]), []).append(name)
    return {number: names for number, names in seen.items() if len(names) > 1}


def autofire_pairs():
    """Return [(description, switch_name, coil_name)] for every hardware-linked switch/coil pair
    declared in hardware-devices.yaml's autofire_coils: and flippers: sections - MPF's own
    authoritative declaration of which pairs are hardware rules, not software-triggered."""
    devices = _load_yaml_top(MPF_DEVICES_PATH)
    pairs = []
    for name, cfg in (devices.get("autofire_coils") or {}).items():
        pairs.append((f"autofire_coils.{name}", cfg["switch"], cfg["coil"]))
    for name, cfg in (devices.get("flippers") or {}).items():
        pairs.append((f"flippers.{name}", cfg["activation_switch"], cfg["main_coil"]))
    return pairs


def full_scan():
    """Run every collision and pairing check across the real MPF config. Returns a list of
    violation description strings - empty if everything checks out."""
    violations = []

    for path in (MPF_SWITCHES_PATH, MPF_COILS_PATH, MPF_LEDS_PATH):
        for number, names in find_duplicate_numbers(path).items():
            violations.append(f"{path.name}: number {number} used by more than one entry: {', '.join(names)}")

    switch_numbers = mpf_switch_numbers()
    coil_numbers = mpf_coil_numbers()
    switch_by_name = {name: number for number, name in switch_numbers.items()}
    coil_by_name = {name: number for number, name in coil_numbers.items()}

    for description, switch_name, coil_name in autofire_pairs():
        switch_number = switch_by_name.get(switch_name)
        coil_number = coil_by_name.get(coil_name)
        if switch_number is None:
            violations.append(f"{description}: switch '{switch_name}' has no number in hardware-switches.yaml")
            continue
        if coil_number is None:
            violations.append(f"{description}: coil '{coil_name}' has no number in hardware-coils.yaml")
            continue
        error = check_pairing(switch_number, coil_number)
        if error:
            violations.append(f"{description}: {error}")

    return violations
