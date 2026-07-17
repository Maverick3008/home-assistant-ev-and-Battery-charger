# Changelog

## 1.0.17

- Ignore calendar events whose start time is equal to or earlier than the current time.
- Use the configured daily ready time as fallback when calendar priority is selected and the exposed calendar event has already started.
- Clear the calendar event title/start/end diagnostic values for rejected past or running events.
- Updated the manifest and German/English documentation to version 1.0.17.

## 1.0.16

- Fixed the Config Flow label for the 100% full-charge safety extension.
- The field now uses a UI-safe key so Home Assistant no longer shows `full_charge_extra_minutes` when translations are cached or not resolved.

## 1.0.15

- Added the full-charge safety extension to the config flow.
- Added the German label `Zusätzliche Ladezeit bei 100 % Ziel-Ladestand`.
- Made the 100% target charge extension configurable instead of fixed at 10 minutes.

## 1.0.14

- Added a 10-minute full-charge safety extension when the target state of charge is 100%.
- The extra time is included in the required charging duration and therefore moves the planned charging start 10 minutes earlier.

## 1.0.13

- Improved the config-flow label for the initial target state of charge.
- Uses a dedicated UI field key so Home Assistant no longer shows the raw technical label `target_soc` on some frontend versions.
- Keeps existing configuration compatibility by storing the value internally as `target_soc`.

## 1.0.11

- Added entity selectors to the config/options flow for the current SOC entity and optional calendar entity.
- Added an internal **Target state of charge** number entity so the target SOC can be changed directly in Home Assistant.
- Removed the need for a separate external `input_number` target SOC helper for new setups.
- Kept migration fallback for older configs that still contain `target_soc_entity`.

## 1.0.10

- Changed charge-window behavior: once a charging window starts, the initially calculated required duration is frozen.
- SOC changes during an active charging window no longer recalculate or shorten the required duration.
- After the frozen required duration has elapsed, the status changes directly to `not_needed` for the current charge target.
- Added diagnostic attributes for the locked runtime: `locked_duration_minutes`, `locked_charge_started_at`, and `locked_charge_finished_at`.

## 1.0.9

- Added charge-window locking. Once the charging window has started, the status stays in `charging_window` until the target SOC is reached or the planned end time has passed.
- Prevented the status from jumping back to `waiting` while charging, when the remaining charge duration becomes shorter and the calculated start time would move forward.
- Added `charging_window_locked` as a diagnostic attribute.

## 1.0.8

- Improved German and English labels for the target source priority selector.
- Added translated dropdown labels: Calendar event first / Daily overnight time first.
- Reworked the reconfigure flow to use Home Assistant's safe update-and-reload helper.
- Simplified the options flow to use Home Assistant's built-in `self.config_entry` handling.
- Changed option reload handling to use `hass.config_entries.async_reload(entry.entry_id)` instead of manual unload/setup.
- Avoided double reloads on Home Assistant versions with OptionsFlowWithReload.

## 1.0.7

- Added configurable target source priority.
- You can now choose whether the calendar or the daily overnight ready-by time is used first.
- Added a target source priority sensor and translations.

## 1.0.6

- Made the existing configuration/options flow more robust.
- Added an explicit reconfigure flow for already configured entries.
- Added safer number validation to prevent the configuration dialog from hanging on invalid values.

## 1.0.5

- Added optional Home Assistant calendar support.
- The next calendar event can now be used as the ready-by time.
- Added target ready time, target source and next calendar event sensors.
- Updated German and English documentation.

## 1.0.4

- Added local brand assets in `custom_components/ev_and_battery_charger/brand/`.
- Added repository-level `brand/` folder for HACS compatibility.

## 1.0.3

- Fixed a possible Home Assistant config flow `400: Bad Request` error by replacing advanced form selectors with robust plain input fields.
- Added additional validation messages for entity IDs, time format, positive values and efficiency.
- Set a static config flow title for better compatibility.

## 1.0.2

- Added `icon.png`, `logo.png` and `icon.svg`.
- Reworked the icon with less empty border/padding.

## 1.0.1

- Renamed integration to **EV and Battery Charger**.
- Renamed domain/folder to `ev_and_battery_charger`.
- Updated German and English descriptions for EVs, plug-in hybrids and battery storage systems.

## 1.0.0

- Initial release.
- Config flow setup.
- Sensors for required charge duration, planned charge start, planned charge end, energy needed and charge plan status.
- German and English translations.
