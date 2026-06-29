# EV and Battery Charger

Custom Integration für Home Assistant, die die Ladedauer in Minuten, den geplanten Ladestart und das geplante Ladeende für ein E-Auto, Plug-in-Hybrid-Fahrzeug oder einen Batteriespeicher berechnet.

## Funktionen

- Nutzt einen aktuellen SOC-Sensor in Prozent.
- Nutzt einen Ziel-Ladestand-Helper, normalerweise ein `input_number`.
- Nutzt eine tägliche Fertig-Uhrzeit.
- Berechnet die benötigte Ladedauer in Minuten.
- Berechnet den geplanten Ladestart.
- Berechnet das geplante Ladeende mit konfigurierbarem Puffer vor der Fertig-Uhrzeit.
- Schätzt die benötigte Energie in kWh.

## Standardwerte

```text
battery_size_kwh = 19.7
charge_power_kw = 10.5
efficiency = 0.93
buffer_minutes = 30
```

## Installation

Kopiere `custom_components/ev_and_battery_charger` in deinen Home-Assistant-Ordner `custom_components`, starte Home Assistant neu und füge **EV and Battery Charger** unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** hinzu.

## Icons und Logo

Das Repository enthält `icon.png`, `logo.png` und `icon.svg` für GitHub/HACS-Branding. Die Entitäts-Icons sind zusätzlich über `icons.json` definiert.
