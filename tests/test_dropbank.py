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
        # 1000 (bank completion) + 3000 (bank completion also starts multiball - see
        # tests/test_multiball.py, modes/multiball/config/multiball.yaml)
        self.assertEqual(4000, self.machine.game.player.score)

    def test_bank_completion_score_escalates_per_repeat(self):
        # The bank auto-resets (reset_coils: c-drop) after completion, so it can be completed
        # multiple times per ball - each repeat completion should score 500 more than the last
        # (design/features/dropbank.yaml's "escalating value per repeat completion" pattern).
        # smart_virtual doesn't simulate the physical reset knocking switches back open, so
        # release them manually between completions to simulate that.
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_switch_and_run("s-drop1", 0.1)
        self.hit_switch_and_run("s-drop2", 0.1)
        self.hit_switch_and_run("s-drop3", 0.1)
        # 1000 (bank completion) + 3000 (also starts multiball, see tests/test_multiball.py)
        self.assertEqual(4000, self.machine.game.player.score)

        self.release_switch_and_run("s-drop1", 0.1)
        self.release_switch_and_run("s-drop2", 0.1)
        self.release_switch_and_run("s-drop3", 0.1)
        self.hit_switch_and_run("s-drop1", 0.1)
        self.hit_switch_and_run("s-drop2", 0.1)
        self.hit_switch_and_run("s-drop3", 0.1)
        # 2nd completion: +1500 (1000 + 500 * 1 prior completion). No further +3000 here - the
        # multiball from the 1st completion is still active (shoot_again pending), and Multiball's
        # own start() no-ops while balls_live_target > 0, confirmed in the log (only one
        # multiball_mb-dropbank_started event across all 3 completions in this test).
        self.assertEqual(4000 + 1500, self.machine.game.player.score)

        self.release_switch_and_run("s-drop1", 0.1)
        self.release_switch_and_run("s-drop2", 0.1)
        self.release_switch_and_run("s-drop3", 0.1)
        self.hit_switch_and_run("s-drop1", 0.1)
        self.hit_switch_and_run("s-drop2", 0.1)
        self.hit_switch_and_run("s-drop3", 0.1)
        # 3rd completion: +2000 (1000 + 500 * 2 prior completions), still no further multiball.
        self.assertEqual(4000 + 1500 + 2000, self.machine.game.player.score)

    def test_insinerator_hit_scores(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_and_release_switch("s-insinerator")
        self.advance_time_and_run(0.2)
        self.assertEqual(500, self.machine.game.player.score)

    def test_insinerator_hit_show_plays(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.hit_switch_and_run("s-insinerator", 0.05)
        self.assertLightColor("led-insinerator", "red")

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
