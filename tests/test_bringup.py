"""Baseline regression test: game start + trough/ball routing + basic scoring.

Run with (from the repo root, inside the .venv):
    python -m unittest discover tests

This exercises the real machinefolder/ config against MPF's smart_virtual
platform - no cabinet, no keyboard, no Godot display required. It's the
harness sanity check: if this fails, something is wrong with the test setup
itself, not necessarily the game logic.
"""
import os

from mpf.tests.MpfGameTestCase import MpfGameTestCase

MACHINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "machinefolder"))


class TestBringup(MpfGameTestCase):

    def get_machine_path(self):
        return MACHINE_PATH

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def test_game_starts_and_scores(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_switch_and_run("s_toplane1", 1)
        self.assertEqual(100, self.machine.game.player.score)
