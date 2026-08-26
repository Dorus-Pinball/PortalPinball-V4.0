"""Regression test for the lanes mode (top/bottom lane shots + shot_groups).

Run with (from the repo root, inside the .venv):
    python -m unittest discover tests
"""
import os

from mpf.tests.MpfGameTestCase import MpfGameTestCase

MACHINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "machinefolder"))


class TestLanes(MpfGameTestCase):

    def get_machine_path(self):
        return MACHINE_PATH

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def _consume_skillshot(self):
        # modes/skillshot also owns the 3 top lane switches (one-per-ball bonus) - hit and
        # release one first so these tests' assertions are decoupled from its score value.
        self.hit_and_release_switch("s-toplane3")
        self.advance_time_and_run(0.2)
        return self.machine.game.player.score

    def test_top_lane_hit_scores(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)
        baseline = self._consume_skillshot()

        self.hit_switch_and_run("s-toplane1", 1)
        self.assertEqual(baseline + 500, self.machine.game.player.score)

    def test_bottom_lane_hit_scores(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_switch_and_run("s-bottomlane1", 1)
        self.assertEqual(250, self.machine.game.player.score)

    def test_top_lanes_group_complete_awards_bonus(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)
        baseline = self._consume_skillshot()

        self.hit_switch_and_run("s-toplane1", 0.1)
        self.hit_switch_and_run("s-toplane2", 0.1)
        self.hit_switch_and_run("s-toplane3", 0.1)
        # 3 x 500 per-shot + 2500 group-complete bonus
        self.assertEqual(baseline + 4000, self.machine.game.player.score)
