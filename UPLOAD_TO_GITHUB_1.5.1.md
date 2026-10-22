# GitHub Upload – Version 1.5.1

## Dateien ersetzen

### Repository Root
- `README.md`
- `README.de.md`
- `README.en.md`
- `CHANGELOG.md`
- `info.md`

### Integration
- `custom_components/ev_and_battery_charger/sensor.py`
- `custom_components/ev_and_battery_charger/manifest.json`
- `custom_components/ev_and_battery_charger/strings.json`
- `custom_components/ev_and_battery_charger/translations/de.json`
- `custom_components/ev_and_battery_charger/translations/en.json`

Die folgenden Dateien aus 1.5.0 sind weiterhin Teil des vollständigen Pakets und können unverändert mit hochgeladen werden:
- `custom_components/ev_and_battery_charger/__init__.py`
- `custom_components/ev_and_battery_charger/config_flow.py`

## Nicht ändern
- `hacs.json`
- `custom_components/ev_and_battery_charger/const.py`
- `custom_components/ev_and_battery_charger/number.py`
- `custom_components/ev_and_battery_charger/icons.json`
- Icons, Logos und Brand-Dateien

## Danach
1. Änderungen nach `main` hochladen/committen.
2. GitHub Release erstellen.
3. Tag: `1.5.1`
4. Release-Name: `Release 1.5.1`
5. In HACS aktualisieren.
6. Home Assistant neu starten.

Die Integrationsversion steht in `manifest.json` auf `1.5.1`.
