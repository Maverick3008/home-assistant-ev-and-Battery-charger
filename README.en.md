# EV and Battery Charger

**EV and Battery Charger** is a Home Assistant custom integration that calculates charging duration, planned charging start and planned charging end for an electric vehicle, plug-in hybrid or battery storage system.

The integration can use a fixed daily ready-by time or optionally use the **next event from a Home Assistant calendar**. The config flow now lets you choose which source has priority: **calendar first** or **daily time first**. The planned charging end is still placed before the selected ready-by time by the configured buffer, for example 30 minutes.

## Features

- Calculates required charging duration in minutes
- Calculates required energy in kWh
- Calculates planned charging start
- Calculates planned charging end with buffer
- Optional: charging plan based on the next Home Assistant calendar event
- Priority selection: calendar first or daily time first
- Falls back to the daily ready-by time when calendar first is selected and no calendar event is available
- Target charge through an `input_number`
- Current state of charge through a sensor entity
- German and English translations
- Icon, logo and brand files included

## Example values for Cupra Leon e-Hybrid

| Setting | Example |
|---|---:|
| Battery size | `19.7` kWh |
| Charging power | `10.5` kW |
| Charging efficiency | `0.93` |
| Buffer | `30` minutes |

## Calculation

```text
soc_diff = target_soc - current_soc
kwh_needed = (soc_diff / 100) * battery_size_kwh / efficiency
duration_minutes = ceil((kwh_needed / charge_power_kw) * 60)
planned_end = ready_by - buffer_minutes
planned_start = planned_end - duration_minutes
```

## Calendar feature

Optionally, enter a calendar in the config flow, for example:

```text
calendar.cupra_charging
```

In the config flow, also choose the priority:

```text
calendar_first
```

or:

```text
daily_time_first
```

With `calendar_first`, the integration uses the next calendar event as the target ready-by time if one is available. With `daily_time_first`, it uses the daily ready-by time as the primary source.

Example with `calendar_first`:

- Calendar event: `Tomorrow 08:00`
- Buffer: `30 minutes`
- Required charging duration: `90 minutes`

Result:

```text
Target ready time: Tomorrow 08:00
Planned charge end: Tomorrow 07:30
Planned charge start: Tomorrow 06:00
```

If `calendar_first` is selected and no calendar is configured or no calendar event with `start_time` is available, the integration uses the daily ready-by time. If `daily_time_first` is selected, the daily ready-by time is used directly.

Note: The integration uses the next-event attributes of the calendar entity (`message`, `start_time`, `end_time`). For complex calendars with multiple overlapping events, Home Assistant calendar automations may be more flexible.

## Created sensors

| Sensor | Meaning |
|---|---|
| Required charge duration | Charging duration in minutes |
| Target ready time | Active target time, either daily time or calendar event |
| Planned charge start | Time when charging should start |
| Planned charge end | Time when charging should end before the buffer |
| Energy needed | Estimated energy in kWh |
| Next calendar event start | Start time of the next calendar event, if available |
| Next calendar event | Title of the next calendar event, if available |
| Target source | `daily_time` or `calendar` |
| Target source priority | `calendar_first` or `daily_time_first` |
| Charge plan status | `not_needed`, `waiting`, `charging_window` or `late` |

## Installation

1. Copy the folder `custom_components/ev_and_battery_charger` to Home Assistant.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration**.
4. Search for **EV and Battery Charger**.
5. Enter your entities and charging parameters.

## Example charging automation

The integration does not switch your charger automatically. Use a Home Assistant automation based on the sensors.

```yaml
alias: Charge Cupra by charging plan
mode: single
triggers:
  - trigger: time
    at: sensor.cupra_leon_planned_charge_start
conditions:
  - condition: numeric_state
    entity_id: sensor.cupra_leon_required_charge_duration
    above: 0
actions:
  - action: select.select_option
    target:
      entity_id: select.myenergi_zappi_24278485_charge_mode
    data:
      option: Fast
```

You can stop charging in the same way using the planned charge end sensor.
