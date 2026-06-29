## 1.0.5

- Added optional Home Assistant calendar support.
- The next calendar event can now be used as the ready-by time.
- Added target ready time, target source and next calendar event sensors.
- Updated German and English documentation.

# Changelog

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

## 1.0.6

### Fixed
- Made the existing configuration/options flow more robust.
- Added an explicit reconfigure flow for already configured entries.
- Added safer number validation to prevent the configuration dialog from hanging on invalid values.
