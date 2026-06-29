# EV and Battery Charger

**EV and Battery Charger** ist eine Home-Assistant-Custom-Integration zur Berechnung der Ladedauer, des geplanten Ladestarts und des geplanten Ladeendes für ein E-Auto, Plug-in-Hybrid-Fahrzeug oder einen Batteriespeicher.

Die Integration kann mit einer festen täglichen Fertig-Uhrzeit arbeiten oder optional den **nächsten Termin aus einem Home-Assistant-Kalender** verwenden. Ist ein Kalender hinterlegt und enthält dieser einen nächsten Termin, wird die Startzeit dieses Termins als gewünschte Fertig-Zeit genutzt. Das geplante Ladeende liegt weiterhin um den konfigurierten Puffer davor, zum Beispiel 30 Minuten.

## Funktionen

- Berechnung der benötigten Ladedauer in Minuten
- Berechnung der benötigten Energie in kWh
- Berechnung des geplanten Ladestarts
- Berechnung des geplanten Ladeendes mit Puffer
- Optional: Ladeplanung anhand des nächsten Home-Assistant-Kalendertermins
- Fallback auf tägliche Fertig-Uhrzeit, wenn kein Kalender oder kein Kalendertermin verfügbar ist
- Ziel-Ladestand über `input_number`
- Aktueller Akkustand über Sensor-Entität
- Deutsche und englische Übersetzungen
- Icon, Logo und Brand-Dateien enthalten

## Beispielwerte für Cupra Leon e-Hybrid

| Einstellung | Beispiel |
|---|---:|
| Batteriegröße | `19.7` kWh |
| Ladeleistung | `10.5` kW |
| Ladeeffizienz | `0.93` |
| Puffer | `30` Minuten |

## Berechnung

```text
soc_diff = target_soc - current_soc
kwh_needed = (soc_diff / 100) * battery_size_kwh / efficiency
duration_minutes = ceil((kwh_needed / charge_power_kw) * 60)
planned_end = ready_by - buffer_minutes
planned_start = planned_end - duration_minutes
```

## Kalender-Funktion

Optional kann im Config Flow ein Kalender angegeben werden, zum Beispiel:

```text
calendar.cupra_ladung
```

Dann verwendet die Integration den nächsten Termin dieses Kalenders als Ziel-Zeitpunkt. Beispiel:

- Termin im Kalender: `Morgen 08:00 Uhr`
- Puffer: `30 Minuten`
- Benötigte Ladedauer: `90 Minuten`

Ergebnis:

```text
Ladeziel Zeitpunkt: Morgen 08:00 Uhr
Geplantes Ladeende: Morgen 07:30 Uhr
Geplanter Ladestart: Morgen 06:00 Uhr
```

Wenn kein Kalender eingetragen ist oder kein Kalendertermin mit `start_time` verfügbar ist, nutzt die Integration die tägliche Fertig-Uhrzeit.

Hinweis: Die Integration nutzt die nächsten Kalendertermin-Attribute der Kalender-Entität (`message`, `start_time`, `end_time`). Für sehr komplexe Kalender mit mehreren parallelen Terminen ist die Kalender-Automation von Home Assistant oft flexibler.

## Entstehende Sensoren

| Sensor | Bedeutung |
|---|---|
| Benötigte Ladedauer | Ladedauer in Minuten |
| Ladeziel Zeitpunkt | Verwendeter Ziel-Zeitpunkt, entweder tägliche Uhrzeit oder Kalendertermin |
| Geplanter Ladestart | Zeitpunkt, zu dem die Ladung starten sollte |
| Geplantes Ladeende | Zeitpunkt, zu dem die Ladung vor dem Puffer enden sollte |
| Benötigte Energie | Geschätzte Energie in kWh |
| Nächster Kalendertermin Start | Startzeit des nächsten Kalendertermins, falls verfügbar |
| Nächster Kalendertermin | Titel des nächsten Kalendertermins, falls verfügbar |
| Ladeziel Quelle | `daily_time` oder `calendar` |
| Ladeplan Status | `not_needed`, `waiting`, `charging_window` oder `late` |

## Installation

1. Kopiere den Ordner `custom_components/ev_and_battery_charger` nach Home Assistant.
2. Starte Home Assistant neu.
3. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen**.
4. Suche nach **EV and Battery Charger**.
5. Trage deine Entitäten und Ladeparameter ein.

## Beispiel-Automation zum Laden

Die Integration schaltet dein Ladegerät nicht automatisch. Dafür kannst du eine Home-Assistant-Automation verwenden, die auf den Sensoren basiert.

```yaml
alias: Cupra nach Ladeplan laden
mode: single
triggers:
  - trigger: time
    at: sensor.cupra_leon_geplanter_ladestart
conditions:
  - condition: numeric_state
    entity_id: sensor.cupra_leon_benoetigte_ladedauer
    above: 0
actions:
  - action: select.select_option
    target:
      entity_id: select.myenergi_zappi_24278485_charge_mode
    data:
      option: Fast
```

Stoppen kannst du entsprechend mit dem Sensor für das geplante Ladeende.
