"""Regression test for service mode entry/navigation.

The installed MPF 0.80.0 service mode's config_spec advertises configurable
enter_events/esc_events/up_events/down_events (a mode_settings: section), but its actual
_get_key() implementation (mpf/modes/service/code/service.py) hardcodes the literal switch names
sw_service_enter/sw_service_esc/sw_service_up/sw_service_down instead of reading that config -
confirmed by reading the installed source directly, after a config-only override attempt had no
effect. hardware-switches.yaml's sw_service_* switches are named to match those hardcoded
literals, breaking from this project's usual `s-` convention for that reason specifically.

Run with (from the repo root, inside the .venv):
    python -m unittest discover tests
"""
import os

from mpf.tests.MpfTestCase import MpfTestCase

MACHINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "machinefolder"))


class TestService(MpfTestCase):

    def get_machine_path(self):
        return MACHINE_PATH

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def test_service_enter_switch_opens_the_menu(self):
        # The service mode itself (mode_service_*) runs continuously from early boot
        # (start_events: reset_complete) listening for a key - sw_service_enter brings up the
        # main menu (service_mode_entered) and hands control to the connected MC (Godot), which
        # drives menu navigation/exit over BCP from there (service_trigger events) - not
        # reproducible headless, so not asserted here. See mpf/modes/service/code/service.py's
        # _service_mode_main_menu()/_service_trigger() for that hand-off.
        self.assertTrue(self.machine.mode_controller.is_active("service"))
        self.mock_event("service_mode_entered")

        self.hit_and_release_switch("sw_service_enter")
        self.advance_time_and_run(0.2)
        self.assertEventCalled("service_mode_entered")

    def test_service_nav_switches_are_wired_to_the_mode(self):
        self.mock_event("service_mode_entered")
        self.mock_event("service_button")
        self.hit_and_release_switch("sw_service_enter")
        self.advance_time_and_run(0.2)
        self.assertEventCalled("service_mode_entered")

        # once inside the menu, each nav switch should register as a service_button event -
        # actually acting on it (moving the on-screen selection, exiting) is driven by the
        # connected MC (Godot) from there, not reproducible headless.
        self.hit_and_release_switch("sw_service_down")
        self.advance_time_and_run(0.2)
        self.assertEventCalledWith("service_button", button="DOWN")

        self.hit_and_release_switch("sw_service_up")
        self.advance_time_and_run(0.2)
        self.assertEventCalledWith("service_button", button="UP")

        self.hit_and_release_switch("sw_service_esc")
        self.advance_time_and_run(0.2)
        self.assertEventCalledWith("service_button", button="ESC")
