"""Tests for the integration's setup helpers."""

import inspect
import logging

from pytryfi import fiPet

from custom_components.fitracking import (
    _PYTRYFI_PLACE_MESSAGE,
    _drop_place_warning,
)


def _record(message):
    return logging.LogRecord("pytryfi.fiPet", logging.WARNING, __file__, 0, message, None, None)


def test_filter_drops_the_place_warning():
    assert _drop_place_warning(_record(_PYTRYFI_PLACE_MESSAGE)) is False


def test_filter_keeps_every_other_message():
    assert _drop_place_warning(_record("Could not update stats for Pet Scottie")) is True


def test_pytryfi_still_emits_the_filtered_message():
    """Guards the literal: if upstream fixes the log, the filter is dead code."""
    assert _PYTRYFI_PLACE_MESSAGE in inspect.getsource(fiPet)
