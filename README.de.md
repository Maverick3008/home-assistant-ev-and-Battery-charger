# EV and Battery Charger

## Version 1.5.1 – einfacher 03:00-Uhr-Kalender-Fallback

Version **1.5.1** ergänzt einen bewusst einfachen Sicherheits-Fallback für den Fall, dass der SOC-Wert des Fahrzeugs nicht korrekt aktualisiert wird:

- Ab **03:00 Uhr** wird geprüft, ob **heute noch ein zukünftiger Kalendertermin** vorhanden ist.
- Ergibt der normale Ladeplan zu diesem Zeitpunkt `not_needed` / **Nicht nötig**, wird der SOC für diesen Fallback ignoriert.
- Der Ladeplan-Status wird auf **`charging_window` / Ladefenster** gesetzt.
- `planned_start` wird auf **03:00 Uhr** gesetzt.
- `planned_end` wird auf den **Start des nächsten Kalendertermins heute** gesetzt.
- Die angezeigte Ladedauer entspricht in diesem Fall nur dem Zeitfenster von 03:00 Uhr bis zum Termin und wird **nicht aus dem SOC berechnet**.
- Sobald der Termin beginnt, endet der Fallback automatisch.
- Gibt es heute keinen zukünftigen Termin oder lautet der normale Status nicht `not_needed`, greift der Fallback nicht.

Damit kann eine bestehende Wallbox-Automation auf `charging_window` reagieren und das Fahrzeug vorsorglich laden, auch wenn der gemeldete SOC fälschlich suggeriert, dass keine Ladung nötig ist.

Zusätzliche Diagnose-Attribute:

```text
calendar_fallback_active
calendar_fallback_reason
calendar_fallback_start
```

## Version 1.5.0 – mehrere Kalender

**EV and Battery Charger** ist eine Home-Assistant-Custom-Integration zur Berechnung der Ladedauer, des geplanten Ladestarts und des geplanten Ladeendes für E-Autos, Plug-in-Hybride oder Batteriespeicher.

Ab **Version 1.5.0** können im Config Flow **mehrere Home-Assistant-Kalender** ausgewählt werden. Die Integration prüft alle ausgewählten Kalender und verwendet für die Ladeplanung den **zeitlich frühesten zukünftigen Termin**.

### Verhalten bei mehreren Kalendern

- Im Config Flow können mehrere `calendar.*`-Entitäten ausgewählt werden.
- Alle ausgewählten Kalender werden alle **30 Minuten** über `homeassistant.update_entity` aktualisiert.
- Aus allen Kalendern wird der **früheste zukünftige Termin** verwendet.
- Bei zwei Terminen mit identischer Startzeit entscheidet die Reihenfolge der ausgewählten Kalender.
- Bestehende Installationen mit nur einem Kalender bleiben kompatibel; der bisher gespeicherte Einzelwert wird automatisch als Liste behandelt.
- Das Sensorattribut `calendar_entities` zeigt alle ausgewählten Kalender.
- Das bestehende Attribut `calendar_entity` zeigt weiterhin den Kalender, aus dem der aktuell verwendete Termin stammt.

## Kalender- und Ziel-Ladestand-Logik

Die bestehende Logik aus Version 1.4.1 bleibt erhalten:

- Ein geeigneter Termin **morgen** darf den Ziel-Ladestand erst auf **100 %** setzen, nachdem die heutige konfigurierte tägliche Fertig-Uhrzeit erreicht wurde.
- Termine übermorgen oder später lösen noch keine 100-%-Umschaltung aus.
- Ein bereits aktivierter Termin behält 100 % auch nach Mitternacht bis zum Abschluss des zugehörigen Ladezyklus.
- Danach wird der Ziel-Ladestand automatisch wieder auf **80 %** gesetzt.
- Bei 100 % kann ein konfigurierbarer Sicherheitsaufschlag zur Ladedauer addiert werden.

## Ladeziel-Priorität

Du kannst zwischen zwei Varianten wählen:

**Kalendertermin zuerst**
: Der früheste zukünftige Termin aus allen ausgewählten Kalendern wird als Ladeziel verwendet. Ist kein zukünftiger Termin vorhanden, wird die tägliche Fertig-Uhrzeit verwendet.

**Nacht-Uhrzeit bevorzugt (frühere Termine zuerst)**
: Normalerweise wird die tägliche Fertig-Uhrzeit verwendet. Liegt der früheste Kalendertermin davor, übernimmt dieser automatisch das Ladeziel.

## Funktionen

- Benötigte Ladedauer in Minuten
- Benötigte Energie in kWh
- Geplanter Ladestart
- Geplantes Ladeende mit Puffer
- Eigene Zahl-Entität für den Ziel-Ladestand
- Mehrere optionale Kalender
- Frühesten zukünftigen Termin kalenderübergreifend bestimmen
- Automatische Aktualisierung der ausgewählten Kalender alle 30 Minuten
- Automatische 100-%-/80-%-Kalenderlogik
- Feste Ladedauer nach Start eines Ladefensters
- Deutsche und englische Übersetzungen
- HACS-Unterstützung

## Beispielwerte Cupra Leon e-Hybrid

| Einstellung | Beispiel |
|---|---:|
| Batteriegröße | `19.7` kWh |
| Ladeleistung | `10.5` kW |
| Ladeeffizienz | `0.93` |
| Puffer | `30` Minuten |
| Zusätzliche Ladezeit bei 100 % | `10` Minuten |

## Berechnung

```text
soc_diff = target_soc - current_soc
kwh_needed = (soc_diff / 100) * battery_size_kwh / efficiency
duration_minutes = ceil((kwh_needed / charge_power_kw) * 60)

if target_soc >= 100 and duration_minutes > 0:
    duration_minutes += full_charge_extra_minutes

planned_end = ready_by - buffer_minutes
planned_start = planned_end - duration_minutes
```

## Entstehende Sensoren

| Sensor | Bedeutung |
|---|---|
| Benötigte Ladedauer | Ladedauer in Minuten |
| Ladeziel Zeitpunkt | Verwendeter Ziel-Zeitpunkt |
| Geplanter Ladestart | Geplanter Start der Ladung |
| Geplantes Ladeende | Geplantes Ende vor dem Puffer |
| Benötigte Energie | Geschätzte Energie in kWh |
| Nächster Kalendertermin Start | Start des frühesten Kalendertermins |
| Nächster Kalendertermin | Titel des frühesten Kalendertermins |
| Ladeziel Quelle | `daily_time` oder `calendar` |
| Ladeziel Priorität | Gewählte Prioritätslogik |
| Ladeplan Status | `not_needed`, `waiting`, `charging_window` oder `late` |

Zusätzlich wird die Zahl-Entität **Ziel-Ladestand** erstellt.

## Installation

1. Den Ordner `custom_components/ev_and_battery_charger` nach Home Assistant kopieren oder die Integration über HACS installieren.
2. Home Assistant neu starten.
3. **Einstellungen → Geräte & Dienste → Integration hinzufügen**.
4. **EV and Battery Charger** auswählen.
5. SOC-Sensor, tägliche Fertig-Uhrzeit, Ladeparameter und optional mehrere Kalender auswählen.

## Update von 1.4.1

Die vorhandene Konfiguration muss nicht gelöscht werden. Ein bislang gespeicherter einzelner Kalender wird von 1.5.0 automatisch weiterverwendet. Öffnest du anschließend die Optionen der Integration, kannst du weitere Kalender ergänzen.

## Release

Integrationsversion: **1.5.1**

Für HACS sollte nach dem Upload der Dateien ein GitHub-Release/Tag **`1.5.1`** erstellt werden.
