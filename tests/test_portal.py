"""Regression test for the portal mode (dropper -> transfer -> exit sequence).

Run with (from the repo root, inside the .venv):
    python -m unittest discover tests
"""
import os

from mpf.tests.MpfGameTestCase import MpfGameTestCase

MACHINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "machinefolder"))


class TestPortal(MpfGameTestCase):

    def get_machine_path(self):
        return MACHINE_PATH

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def test_dropper_hit_scores(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_and_release_switch("s-dropper")
        self.advance_time_and_run(0.2)
        self.assertEqual(200, self.machine.game.player.score)

    def test_full_transfer_sequence_awards_bonus(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_and_release_switch("s-dropper")
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch("s-portal-r")
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch("s-exit-success")
        self.advance_time_and_run(0.1)
        # 200 (dropper) + 200 (portal-r) + 500 (exit-success) + 5000 (sequence complete)
        self.assertEqual(5900, self.machine.game.player.score)

    def test_out_of_order_does_not_complete(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_and_release_switch("s-exit-success")
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch("s-dropper")
        self.advance_time_and_run(0.1)
        # both shots still score their own flat per-hit points (shots are independent of the
        # sequence) - 500 (exit-success) + 200 (dropper) - but the sequence itself doesn't
        # advance from the early exit-success hit (step 2 requires value==2, still 0), so no
        # 5000 completion bonus
        self.assertEqual(700, self.machine.game.player.score)
