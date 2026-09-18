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
| Sleep | `min` | `duration` | `total_increasing` |
| Nap | `min` | `duration` | `total_increasing` |
| Goal | `steps` | – | `measurement` |

Plus, per pet: collar battery level (`%`, `battery`), activity type, current place name, current place address, and the current connection source. Each Fi Base reports `Online` / `Offline`.

Because every statistic carries a state class, they are recorded as **long-term statistics** and can be charted over months.

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

## Credits

Original integration by [@sbabcock23](https://github.com/sbabcock23), built on the
[pytryfi](https://github.com/sbabcock23/pytryfi) library. This fork is not affiliated with Fi.

## License

[Apache-2.0](LICENSE)
