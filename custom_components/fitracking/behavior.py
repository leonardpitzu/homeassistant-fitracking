"""Per-behaviour event trends, which pytryfi does not implement.

Fi serves these from getPetHealthTrendsForPet. Only the DAY period carries data;
WEEK and MONTH return empty intervals until there is enough history.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from homeassistant.util import dt as dt_util
from pytryfi.common import query

LOGGER = logging.getLogger(__name__)

# Built by concatenation: the query body is full of GraphQL braces.
_QUERY_HEAD = 'query { getPetHealthTrendsForPet(petId: "'
_QUERY_TAIL = (
    '", period: DAY) { behaviorTrends { id title '
    "chart { ... on PetHealthTrendSegmentedTimeline { "
    "intervals { intervalType offset } } } } } }"
)


def fetch_behavior_events(session, pet_id: str) -> dict[str, list[datetime]]:
    """Return {behaviour key: event times} for today in local time.

    Offsets are seconds since local midnight. An EVENT's `length` is a fixed
    render width (always 700s) and events can overlap, so it is not a duration
    and is deliberately not requested.
    """
    response = query.query(session, _QUERY_HEAD + pet_id + _QUERY_TAIL)
    trends = (response.get("data") or {}).get("getPetHealthTrendsForPet") or {}
    midnight = dt_util.start_of_local_day()

    events: dict[str, list[datetime]] = {}
    for trend in trends.get("behaviorTrends") or []:
        key = str(trend.get("id") or "").split(":")[0]
        if not key:
            continue
        intervals = (trend.get("chart") or {}).get("intervals") or []
        events[key] = [
            midnight + timedelta(seconds=interval["offset"])
            for interval in intervals
            if interval.get("intervalType") == "EVENT"
            and interval.get("offset") is not None
        ]
    return events
