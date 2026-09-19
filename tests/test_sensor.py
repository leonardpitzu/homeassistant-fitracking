"""Tests for the Fi Tracking sensor platform."""

import pytest
from homeassistant.components.sensor import SensorStateClass

from custom_components.fitracking.const import (
    SENSOR_STATS_BY_TIME,
    SENSOR_STATS_BY_TYPE,
)
from custom_components.fitracking.sensor import STAT_META, PetBehaviorSensor

# Stat attribute names pytryfi exposes on a pet object.
PYTRYFI_STAT_ATTRS = {
    "dailySteps",
    "weeklySteps",
    "monthlySteps",
    "dailyTotalDistance",
    "weeklyTotalDistance",
    "monthlyTotalDistance",
    "dailySleep",
    "weeklySleep",
    "monthlySleep",
    "dailyNap",
    "weeklyNap",
    "monthlyNap",
    "dailyGoal",
    "weeklyGoal",
    "monthlyGoal",
}


def test_every_stat_type_has_metadata():
    assert set(SENSOR_STATS_BY_TYPE) == set(STAT_META)


def test_goal_is_exposed():
    """Upstream shipped a TODO comment instead of the goal sensors."""
    assert "GOAL" in SENSOR_STATS_BY_TYPE


@pytest.mark.parametrize("stat_type", SENSOR_STATS_BY_TYPE)
@pytest.mark.parametrize("stat_time", SENSOR_STATS_BY_TIME)
def test_attribute_name_resolves(stat_type, stat_time):
    """Every stat/period pair must address a real pytryfi attribute."""
    attr = f"{stat_time.lower()}{STAT_META[stat_type]['attr']}"
    assert attr in PYTRYFI_STAT_ATTRS


def test_all_pytryfi_stats_are_covered():
    built = {
        f"{stat_time.lower()}{STAT_META[stat_type]['attr']}"
        for stat_type in SENSOR_STATS_BY_TYPE
        for stat_time in SENSOR_STATS_BY_TIME
    }
    assert built == PYTRYFI_STAT_ATTRS


@pytest.mark.parametrize(
    ("stat_type", "raw", "expected"),
    [
        ("STEPS", 12049, 12049),
        ("GOAL", 12000, 12000),
        ("DISTANCE", 1430, 1.43),  # metres -> km
        ("SLEEP", 5454, 90.9),  # seconds -> minutes
        ("NAP", 3441, 57.35),
    ],
)
def test_unit_scaling(stat_type, raw, expected):
    meta = STAT_META[stat_type]
    value = raw if meta["divisor"] == 1 else round(raw / meta["divisor"], 2)
    assert value == expected


def test_icons_are_distinct():
    """Upstream returned mdi:map-marker-distance for every stat, sleep included."""
    icons = [meta["icon"] for meta in STAT_META.values()]
    assert len(icons) == len(set(icons))


def test_every_stat_reports_a_state_class():
    """Without a state class there are no long-term statistics."""
    assert all(meta["state_class"] is not None for meta in STAT_META.values())


def test_no_sensor_is_a_counter():
    """Fi revises these downward after first reporting them.

    HA's reset tolerance is relative, so a small absolute revision early in a
    period is a large enough drop to read as a counter reset and inflate the sum.
    """
    state_classes = [meta["state_class"] for meta in STAT_META.values()]
    # HA's entity metaclass turns _attr_state_class into a descriptor, so the
    # value only resolves through the public property on an instance.
    state_classes.append(object.__new__(PetBehaviorSensor).state_class)
    assert all(state_class is SensorStateClass.MEASUREMENT for state_class in state_classes)
