"""Regression tests for the config and options flows."""

from custom_components.fitracking import CannotConnect as BaseCannotConnect
from custom_components.fitracking.config_flow import CannotConnect, OptionsFlowHandler


def test_options_flow_does_not_override_init():
    """OptionsFlow.config_entry is read-only from HA 2024.11 (upstream issue #113)."""
    assert "__init__" not in vars(OptionsFlowHandler)


def test_cannot_connect_is_not_shadowed():
    """config_flow imported CannotConnect and then redefined it."""
    assert CannotConnect is BaseCannotConnect
