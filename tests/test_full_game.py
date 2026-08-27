"""Regression test for a full 3-ball single-player game, draining ball by ball to game_over.

Root-causes and closes the TODO.md item that flagged this as "stuck after ball 1, not yet
root-caused". It was never a bug in this project's config: the machine uses `mechanical_eject`
on bd-plunger (the player must hit s-launch - MPF doesn't auto-plunge), so a ball sits in the
plunger lane, not on the playfield, until launched. The earlier investigation's scratch test
called `drain_all_balls()` right after `start_game()`, before ever launching ball 1 - that
desyncs `playfield.available_balls` (a phantom ball gets drained while the real one is still
parked in the plunger), and every later `ball_starting` then hangs forever in MPF's
`BallController.wait_until_playfields_are_empty()` (logged as repeating "Playfields still
contain balls. Waiting for those to drain." with no game progress). Launching each ball onto the
playfield before draining it - the same order a real player experiences - fixes it completely.

Run with (from the repo root, inside the .venv):
    python -m unittest discover tests
"""
import os

from mpf.tests.MpfGameTestCase import MpfGameTestCase

MACHINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "machinefolder"))


class TestFullGame(MpfGameTestCase):

    def get_machine_path(self):
        return MACHINE_PATH

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def fill_troughs_matching_balls_installed(self):
        # hardware-basic.yaml sets balls_installed: 4 and
        # virtual_platform_start_active_switches: s-trough1..4 (only 4 real balls on the physical
        # machine). The stock MpfGameTestCase.fill_troughs() helper instead activates EVERY
        # ball_switch configured on any device tagged "trough" - for bd-trough that's 7
        # (s-trough1-6 + s-trough-jam, a trough capacity larger than balls actually installed,
        # normal for the real cabinet) - which conflicts with balls_installed: 4 and confuses the
        # ball controller (it logs "Found a new ball which was captured from playfield" and
        # inflates its known-ball count past what the machine actually has). Mirror the real
        # virtual-platform startup state instead for any test that runs a full multi-ball-drain
        # game, where getting the starting ball count right matters.
        for name in ("s-trough1", "s-trough2", "s-trough3", "s-trough4"):
            self.hit_switch_and_run(name, 0)
        self.advance_time_and_run()

    def launch_and_drain_ball(self):
        self.hit_and_release_switch("s-launch")
        self.advance_time_and_run(2)
        self.drain_all_balls()
        self.advance_time_and_run(2)

    def test_full_3ball_game_reaches_game_over(self):
        self.fill_troughs_matching_balls_installed()
        self.start_game()
        self.assertBallNumber(1)
        self.assertEqual(1, self.machine.game.balls_in_play)

        self.launch_and_drain_ball()
        self.assertGameIsRunning()
        self.assertBallNumber(2)
        self.assertEqual(1, self.machine.game.balls_in_play)

        self.launch_and_drain_ball()
        self.assertGameIsRunning()
        self.assertBallNumber(3)
        self.assertEqual(1, self.machine.game.balls_in_play)

        # draining ball 3 of a single-player 3-ball game should end the game (match/high_score
        # run as part of game teardown - both are in config.yaml's modes: list).
        self.hit_and_release_switch("s-launch")
        self.advance_time_and_run(2)
        self.drain_all_balls()
        self.advance_time_and_run(3)
        self.assertGameIsNotRunning()
