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

---

# EV and Battery Charger

**EV and Battery Charger** is a Home Assistant custom integration that calculates charging duration, planned charging start and planned charging end for an electric vehicle, plug-in hybrid or battery storage system.

The integration can use a fixed daily ready-by time or optionally use the **next event from a Home Assistant calendar**. If a calendar is configured and a next event is available, the start time of that event is used as the desired ready-by time. The planned charging end is still placed before that time by the configured buffer, for example 30 minutes.

## Features

- Calculates required charging duration in minutes
- Calculates required energy in kWh
- Calculates planned charging start
- Calculates planned charging end with buffer
- Optional: charging plan based on the next Home Assistant calendar event
- Falls back to the daily ready-by time if no calendar or calendar event is available
- Target charge through an `input_number`
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

## Calculation

```text
soc_diff = target_soc - current_soc
kwh_needed = (soc_diff / 100) * battery_size_kwh / efficiency
duration_minutes = ceil((kwh_needed / charge_power_kw) * 60)
planned_end = ready_by - buffer_minutes
planned_start = planned_end - duration_minutes
```

## Calendar feature

Optionally, enter a calendar in the config flow, for example:

```text
calendar.cupra_charging
```

The integration will then use the next event in this calendar as the target ready-by time. Example:

- Calendar event: `Tomorrow 08:00`
- Buffer: `30 minutes`
- Required charging duration: `90 minutes`

Result:

```text
Target ready time: Tomorrow 08:00
Planned charge end: Tomorrow 07:30
Planned charge start: Tomorrow 06:00
```

If no calendar is configured or no calendar event with `start_time` is available, the integration uses the daily ready-by time.

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
| Charge plan status | `not_needed`, `waiting`, `charging_window` or `late` |

## Installation

1. Copy the folder `custom_components/ev_and_battery_charger` to Home Assistant.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration**.
4. Search for **EV and Battery Charger**.
5. Enter your entities and charging parameters.

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
