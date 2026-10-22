# EV and Battery Charger

## Version 1.5.1 – simple 03:00 calendar fallback

Version **1.5.1** adds a deliberately simple safety fallback for cases where the vehicle SOC does not update correctly:

- From **03:00**, the integration checks whether a **future calendar event still exists today**.
- If the normal plan reports `not_needed`, the SOC is ignored for this fallback.
- The charge-plan status is changed to **`charging_window`**.
- `planned_start` is set to **03:00**.
- `planned_end` is set to the **start of today's next calendar event**.
- The displayed charge duration represents only the fallback window from 03:00 until the event and is **not calculated from SOC**.
- The fallback ends automatically when the event starts.
- If there is no future event today, or the normal status is not `not_needed`, the fallback does not activate.

This allows an existing wallbox automation to react to `charging_window` and start charging even when a stale or incorrect SOC value would otherwise suppress charging.

Additional diagnostic attributes:

```text
calendar_fallback_active
calendar_fallback_reason
calendar_fallback_start
```

## Version 1.5.0 – multiple calendars

**EV and Battery Charger** is a Home Assistant custom integration that calculates charging duration, planned charging start, and planned charging end for EVs, plug-in hybrids, or battery storage systems.

Starting with **version 1.5.0**, the config flow supports **multiple Home Assistant calendars**. The integration checks all selected calendars and uses the **earliest future event** for the charging plan.

### Multiple-calendar behavior

- Select multiple `calendar.*` entities in the config flow.
- All selected calendars are refreshed every **30 minutes** using `homeassistant.update_entity`.
- The **earliest future event** across all selected calendars is used.
- If two events have the same start time, calendar selection order wins.
- Existing installations with a single calendar remain compatible; the stored single value is automatically treated as a list.
- The sensor attribute `calendar_entities` contains all selected calendars.
- The existing `calendar_entity` attribute identifies the calendar providing the currently selected event.

## Calendar and target-SOC logic

The behavior introduced in version 1.4.1 remains unchanged:

- An eligible event **tomorrow** can raise the target SOC to **100%** only after today's configured daily ready time has been reached.
- Events two or more days away do not raise the target SOC yet.
- Once activated, the same event keeps the 100% target across midnight until its associated charging cycle completes.
- After completion, the target SOC is reset automatically to **80%**.
- A configurable safety extension can be added when charging to 100%.

## Target priority

**Calendar event first**
: Uses the earliest future event across all selected calendars. If none is available, the daily ready time is used.

**Prefer daily overnight time (earlier events first)**
: Normally uses the daily ready time. If the earliest calendar event happens sooner, that event automatically becomes the target.

## Features

- Required charging duration in minutes
- Required energy in kWh
- Planned charging start
- Planned charging end with buffer
- Dedicated target-SOC number entity
- Multiple optional calendars
- Earliest future event across all selected calendars
- Automatic 30-minute calendar refresh
- Automatic 100% / 80% calendar target behavior
- Locked charging duration once a charging window starts
- German and English translations
- HACS support

## Example values – Cupra Leon e-Hybrid

| Setting | Example |
|---|---:|
| Battery size | `19.7` kWh |
| Charging power | `10.5` kW |
| Charging efficiency | `0.93` |
| Buffer | `30` minutes |
| Extra charging time at 100% | `10` minutes |

## Calculation

```text
soc_diff = target_soc - current_soc
kwh_needed = (soc_diff / 100) * battery_size_kwh / efficiency
duration_minutes = ceil((kwh_needed / charge_power_kw) * 60)

if target_soc >= 100 and duration_minutes > 0:
    duration_minutes += full_charge_extra_minutes

planned_end = ready_by - buffer_minutes
planned_start = planned_end - duration_minutes
```

## Sensors

| Sensor | Meaning |
|---|---|
| Required charge duration | Charging duration in minutes |
| Target ready time | Ready-by time used by the planner |
| Planned charge start | Planned charging start |
| Planned charge end | Planned charging end before the buffer |
| Energy needed | Estimated energy in kWh |
| Next calendar event start | Start of the earliest calendar event |
| Next calendar event | Title of the earliest calendar event |
| Target source | `daily_time` or `calendar` |
| Target source priority | Selected priority logic |
| Charge plan status | `not_needed`, `waiting`, `charging_window`, or `late` |

A **Target state of charge** number entity is also created.

## Installation

1. Copy `custom_components/ev_and_battery_charger` to Home Assistant or install through HACS.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration**.
4. Select **EV and Battery Charger**.
5. Configure the SOC sensor, daily ready time, charging parameters, and optionally multiple calendars.

## Updating from 1.4.1

You do not need to remove the existing configuration. A previously stored single calendar is automatically reused by 1.5.0. Open the integration options afterwards to add more calendars.

## Release

Integration version: **1.5.1**

For HACS, create a GitHub release/tag **`1.5.1`** after uploading the files.
