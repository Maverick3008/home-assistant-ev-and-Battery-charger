# Changelog

## 1.5.1
- Added a simple **03:00 calendar fallback** for stale or incorrect vehicle SOC values.
- From 03:00 onward, when a future calendar event still exists later on the same day and the normal charging plan reports `not_needed`, the integration now exposes `charging_window` regardless of SOC.
- During the fallback, `planned_start` is fixed to 03:00 and `planned_end` is the start time of today's selected calendar event.
- The fallback charge duration represents the complete 03:00-to-event window and is intentionally not calculated from SOC.
- The fallback ends automatically when the calendar event starts.
- Added diagnostic attributes `calendar_fallback_active`, `calendar_fallback_reason`, and `calendar_fallback_start`.
- Kept the multi-calendar behavior introduced in 1.5.0 unchanged.
- Updated manifest, translations, documentation, and release metadata to **1.5.1**.

## 1.5.0
- Added support for selecting **multiple Home Assistant calendar entities** in the config/options flow.
- Existing single-calendar configurations are migrated transparently and remain compatible.
- The charging planner now evaluates all selected calendars and uses the **earliest future event**.
- If multiple calendar events have the same start time, the configured calendar selection order is used as the tie-breaker.
- All selected calendar entities are refreshed every **30 minutes** using `homeassistant.update_entity`.
- State-change listeners now monitor all selected calendar entities.
- Added the diagnostic attribute `calendar_entities` with the complete configured calendar list.
- Kept `calendar_entity` as the calendar that supplied the currently selected event.
- Preserved the version 1.4.1 automatic 100% / 80% calendar target-SOC behavior.
- Updated German and English config-flow texts, documentation, and release metadata.
- Updated integration manifest version to **1.5.0**.

## 1.4.1
- Changed the automatic calendar target-SOC behavior introduced in 1.4.0.
- A calendar event may now raise the target state of charge to **100% only when it starts tomorrow AND today's configured daily ready-by time has already been reached**.
- This prevents a tomorrow-event from changing the current morning's normal charging target too early.
- Calendar events starting **two or more days in the future** still do not raise the target SOC prematurely.
- Once an eligible tomorrow-event has activated the 100% target, the target remains at 100% after midnight for the same event until the associated charging cycle has completed.
- After the associated locked charging cycle completes, the target state of charge is reset automatically to **80%**.
- The selected calendar entity continues to be refreshed every **30 minutes** using `homeassistant.update_entity`.

## 1.4.0
- Automatically set the integration's target state of charge to **100%** as soon as the selected calendar exposes a future event.
- Automatically reset the target state of charge to **80%** after the associated locked charge cycle has completed.
- Track completed calendar events so the same still-visible event cannot immediately switch the target back to 100%.
- Reset the target to 80% when an active, not-yet-completed calendar event is removed.
- Refresh the configured calendar entity every **30 minutes** using `homeassistant.update_entity`.
- Keep the visible target SOC number entity synchronized with automatic calendar-driven changes.

## 1.3.0
- Changed `daily_time_first` behavior so the daily overnight target remains the default, but an earlier future calendar event automatically becomes the active ready-by target.
- Calendar events later than the next daily ready time no longer affect the preferred overnight charging plan.

## 1.2.0
- Ignore calendar events whose start time is equal to or earlier than the current time.
- Use the configured daily ready time as fallback when calendar priority is selected and the exposed calendar event has already started.

## 1.0.17
- Maintenance release.

## 1.0.16
- Fixed the Config Flow label for the 100% full-charge safety extension.

## 1.0.15
- Added the configurable full-charge safety extension.

## 1.0.14
- Added a 10-minute full-charge safety extension when the target state of charge is 100%.

## 1.0.13
- Improved the config-flow label for the initial target state of charge.

## 1.0.11
- Added entity selectors and an internal Target state of charge number entity.

## 1.0.10
- Frozen charging duration once a charging window starts.

## 1.0.9
- Added charge-window locking.

## 1.0.8
- Improved translated target-source priority labels and reload handling.

## 1.0.7
- Added configurable target-source priority.

## 1.0.6
- Improved config/options flow robustness.

## 1.0.5
- Added optional Home Assistant calendar support.

## 1.0.4
- Added local brand assets and HACS-compatible repository brand assets.

## 1.0.3
- Improved config-flow compatibility and validation.

## 1.0.2
- Added icon and logo assets.

## 1.0.1
- Renamed integration to **EV and Battery Charger** and updated the domain.

## 1.0.0
- Initial release.
