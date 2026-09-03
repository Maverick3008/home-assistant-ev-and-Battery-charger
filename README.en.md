# EV and Battery Charger

### Note for version 1.4.1

The automatic target state of charge is now raised to **100% only when the selected calendar event starts tomorrow**. An event two or more days away remains available to the charging planner but does not trigger the 100% automation yet.

Once a tomorrow-event has activated 100%, that target remains active for the same event **after midnight** until its associated charging cycle has completed. The target is then automatically reset to **80%**, as before.

The **selected calendar entity is still refreshed every 30 minutes** using `homeassistant.update_entity`. This is particularly useful with Home Assistant's **Remote Calendar** integration.

**EV and Battery Charger** is a Home Assistant custom integration that calculates charging duration, planned charging start and planned charging end for an electric vehicle, plug-in hybrid or battery storage system.

The integration can use a fixed daily ready-by time or optionally use the **next event from a Home Assistant calendar**. The config flow lets you choose either **Calendar event first** or **Prefer daily overnight time**, where an earlier calendar event automatically takes precedence. The planned charging end is placed before the selected ready-by time by the configured buffer, for example 30 minutes.

## Features

- Calculates required charging duration in minutes
- Calculates required energy in kWh
- Calculates planned charging start
- Calculates planned charging end with buffer
- Optional: charging plan based on the next Home Assistant calendar event
- Charging target logic: calendar event first or prefer daily overnight time
- With preferred overnight charging, an earlier future calendar event automatically overrides the overnight target
- A later calendar event does not postpone the normal overnight charge
- Falls back to the daily ready-by time when calendar first is selected and no calendar event is available
- Dedicated target state of charge number entity (`number.*`)
- **Calendar event tomorrow** detected → target SOC automatically set to `100%`
- Calendar event **two or more days away** → no automatic 100% change yet
- An already activated event keeps `100%` after midnight until the related charge cycle completes
- After the related charge cycle completes → target automatically reset to `80%`
- Selected calendar entity is refreshed automatically every `30 minutes`
- Adds a configurable safety extension when the target state of charge is 100%
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
| Extra charging time at 100% target state of charge | `10` minutes |

## Calculation

```text
soc_diff = target_soc - current_soc
kwh_needed = (soc_diff / 100) * battery_size_kwh / efficiency
duration_minutes = ceil((kwh_needed / charge_power_kw) * 60)
if target_soc >= 100 and duration_minutes > 0:
    duration_minutes = duration_minutes + full_charge_extra_minutes
planned_end = ready_by - buffer_minutes
planned_start = planned_end - duration_minutes
```

## Calendar feature

Optionally, enter a calendar in the config flow, for example:

```text
calendar.cupra_charging
```

### Automatic calendar refresh and target SOC

Only the calendar entity selected in this integration is refreshed every 30 minutes through `homeassistant.update_entity`. The integration does not refresh every calendar in Home Assistant.

Starting with version **1.4.1**, the automatic 100% behavior is:

- Event starts **tomorrow** → target SOC is automatically raised to **100%**.
- Event starts **two or more days from now** → target SOC remains unchanged.
- Once an event has activated 100%, the same event keeps that target after midnight.
- After the associated locked charging window finishes, the target SOC is reset to **80%**.
- The same completed event cannot immediately trigger 100% again.
- If an active, uncompleted event is removed, the target is also reset to 80%.

Example: if today is **September 3**, an event on **September 4** activates 100%. An event on **September 5** does not activate it on September 3; on September 4 that event becomes "tomorrow" and may then raise the target to 100%.

This automatic 100% behavior is independent of whether the calendar event becomes the active `ready_by` source under the selected target priority.

In the config flow, choose the priority:

```text
Calendar event first
```

or:

```text
Prefer daily overnight time (earlier events first)
```

With `Calendar event first`, the integration uses the next calendar event as the target ready-by time only if its start time is still in the future.

With `Prefer daily overnight time (earlier events first)`, the daily ready time is the normal target. However, if the next future calendar event occurs **earlier** than that daily ready time, the calendar event is used instead. If the calendar event is later, the daily overnight target remains active.

Example with `Calendar event first`:

- Calendar event: `Tomorrow 08:00`
- Buffer: `30 minutes`
- Required charging duration: `90 minutes`

Result:

```text
Target ready time: Tomorrow 08:00
Planned charge end: Tomorrow 07:30
Planned charge start: Tomorrow 06:00
```

With `Prefer daily overnight time (earlier events first)`:

- Calendar event **before** the next overnight target → the calendar event becomes the charging target.
- Calendar event **after** the next overnight target → the overnight target stays active.
- No valid future calendar event → the overnight target stays active.

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
| Target source priority | `Calendar event first` or `Prefer daily overnight time (earlier events first)` |
| Charge plan status | `not_needed`, `waiting`, `charging_window` or `late` |

A number entity is also created:

| Entity | Meaning |
|---|---|
| Target state of charge | Target SOC in percent that you can change directly in Home Assistant |

### 100% full-charge safety extension

If the target state of charge is set to **100%** and charging is actually required, the integration adds the safety extension configured in the config flow to the calculated charging duration. The default is **10 minutes**.

### Fixed charging duration during an active charging window

Once the charging window has been reached, the **required charge duration** calculated at that moment is frozen. During the active charging window, the duration is no longer recalculated or shortened by rising SOC values.

The status stays on `charging_window` for exactly this frozen duration. After that duration has elapsed, the status changes directly to `not_needed` for the current charge target.

Additional diagnostic attributes:

```text
locked_duration_minutes
locked_charge_started_at
locked_charge_finished_at
```

## Installation

1. Copy the folder `custom_components/ev_and_battery_charger` to Home Assistant.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration**.
4. Search for **EV and Battery Charger**.
5. Select the current state of charge entity, optionally select a calendar, and enter your charging parameters.
6. Afterwards, change the target SOC through the **Target state of charge** number entity.

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

Version: 1.4.1
