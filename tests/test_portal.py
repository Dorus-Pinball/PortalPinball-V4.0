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

    def complete_portal_sequence(self):
        self.hit_and_release_switch("s-dropper")
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch("s-portal-r")
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch("s-exit-success")
        self.advance_time_and_run(0.1)

    def test_full_transfer_sequence_awards_bonus(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.complete_portal_sequence()
        # 200 (dropper) + 200 (portal-r) + 500 (exit-success) + 5000 (sequence complete)
        # + 1000 (1st exit-open stage, chained off the same sequence completion)
        self.assertEqual(6900, self.machine.game.player.score)

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

    def test_five_repeat_completions_light_all_five_exit_open_stages(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.mock_event("achievement_exit_open_1_state_completed")
        self.mock_event("achievement_exit_open_2_state_completed")
        self.mock_event("achievement_exit_open_3_state_completed")
        self.mock_event("achievement_exit_open_4_state_completed")
        self.mock_event("portal_all_exits_open")

        self.complete_portal_sequence()
        self.assertEventCalled("achievement_exit_open_1_state_completed")
        self.assertEventNotCalled("achievement_exit_open_2_state_completed")

        self.complete_portal_sequence()
        self.assertEventCalled("achievement_exit_open_2_state_completed")
        self.assertEventNotCalled("achievement_exit_open_3_state_completed")

        self.complete_portal_sequence()
        self.assertEventCalled("achievement_exit_open_3_state_completed")
        self.assertEventNotCalled("achievement_exit_open_4_state_completed")

        self.complete_portal_sequence()
        self.assertEventCalled("achievement_exit_open_4_state_completed")
        self.assertEventNotCalled("portal_all_exits_open")

        self.complete_portal_sequence()
        self.assertEventCalled("portal_all_exits_open")

        # a 6th completion should just score the base sequence bonus again - no 6th stage exists,
        # so no further per-stage bonus, and nothing should error.
        score_before = self.machine.game.player.score
        self.complete_portal_sequence()
        self.assertEqual(score_before + 200 + 200 + 500 + 5000, self.machine.game.player.score)

    def test_exit_open_progress_persists_across_balls(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.mock_event("achievement_exit_open_2_state_completed")
        self.complete_portal_sequence()  # stage 1
        self.assertEventNotCalled("achievement_exit_open_2_state_completed")

        # ball must actually reach the playfield before draining it (bd-plunger uses
        # mechanical_eject) - see tests/test_full_game.py for why skipping this hangs the next
        # ball_starting forever.
        self.hit_and_release_switch("s-launch")
        self.advance_time_and_run(2)
        self.drain_all_balls()
        # the bonus mode (ball_ending) now gates the next ball_starting behind ~6s of its own
        # display_delay_ms sequence - see tests/test_full_game.py's launch_and_drain_ball().
        self.advance_time_and_run(7)
        self.assertBallNumber(2)

        # stage 2 should still be reachable on ball 2 - a fresh completion continues the chain
        # rather than restarting it, since achievement state lives on the player, not the mode.
        self.complete_portal_sequence()
        self.assertEventCalled("achievement_exit_open_2_state_completed")
