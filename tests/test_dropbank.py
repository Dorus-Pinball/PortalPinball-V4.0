"""Regression test for the dropbank mode (bank completion + insinerator finisher sequence).

Run with (from the repo root, inside the .venv):
    python -m unittest discover tests
"""
import os

from mpf.tests.MpfGameTestCase import MpfGameTestCase

MACHINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "machinefolder"))


class TestDropbank(MpfGameTestCase):

    def get_machine_path(self):
        return MACHINE_PATH

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def test_bank_completion_scores(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        # drop targets stay down (switch held active) until a reset coil fires - unlike a
        # momentary shot switch, so hold each one active rather than hit_and_release.
        self.hit_switch_and_run("s-drop1", 0.1)
        self.hit_switch_and_run("s-drop2", 0.1)
        self.hit_switch_and_run("s-drop3", 0.1)
        self.assertEqual(1000, self.machine.game.player.score)

    def test_insinerator_hit_scores(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_and_release_switch("s-insinerator")
        self.advance_time_and_run(0.2)
        self.assertEqual(500, self.machine.game.player.score)

    def test_insinerator_finisher_requires_order(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        # wrong order first - should NOT complete the finisher
        self.hit_and_release_switch("s-button")
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch("s-target-l1")
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch("s-insinerator")
        self.advance_time_and_run(0.1)
        # only the flat insinerator hit (500) should have scored, no 2000 finisher bonus
        self.assertEqual(500, self.machine.game.player.score)

        # correct order now completes it
        self.hit_and_release_switch("s-button")
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch("s-target-l1")
        self.advance_time_and_run(0.1)
        self.assertEqual(500 + 2000, self.machine.game.player.score)
