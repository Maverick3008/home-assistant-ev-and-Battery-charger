# Upload für Version 1.5.0

Diese Dateien im Repository ersetzen bzw. neu hochladen:

## Root
- `README.md`
- `README.de.md`
- `README.en.md`
- `CHANGELOG.md`
- `info.md`

## Integration
- `custom_components/ev_and_battery_charger/__init__.py`
- `custom_components/ev_and_battery_charger/config_flow.py`
- `custom_components/ev_and_battery_charger/sensor.py`
- `custom_components/ev_and_battery_charger/manifest.json`
- `custom_components/ev_and_battery_charger/strings.json`
- `custom_components/ev_and_battery_charger/translations/de.json`
- `custom_components/ev_and_battery_charger/translations/en.json`

## Unverändert lassen
- `hacs.json`
- `custom_components/ev_and_battery_charger/const.py`
- `custom_components/ev_and_battery_charger/number.py`
- `custom_components/ev_and_battery_charger/icons.json`
- Icons, Logos und Brand-Dateien

## Danach
1. Änderungen nach `main` committen.
2. GitHub Release erstellen.
3. Tag: `1.5.0`
4. Release-Name: `Release 1.5.0`
5. Home Assistant/HACS aktualisieren und Home Assistant neu starten.

Die Integrationsversion steht in `manifest.json` auf `1.5.0`.
`hacs.json` enthält in diesem Repository keine Paketversion und muss daher nicht geändert werden.
