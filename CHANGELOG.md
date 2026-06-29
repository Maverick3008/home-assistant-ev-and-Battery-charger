# Changelog
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
