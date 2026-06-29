# EV and Battery Charger

Custom integration for Home Assistant that calculates the charging duration in minutes, the planned charging start and the planned charging end for an EV, plug-in hybrid or battery storage system.

## Features

- Uses a current SOC sensor in percent.
- Uses a target charge helper, usually an `input_number`.
- Uses a daily ready-by time.
- Calculates the required charging duration in minutes.
- Calculates the planned charging start.
- Calculates the planned charging end with a configurable buffer before the ready-by time.
- Estimates the required energy in kWh.

## Default values

```text
battery_size_kwh = 19.7
charge_power_kw = 10.5
efficiency = 0.93
buffer_minutes = 30
```

## Installation

Copy `custom_components/ev_and_battery_charger` to your Home Assistant `custom_components` directory, restart Home Assistant and add **EV and Battery Charger** from **Settings → Devices & services → Add integration**.

## Icons and logo

The repository includes `icon.png`, `logo.png` and `icon.svg` for GitHub/HACS branding. Entity icons are also defined via `icons.json`.
