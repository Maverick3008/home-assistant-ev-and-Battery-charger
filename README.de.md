# EV and Battery Charger

### Hinweis zu Version 1.0.15

Wenn der Ziel-Ladestand auf **100 %** steht und tatsächlich noch geladen werden muss, wird ein konfigurierbarer Sicherheitsaufschlag zur Ladedauer addiert. Standard: **10 Minuten**.


**EV and Battery Charger** ist eine Home-Assistant-Custom-Integration zur Berechnung der Ladedauer, des geplanten Ladestarts und des geplanten Ladeendes für ein E-Auto, Plug-in-Hybrid-Fahrzeug oder einen Batteriespeicher.

Die Integration kann mit einer festen täglichen Fertig-Uhrzeit arbeiten oder optional den **nächsten Termin aus einem Home-Assistant-Kalender** verwenden. Im Config Flow kannst du jetzt festlegen, welche Quelle Vorrang hat: **Kalender zuerst** oder **tägliche Uhrzeit zuerst**. Das geplante Ladeende liegt weiterhin um den konfigurierten Puffer davor, zum Beispiel 30 Minuten.

## Funktionen

- Berechnung der benötigten Ladedauer in Minuten
- Berechnung der benötigten Energie in kWh
- Berechnung des geplanten Ladestarts
- Berechnung des geplanten Ladeendes mit Puffer
- Optional: Ladeplanung anhand des nächsten Home-Assistant-Kalendertermins
- Auswahl der Priorität: Kalender zuerst oder tägliche Uhrzeit zuerst
- Fallback auf tägliche Fertig-Uhrzeit, wenn Kalender zuerst gewählt ist und kein Kalendertermin verfügbar ist
- Eigene Zahl-Entität für den Ziel-Ladestand (`number.*`)
- Bei Ziel-Ladestand 100 % wird ein konfigurierbarer Sicherheitsaufschlag zur Ladedauer addiert
- Aktueller Akkustand direkt im Config Flow auswählbar
- Deutsche und englische Übersetzungen
- Icon, Logo und Brand-Dateien enthalten

## Beispielwerte für Cupra Leon e-Hybrid

| Einstellung | Beispiel |
|---|---:|
| Batteriegröße | `19.7` kWh |
| Ladeleistung | `10.5` kW |
| Ladeeffizienz | `0.93` |
| Puffer | `30` Minuten |
| Zusätzliche Ladezeit bei 100 % Ziel-Ladestand | `10` Minuten |

## Berechnung

```text
soc_diff = target_soc - current_soc
kwh_needed = (soc_diff / 100) * battery_size_kwh / efficiency
duration_minutes = ceil((kwh_needed / charge_power_kw) * 60)
if target_soc >= 100 and duration_minutes > 0:
    duration_minutes = duration_minutes + full_charge_extra_minutes
planned_end = ready_by - buffer_minutes
planned_start = planned_end - duration_minutes
```

## Kalender-Funktion

Optional kann im Config Flow ein Kalender angegeben werden, zum Beispiel:

```text
calendar.cupra_ladung
```

Zusätzlich wählst du im Config Flow die Priorität:

```text
Kalendertermin zuerst
```

oder:

```text
Tägliche Nacht-Uhrzeit zuerst
```

Bei `Kalendertermin zuerst` verwendet die Integration den nächsten Kalendertermin als Ziel-Zeitpunkt, sofern einer verfügbar ist. Bei `Tägliche Nacht-Uhrzeit zuerst` verwendet sie die tägliche Fertig-Uhrzeit als Hauptquelle.

Beispiel mit `Kalendertermin zuerst`:

- Termin im Kalender: `Morgen 08:00 Uhr`
- Puffer: `30 Minuten`
- Benötigte Ladedauer: `90 Minuten`

Ergebnis:

```text
Ladeziel Zeitpunkt: Morgen 08:00 Uhr
Geplantes Ladeende: Morgen 07:30 Uhr
Geplanter Ladestart: Morgen 06:00 Uhr
```

Wenn `Kalendertermin zuerst` gewählt ist und kein Kalender eingetragen ist oder kein Kalendertermin mit `start_time` verfügbar ist, nutzt die Integration die tägliche Fertig-Uhrzeit. Wenn `Tägliche Nacht-Uhrzeit zuerst` gewählt ist, wird die tägliche Fertig-Uhrzeit direkt verwendet.

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
| Ladeziel Priorität | `Kalendertermin zuerst` oder `Tägliche Nacht-Uhrzeit zuerst` |
| Ladeplan Status | `not_needed`, `waiting`, `charging_window` oder `late` |

Zusätzlich wird eine Zahl-Entität erstellt:

| Entität | Bedeutung |
|---|---|
| Ziel-Ladestand | Ziel-SOC in Prozent, den du später direkt in Home Assistant ändern kannst |


### Sicherheitsaufschlag bei 100 %

Wenn der Ziel-Ladestand auf **100 %** steht und tatsächlich noch geladen werden muss, addiert die Integration den im Config Flow eingestellten Sicherheitsaufschlag zur berechneten Ladedauer. Die Einstellung heißt **Zusätzliche Ladezeit bei 100 % Ziel-Ladestand**. Standardwert: **10 Minuten**. Dadurch startet die Ladung entsprechend früher beziehungsweise bleibt entsprechend länger im Ladefenster, damit das Auto wirklich voll wird.

### Feste Ladedauer im laufenden Ladefenster

Sobald das Ladefenster einmal erreicht wurde, wird die zu diesem Zeitpunkt berechnete **Benötigte Ladedauer** eingefroren. Während des laufenden Ladefensters wird die Dauer nicht mehr durch steigenden SOC neu berechnet oder verkürzt.

Der Status bleibt für genau diese eingefrorene Ladedauer auf `charging_window`. Danach wechselt der Status für dieses Ladeziel direkt auf `not_needed`.

Zusätzliche Diagnose-Attribute:

```text
locked_duration_minutes
locked_charge_started_at
locked_charge_finished_at
```

## Installation

1. Kopiere den Ordner `custom_components/ev_and_battery_charger` nach Home Assistant.
2. Starte Home Assistant neu.
3. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen**.
4. Suche nach **EV and Battery Charger**.
5. Wähle den aktuellen Ladestand, optional den Kalender und trage deine Ladeparameter inklusive **Zusätzliche Ladezeit bei 100 % Ziel-Ladestand** ein.
6. Danach kannst du den Ziel-Ladestand über die neue Entität **Ziel-Ladestand** ändern.

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


Version: 1.0.13
