"""Validate design/features/*.yaml against design/schema/feature.schema.json,
and cross-check every shot reference against the real hardware config.

Run with (from the repo root, inside the .venv):
    python -m unittest discover tests

No MPF machine involved here at all - this is pure document validation, so it
runs even faster than tests/test_bringup.py.
"""
import json
import os
import unittest

import jsonschema
from ruamel.yaml import YAML

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DESIGN_DIR = os.path.join(REPO_ROOT, "design")
FEATURES_DIR = os.path.join(DESIGN_DIR, "features")
SCHEMA_PATH = os.path.join(DESIGN_DIR, "schema", "feature.schema.json")
HARDWARE_CONFIG_DIR = os.path.join(REPO_ROOT, "machinefolder", "config")

_yaml = YAML(typ="safe")


def _load_yaml(path):
    with open(path, encoding="utf-8") as handle:
        return _yaml.load(handle)


def _feature_files():
    return sorted(
        name for name in os.listdir(FEATURES_DIR)
        if name.endswith(".yaml") and not name.startswith("_")
    )


def _known_hardware_names():
    """Collect every switch/coil/light name defined in hardware-*.yaml."""
    names = set()
    sections = {
        "hardware-switches.yaml": "switches",
        "hardware-coils.yaml": "coils",
        "hardware-leds.yaml": "lights",
    }
    for filename, top_key in sections.items():
        config = _load_yaml(os.path.join(HARDWARE_CONFIG_DIR, filename))
        names.update((config.get(top_key) or {}).keys())
    return names


class TestDesignDocs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            cls.schema = json.load(handle)
        cls.validator = jsonschema.Draft202012Validator(cls.schema)
        cls.known_hardware = _known_hardware_names()

    def test_schema_itself_is_valid(self):
        jsonschema.Draft202012Validator.check_schema(self.schema)

    def test_template_fails_validation(self):
        # Proves the schema is actually enforcing something, not decorative:
        # the template only sets `id`, so it must fail on the other required fields.
        template = _load_yaml(os.path.join(FEATURES_DIR, "_template.yaml"))
        errors = list(self.validator.iter_errors(template))
        self.assertTrue(errors, "Expected _template.yaml to fail validation, but it passed.")

    def test_all_feature_files_are_valid(self):
        for filename in _feature_files():
            with self.subTest(filename=filename):
                doc = _load_yaml(os.path.join(FEATURES_DIR, filename))
                errors = list(self.validator.iter_errors(doc))
                self.assertEqual(
                    [], [error.message for error in errors],
                    "{} failed schema validation".format(filename),
                )

    def test_feature_id_matches_filename(self):
        for filename in _feature_files():
            with self.subTest(filename=filename):
                doc = _load_yaml(os.path.join(FEATURES_DIR, filename))
                expected_id = os.path.splitext(filename)[0]
                self.assertEqual(expected_id, doc.get("id"))

    def test_shot_refs_point_at_real_hardware(self):
        for filename in _feature_files():
            doc = _load_yaml(os.path.join(FEATURES_DIR, filename))
            for shot in doc.get("shots", []):
                ref = shot.get("ref")
                with self.subTest(filename=filename, ref=ref):
                    self.assertIn(
                        ref, self.known_hardware,
                        "{} references '{}', which is not defined in any hardware-*.yaml".format(
                            filename, ref),
                    )


if __name__ == "__main__":
    unittest.main()
