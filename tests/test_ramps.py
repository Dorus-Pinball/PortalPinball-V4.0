"""Regression test for the ramps mode (shot_group + ramp_combo sequence).

Run with (from the repo root, inside the .venv):
    python -m unittest discover tests
"""
import os

from mpf.tests.MpfGameTestCase import MpfGameTestCase

MACHINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "machinefolder"))


class TestRamps(MpfGameTestCase):

    def get_machine_path(self):
        return MACHINE_PATH

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def test_ramp_hit_scores(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_and_release_switch("s-ramp-l1")
        self.advance_time_and_run(0.2)
        self.assertEqual(400, self.machine.game.player.score)

    def test_ramps_group_complete_awards_bonus(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_and_release_switch("s-ramp-l1")
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch("s-ramp-r1")
        self.advance_time_and_run(0.1)
        # 400 + 400 per-shot + 1500 group-complete bonus + 1000 combo-complete bonus
        # (2 ramp hits back to back also completes the 2-step ramp_combo sequence)
        self.assertEqual(3300, self.machine.game.player.score)
