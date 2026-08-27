"""Regression test for the skillshot mode (any top lane, once per ball).

Run with (from the repo root, inside the .venv):
    python -m unittest discover tests
"""
import os

from mpf.tests.MpfGameTestCase import MpfGameTestCase

MACHINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "machinefolder"))


class TestSkillshot(MpfGameTestCase):

    def get_machine_path(self):
        return MACHINE_PATH

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def test_top_lane_hit_scores_skillshot(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_and_release_switch("s-toplane2")
        self.advance_time_and_run(0.2)
        # 1000 skillshot bonus + 500 lanes per-hit (lanes mode also owns this switch)
        self.assertEqual(1500, self.machine.game.player.score)

    def test_skillshot_only_counts_once_per_ball(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_and_release_switch("s-toplane1")
        self.advance_time_and_run(0.2)
        score_after_first = self.machine.game.player.score

        self.hit_and_release_switch("s-toplane2")
        self.advance_time_and_run(0.2)
        # skillshot mode should have stopped itself - only lanes' 500 per-hit should land,
        # no second 1000 skillshot bonus
        self.assertEqual(score_after_first + 500, self.machine.game.player.score)

    def test_skillshot_hit_show_plays_despite_mode_stopping_on_same_event(self):
        # mode: stop_events: shot_skillshot_hit stops this mode on the very same event that
        # triggers its own show_player entry - confirms the show still gets to play (MPF
        # processes the show_player handler before/independent of the mode-stop teardown) rather
        # than being silently skipped by a race.
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_switch_and_run("s-toplane3", 0.05)
        self.assertLightColor("led-toplane3", "white")
