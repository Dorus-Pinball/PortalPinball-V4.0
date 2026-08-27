"""Regression test for the slings mode (per-hit scoring + sling_combo sequence).

Run with (from the repo root, inside the .venv):
    python -m unittest discover tests
"""
import os

from mpf.tests.MpfGameTestCase import MpfGameTestCase

MACHINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "machinefolder"))


class TestSlings(MpfGameTestCase):

    def get_machine_path(self):
        return MACHINE_PATH

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def test_sling_hit_scores(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_and_release_switch("s-left-sling")
        self.advance_time_and_run(0.2)
        self.assertEqual(100, self.machine.game.player.score)

    def test_sling_combo_awards_bonus(self):
        # NOTE: no time window enforced yet - see the NOT YET IMPLEMENTED comment in
        # modes/slings/config/slings.yaml. This only verifies 3 hits (either side) complete it.
        # Uses hit_and_release_switch (not hit_switch_and_run) since the same switch (left sling)
        # is hit twice - hit_switch_and_run leaves it active, so a repeat hit produces no new
        # _active event.
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_and_release_switch("s-left-sling")
        self.advance_time_and_run(0.2)
        self.hit_and_release_switch("s-right-sling")
        self.advance_time_and_run(0.2)
        self.hit_and_release_switch("s-left-sling")
        self.advance_time_and_run(0.2)
        # 3 x 100 per-hit + 750 combo bonus
        self.assertEqual(1050, self.machine.game.player.score)
