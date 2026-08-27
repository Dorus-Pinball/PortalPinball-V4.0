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

    def test_sling_hit_show_plays(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_switch_and_run("s-left-sling", 0.04)
        self.assertLightColor("led-sling-l", "blue")

    def test_sling_combo_awards_bonus(self):
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

    def test_sling_combo_resets_if_hits_are_too_slow(self):
        # 3 sling hits still happen, but with a >3s gap between the first two - the
        # sling_combo_window timer should expire and reset progress, so hit 3 only continues a
        # fresh (1-hit) sequence rather than completing the combo.
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_and_release_switch("s-left-sling")
        self.advance_time_and_run(4)
        self.hit_and_release_switch("s-right-sling")
        self.advance_time_and_run(0.2)
        self.hit_and_release_switch("s-left-sling")
        self.advance_time_and_run(0.2)
        # 3 x 100 per-hit, no 750 combo bonus - the timeout reset progress after hit 1
        self.assertEqual(300, self.machine.game.player.score)

    def test_sling_combo_window_extends_on_each_hit(self):
        # Each hit restarts the 3s window (sliding, not a fixed deadline from the first hit) - so
        # 3 hits spaced 2.5s apart (9s total, longer than one 3s window) should still combo.
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_and_release_switch("s-left-sling")
        self.advance_time_and_run(2.5)
        self.hit_and_release_switch("s-right-sling")
        self.advance_time_and_run(2.5)
        self.hit_and_release_switch("s-left-sling")
        self.advance_time_and_run(0.2)
        self.assertEqual(1050, self.machine.game.player.score)
