"""Regression test for the Phase 5 wizard-mode gate (tiered mini-wizards + portal + super_wizard).

Run with (from the repo root, inside the .venv):
    python -m unittest discover tests
"""
import os

from mpf.tests.MpfGameTestCase import MpfGameTestCase

MACHINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "machinefolder"))


class TestProgression(MpfGameTestCase):

    def get_machine_path(self):
        return MACHINE_PATH

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    # --- per-feature completion helpers ---

    def complete_lanes(self):
        self.hit_and_release_switch("s-toplane1")
        self.advance_time_and_run(0.05)
        self.hit_and_release_switch("s-toplane2")
        self.advance_time_and_run(0.05)
        self.hit_and_release_switch("s-toplane3")
        self.advance_time_and_run(0.05)
        for name in ("s-bottomlane1", "s-bottomlane2", "s-bottomlane3", "s-bottomlane4", "s-bottomlane5"):
            self.hit_and_release_switch(name)
            self.advance_time_and_run(0.05)

    def complete_skillshot(self):
        # only relevant if not already completed via complete_lanes()'s first hit - skillshot
        # stops itself after the first top-lane hit of the ball, so calling this after
        # complete_lanes() in the same ball is a safe no-op.
        self.hit_and_release_switch("s-toplane1")
        self.advance_time_and_run(0.05)

    def complete_sling_combo(self):
        self.hit_and_release_switch("s-left-sling")
        self.advance_time_and_run(0.2)
        self.hit_and_release_switch("s-right-sling")
        self.advance_time_and_run(0.2)
        self.hit_and_release_switch("s-left-sling")
        self.advance_time_and_run(0.2)

    def complete_orbits(self):
        for name in ("s-orbit-l", "s-orbit-r", "s-orbit-top"):
            self.hit_and_release_switch(name)
            self.advance_time_and_run(0.05)

    def complete_ramps(self):
        for name in ("s-ramp-l1", "s-ramp-r1"):
            self.hit_and_release_switch(name)
            self.advance_time_and_run(0.05)

    def complete_dropbank_finisher(self):
        self.hit_and_release_switch("s-insinerator")
        self.advance_time_and_run(0.05)
        self.hit_and_release_switch("s-button")
        self.advance_time_and_run(0.05)
        self.hit_and_release_switch("s-target-l1")
        self.advance_time_and_run(0.05)

    def complete_aerial(self):
        self.hit_and_release_switch("s-aerial")
        self.advance_time_and_run(0.05)

    def complete_portal_sequence(self):
        self.hit_and_release_switch("s-dropper")
        self.advance_time_and_run(0.05)
        self.hit_and_release_switch("s-portal-r")
        self.advance_time_and_run(0.05)
        self.hit_and_release_switch("s-exit-success")
        self.advance_time_and_run(0.05)

    def complete_all_5_portal_stages(self):
        for _ in range(5):
            self.complete_portal_sequence()

    def test_all_tiers_plus_portal_opens_wizard_gate(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.mock_event("logicblock_tier_a_complete")
        self.mock_event("logicblock_tier_b_complete")
        self.mock_event("logicblock_tier_c_complete")
        self.mock_event("portal_all_exits_open")
        self.mock_event("logicblock_wizard_gate_complete")
        self.mock_event("mode_super_wizard_started")

        self.complete_lanes()  # also completes skillshot (first top lane hit)
        self.complete_sling_combo()
        self.assertEventCalled("logicblock_tier_a_complete")

        self.complete_orbits()
        self.complete_ramps()
        self.assertEventCalled("logicblock_tier_b_complete")

        self.complete_dropbank_finisher()
        self.complete_aerial()
        self.assertEventCalled("logicblock_tier_c_complete")

        self.assertEventNotCalled("logicblock_wizard_gate_complete")

        self.complete_all_5_portal_stages()
        self.assertEventCalled("portal_all_exits_open")
        self.assertEventCalled("logicblock_wizard_gate_complete")
        self.assertEventCalled("mode_super_wizard_started")
        self.assertTrue(self.machine.mode_controller.is_active("super_wizard"))

    def test_missing_one_tier_does_not_open_wizard_gate(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.mock_event("logicblock_wizard_gate_complete")

        self.complete_lanes()
        self.complete_sling_combo()
        self.complete_orbits()
        self.complete_ramps()
        # tier C (dropbank finisher + aerial) deliberately skipped
        self.complete_all_5_portal_stages()

        self.assertEventNotCalled("logicblock_wizard_gate_complete")

    def test_tier_progress_persists_across_balls(self):
        self.fill_troughs()
        self.start_game()
        self.assertBallNumber(1)

        self.mock_event("logicblock_tier_a_complete")
        self.complete_lanes()
        self.assertEventNotCalled("logicblock_tier_a_complete")  # sling combo still missing

        self.hit_and_release_switch("s-launch")
        self.advance_time_and_run(2)
        self.drain_all_balls()
        self.advance_time_and_run(7)
        self.assertBallNumber(2)

        # finishing the tier's last requirement on a later ball should still complete it - tier
        # progress lives on the player (persist_state: true), not the mode/ball.
        self.complete_sling_combo()
        self.assertEventCalled("logicblock_tier_a_complete")
