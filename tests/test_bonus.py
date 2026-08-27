"""Regression test for the end-of-ball bonus tally (modes/bonus/config/bonus.yaml).

Run with (from the repo root, inside the .venv):
    python -m unittest discover tests
"""
import os

from mpf.tests.MpfGameTestCase import MpfGameTestCase

MACHINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "machinefolder"))


class TestBonus(MpfGameTestCase):

    def get_machine_path(self):
        return MACHINE_PATH

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def test_bonus_awards_100_per_shot_made_this_ball(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        # any top lane switch (s-toplane1/2/3) is deliberately avoided here - they're also valid
        # skillshot targets, so the first one hit counts as 2 shots made (its own lane shot +
        # shot_skillshot) which would make this test's arithmetic depend on that overlap instead
        # of just counting switches.
        self.hit_and_release_switch("s-bottomlane1")
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch("s-left-sling")
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch("s-aerial")
        self.advance_time_and_run(0.1)

        score_before_bonus = self.machine.game.player.score

        self.hit_and_release_switch("s-launch")
        self.advance_time_and_run(2)
        self.drain_all_balls()
        # the bonus mode's display_delay_ms sequence takes ~6s (3 steps x 2000ms default) before
        # the total is actually added to the player's score.
        self.advance_time_and_run(7)
        self.assertBallNumber(2)

        # 3 shots made this ball x 100 = 300 bonus.
        self.assertEqual(score_before_bonus + 300, self.machine.game.player.score)

    def test_ball_shots_made_resets_between_balls(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        # any top lane switch (s-toplane1/2/3) is deliberately avoided here - they're also valid
        # skillshot targets, so the first one hit counts as 2 shots made (its own lane shot +
        # shot_skillshot) which would make this test's arithmetic depend on that overlap instead
        # of just counting switches.
        self.hit_and_release_switch("s-bottomlane1")
        self.advance_time_and_run(0.1)

        self.hit_and_release_switch("s-launch")
        self.advance_time_and_run(2)
        self.drain_all_balls()
        self.advance_time_and_run(7)
        self.assertBallNumber(2)

        score_before_bonus = self.machine.game.player.score

        # no shots made on ball 2 - bonus should award nothing.
        self.hit_and_release_switch("s-launch")
        self.advance_time_and_run(2)
        self.drain_all_balls()
        self.advance_time_and_run(7)
        self.assertBallNumber(3)
        self.assertEqual(score_before_bonus, self.machine.game.player.score)
