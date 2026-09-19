# Fi Tracking for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A custom [Home Assistant](https://www.home-assistant.io/) integration for [Fi](https://fitracking.com/) smart GPS dog collars — live location, activity and rest tracking, collar light control and Lost Dog mode.

> Personal fork of [sbabcock23/hass-tryfi](https://github.com/sbabcock23/hass-tryfi), renamed to follow Fi's rebrand from `tryfi.com` to `fitracking.com`. See [Differences from upstream](#differences-from-upstream).

## Features

### Device tracker

A `device_tracker` entity per pet, fed by the collar's reported GPS fix, so the pet appears on the map and can back a `person` entity.

### Sensors

Activity and rest statistics are created for every combination of period (`daily`, `weekly`, `monthly`) and metric:

| Metric | Unit | Device class | State class |
|---|---|---|---|
| Steps | `steps` | – | `total_increasing` |
| Distance | `km` | `distance` | `total_increasing` |
| Sleep | `min` | `duration` | `measurement` |
| Nap | `min` | `duration` | `measurement` |
| Goal | `steps` | – | `measurement` |

Sleep and nap are `measurement` rather than `total_increasing` because Fi
reclassifies rest between the two after the fact, so the value can drop mid-day
and a counter would read that as a reset.

Plus, per pet: collar battery level (`%`, `battery`), activity type, current place name, current place address, and the current connection source. Each Fi Base reports `Online` / `Offline`.

Because every statistic carries a state class, they are recorded as **long-term statistics** and can be charted over months.

### Behaviour sensors

Fi's collar detects five behaviours, each exposed as a sensor counting today's
events:

| Sensor | Fi id | Icon |
|---|---|---|
| Barking | `barking` | `mdi:bullhorn` |
| Eating | `eating` | `mdi:food-drumstick` |
| Drinking | `drinking` | `mdi:cup-water` |
| Licking | `cleaning_self` | `mdi:emoticon-tongue-outline` |
| Scratching | `scratching` | `mdi:hand-back-right` |

Each carries the individual event times as attributes, so a chart can rebuild the
whole day without waiting on recorder history:

```yaml
events: ["2026-09-19T01:27:28+03:00", "2026-09-19T01:29:52+03:00"]
last_event: "2026-09-19T01:29:52+03:00"
```

The counts reset at local midnight. `pytryfi` does not implement this data; it is
fetched directly from Fi's `getPetHealthTrendsForPet` query.

### Binary sensor

Collar battery charging state, with the `battery_charging` device class.

### Light

The collar LED is exposed as a `light` entity. Fi supports a fixed palette — red, green, blue, light blue, purple, yellow and white — and the closest match to the requested colour is used.

### Select

Lost Dog mode is a `select` entity with `Safe` and `Lost` options.

## Installation

### HACS (recommended)

1. In HACS, add this repository as a **custom repository** with category **Integration**.
2. Search for **Fi Tracking** and download it.
3. Restart Home Assistant.

### Manual

1. Copy `custom_components/fitracking` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

## Configuration

Add the integration from **Settings → Devices & Services → Add Integration → Fi Tracking**, then supply:

| Field | Description |
|---|---|
| Username | The e-mail address of your Fi account |
| Password | Your Fi account password |
| Polling | Seconds between updates (default `10`, minimum `1`) |

The polling rate can be changed later from the integration's **Configure** dialog; the entry reloads automatically so the new value takes effect immediately.

An active Fi membership is required — the collar reports nothing without one.

## Dashboard

Both charts need [apexcharts-card](https://github.com/RomRider/apexcharts-card).
Replace `rex` with your own pet's slug.

### Behaviours today

Five lanes across a 24-hour axis, one thin vertical tick per detected event, in
Fi's own colours. The series are built from the `events` attribute rather than
recorder history, so the full day renders immediately after a restart.

```yaml
type: custom:apexcharts-card
graph_span: 24h
span:
  start: day
cache: false
update_interval: 5min
chart_type: line
header:
  show: true
  title: Behaviours today
  show_states: false
apex_config:
  chart:
    height: 240
    toolbar:
      show: false
  markers:
    size: 0
  stroke:
    curve: straight
    width: 2
  legend:
    show: false
  grid:
    show: true
    borderColor: var(--divider-color)
  xaxis:
    type: datetime
  yaxis:
    min: 0.5
    max: 5.5
    tickAmount: 5
    labels:
      formatter: >-
        EVAL:function(v){return
        ['','Scratching','Licking','Drinking','Eating','Barking'][Math.round(v)]||''}
  tooltip:
    x:
      format: HH:mm
series:
  - entity: sensor.rex_barking
    name: Barking
    color: "#AD581F"
    stroke_width: 2
    data_generator: |
      const y = 5;
      const out = [];
      (entity.attributes.events || []).forEach(t => {
        const x = new Date(t).getTime();
        out.push([x, y - 0.34]);
        out.push([x, y + 0.34]);
        out.push([x + 1000, null]);
      });
      return out;
  - entity: sensor.rex_eating
    name: Eating
    color: "#FFA411"
    stroke_width: 2
    data_generator: |
      const y = 4;
      const out = [];
      (entity.attributes.events || []).forEach(t => {
        const x = new Date(t).getTime();
        out.push([x, y - 0.34]);
        out.push([x, y + 0.34]);
        out.push([x + 1000, null]);
      });
      return out;
  - entity: sensor.rex_drinking
    name: Drinking
    color: "#5CB5F5"
    stroke_width: 2
    data_generator: |
      const y = 3;
      const out = [];
      (entity.attributes.events || []).forEach(t => {
        const x = new Date(t).getTime();
        out.push([x, y - 0.34]);
        out.push([x, y + 0.34]);
        out.push([x + 1000, null]);
      });
      return out;
  - entity: sensor.rex_licking
    name: Licking
    color: "#E2123C"
    stroke_width: 2
    data_generator: |
      const y = 2;
      const out = [];
      (entity.attributes.events || []).forEach(t => {
        const x = new Date(t).getTime();
        out.push([x, y - 0.34]);
        out.push([x, y + 0.34]);
        out.push([x + 1000, null]);
      });
      return out;
  - entity: sensor.rex_scratching
    name: Scratching
    color: "#FBDC19"
    stroke_width: 2
    data_generator: |
      const y = 1;
      const out = [];
      (entity.attributes.events || []).forEach(t => {
        const x = new Date(t).getTime();
        out.push([x, y - 0.34]);
        out.push([x, y + 0.34]);
        out.push([x + 1000, null]);
      });
      return out;
```

Each event becomes two points at the same timestamp, one either side of the lane
centre, which draws a vertical stroke; the trailing `null` breaks the line so
consecutive events do not join up. `stroke_width` sets how thick the tick is,
and `± 0.34` how tall.

### Steps against goal

Daily steps as columns with the goal as a line over the past week.

```yaml
type: custom:apexcharts-card
graph_span: 7d
cache: true
update_interval: 5min
span:
  end: day
header:
  show: true
  show_states: true
  colorize_states: true
  title: Steps Actual vs Goal
apex_config:
  chart:
    type: area
    height: 180
  plotOptions:
    bar:
      columnWidth: 70%
  legend:
    show: false
  dataLabels:
    enabled: true
    distributed: true
    background:
      enabled: false
    style:
      colors:
        - var(--primary-text-color)
  fill:
    type: fill
  grid:
    show: false
  yaxis:
    show: true
series:
  - entity: sensor.rex_daily_steps
    type: column
    name: " "
    color: steelblue
    float_precision: 0
    group_by:
      func: max
      duration: 1d
    show:
      datalabels: true
  - entity: sensor.rex_daily_goal
    type: line
    name: Goal
    color: var(--error-color)
    stroke_width: 2
    float_precision: 0
    group_by:
      func: last
      duration: 1d
    show:
      legend_value: false
      datalabels: false
```

## Connection sources

The collar picks the cheapest transport available and the `Connected To` sensor reports which one is in use:

| State | Meaning |
|---|---|
| `ConnectedToBase` | In Bluetooth range of a Fi Base — lowest power |
| `ConnectedToUser` | In Bluetooth range of a phone running the Fi app |
| `ConnectedToCellular` | Reporting over LTE-M, GPS active — highest power |
| `Unknown` | Offline |

A collar sitting on `ConnectedToCellular` while at home usually means the Base is out of Bluetooth range.

## Differences from upstream

| Change | Why |
|---|---|
| Domain renamed `tryfi` → `fitracking` | Matches Fi's rebrand to fitracking.com |
| Goal sensors added | Upstream left `# FUTURE COULD INCLUDE STEP GOAL`; `pytryfi` already exposed the values |
| Migrated to `SensorEntity` | Entities inherited plain `Entity`, so no `state_class` was possible and no long-term statistics were recorded |
| Per-metric icons | Every statistic returned `mdi:map-marker-distance`, sleep included |
| Device classes and display precision | Distance, duration and battery now render natively |
| Options flow fixed | `OptionsFlow.config_entry` is read-only from HA 2024.11, so the dialog crashed ([#113](https://github.com/sbabcock23/hass-tryfi/issues/113), [#114](https://github.com/sbabcock23/hass-tryfi/pull/114)) |
| Polling rate honoured | Setup read `entry.data` while the options flow wrote `entry.options`, so changes did nothing |
| Resilient entity setup | One malformed pet or base aborted the whole platform ([#112](https://github.com/sbabcock23/hass-tryfi/pull/112), [#93](https://github.com/sbabcock23/hass-tryfi/issues/93)) |
| Modern platform unload | Replaced the deprecated `async_forward_entry_unload` loop |
| Behaviour sensors added | Barking, eating, drinking, licking and scratching are in Fi's API but absent from `pytryfi` |

## Credits

Original integration by [@sbabcock23](https://github.com/sbabcock23), built on the
[pytryfi](https://github.com/sbabcock23/pytryfi) library. This fork is not affiliated with Fi.

## License

[Apache-2.0](LICENSE)
