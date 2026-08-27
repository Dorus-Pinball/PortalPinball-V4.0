"""Regression test for the orbits mode (left/right/top orbit shot_group).

Run with (from the repo root, inside the .venv):
    python -m unittest discover tests
"""
import os

from mpf.tests.MpfGameTestCase import MpfGameTestCase

MACHINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "machinefolder"))


class TestOrbits(MpfGameTestCase):

    def get_machine_path(self):
        return MACHINE_PATH

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def test_orbit_hit_scores(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_switch_and_run("s-orbit-l", 1)
        self.assertEqual(750, self.machine.game.player.score)

    def test_orbits_group_complete_awards_bonus(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_switch_and_run("s-orbit-l", 0.1)
        self.hit_switch_and_run("s-orbit-r", 0.1)
        self.hit_switch_and_run("s-orbit-top", 0.1)
        # 750 + 750 + 100 per-shot + 3000 group-complete bonus
        self.assertEqual(4600, self.machine.game.player.score)

    def test_orbit_hit_show_uses_the_right_color_per_side(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        # show step 1 (white) lasts 0.1s before settling into the per-side color.
        self.hit_switch_and_run("s-orbit-l", 0.15)
        self.assertLightColor("led-orbit-l", "blue")

        self.hit_switch_and_run("s-orbit-r", 0.15)
        self.assertLightColor("led-orbit-r", "orange")
