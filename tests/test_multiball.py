"""Regression test for dropbank-triggered multiball (modes/multiball/config/multiball.yaml).

Run with (from the repo root, inside the .venv):
    python -m unittest discover tests
"""
import os

from mpf.tests.MpfGameTestCase import MpfGameTestCase

MACHINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "machinefolder"))


class TestMultiball(MpfGameTestCase):

    def get_machine_path(self):
        return MACHINE_PATH

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def fill_troughs_matching_balls_installed(self):
        # See tests/test_full_game.py's identical helper for why: MpfGameTestCase.fill_troughs()
        # activates all 7 ball_switches on bd-trough (s-trough1-6 + s-trough-jam), which conflicts
        # with hardware-basic.yaml's balls_installed: 4 and confuses the ball controller enough to
        # throw off ball-count bookkeeping - multiball needs correct trough counts to actually
        # find 2 extra balls to release.
        for name in ("s-trough1", "s-trough2", "s-trough3", "s-trough4"):
            self.hit_switch_and_run(name, 0)
        self.advance_time_and_run()

    def complete_dropbank(self):
        self.hit_switch_and_run("s-drop1", 0.1)
        self.hit_switch_and_run("s-drop2", 0.1)
        self.hit_switch_and_run("s-drop3", 0.1)

    def test_completing_dropbank_starts_3_ball_multiball(self):
        self.fill_troughs_matching_balls_installed()
        self.start_game()
        self.assertBallNumber(1)
        self.assertEqual(1, self.machine.game.balls_in_play)

        self.mock_event("multiball_mb-dropbank_started")
        self.complete_dropbank()
        self.advance_time_and_run(2)

        self.assertEventCalled("multiball_mb-dropbank_started")
        self.assertEqual(3, self.machine.game.balls_in_play)

    def test_multiball_start_scores(self):
        self.fill_troughs_matching_balls_installed()
        self.start_game()
        self.assertBallNumber(1)

        score_before = self.machine.game.player.score
        self.complete_dropbank()
        self.advance_time_and_run(2)

        # 1000 (bank completion, dropbank_completions=0) + 3000 (multiball start)
        self.assertEqual(score_before + 1000 + 3000, self.machine.game.player.score)
