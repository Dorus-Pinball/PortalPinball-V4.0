"""Regression test for ball search (hardware-devices.yaml's playfields: enable_ball_search: true).

Run with (from the repo root, inside the .venv):
    python -m unittest discover tests
"""
import os

from mpf.tests.MpfGameTestCase import MpfGameTestCase

MACHINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "machinefolder"))


class TestBallSearch(MpfGameTestCase):

    def get_machine_path(self):
        return MACHINE_PATH

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def fill_troughs_matching_balls_installed(self):
        # See tests/test_full_game.py's identical helper for why: MpfGameTestCase.fill_troughs()
        # activates all 7 ball_switches on bd-trough (s-trough1-6 + s-trough-jam), which conflicts
        # with hardware-basic.yaml's balls_installed: 4 and confuses the ball controller's
        # bookkeeping enough to throw off playfield ball-count confirmation timing.
        for name in ("s-trough1", "s-trough2", "s-trough3", "s-trough4"):
            self.hit_switch_and_run(name, 0)
        self.advance_time_and_run()

    def test_ball_search_starts_after_idle_timeout(self):
        self.fill_troughs_matching_balls_installed()
        self.start_game()
        self.assertBallNumber(1)

        # get the ball out of the plunger and onto the playfield (mechanical_eject - the mode
        # doesn't auto-plunge), then leave it alone. bd-plunger has no switch confirming arrival
        # on the (switchless, from its perspective) playfield, so confirm_eject_type: target
        # falls back to its ~10s default eject timeout before playfield.balls actually updates -
        # confirmed in the debug log (eject fires at t=2.001, "Exited eject mode. Eject success:
        # True" only at t=12.101).
        self.hit_and_release_switch("s-launch")
        self.advance_time_and_run(13)
        self.assertEqual(1, self.machine.playfields["playfield"].balls)

        self.mock_event("ball_search_started")
        self.assertEventNotCalled("ball_search_started")

        # default ball_search_timeout is 15s of no playfield switch activity.
        self.advance_time_and_run(16)
        self.assertEventCalled("ball_search_started")

    def test_playfield_switch_activity_resets_the_idle_timer(self):
        self.fill_troughs_matching_balls_installed()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_and_release_switch("s-launch")
        self.advance_time_and_run(13)
        self.assertEqual(1, self.machine.playfields["playfield"].balls)

        self.mock_event("ball_search_started")

        # hit a playfield switch comfortably inside the 15s idle window, twice, to prove
        # activity keeps postponing the timeout rather than just delaying it once.
        self.advance_time_and_run(10)
        self.hit_and_release_switch("s-left-sling")
        self.advance_time_and_run(10)
        self.hit_and_release_switch("s-right-sling")
        self.advance_time_and_run(10)
        self.assertEventNotCalled("ball_search_started")

        # now let it go idle past the timeout for real.
        self.advance_time_and_run(6)
        self.assertEventCalled("ball_search_started")
