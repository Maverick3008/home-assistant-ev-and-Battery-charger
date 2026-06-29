# EV and Battery Charger / EV- und Batterie-Ladeplaner

Custom integration for Home Assistant that calculates the charging duration, planned charging start and planned charging end for an EV, plug-in hybrid or battery storage system.

Custom Integration für Home Assistant, die die Ladedauer, den geplanten Ladestart und das geplante Ladeende für ein E-Auto, Plug-in-Hybrid-Fahrzeug oder einen Batteriespeicher berechnet.

---

## English

### What it does

The integration uses:

- current state of charge in percent
- target charge helper, usually an `input_number`
- daily ready-by time
- battery size in kWh
- charging power in kW
- charging efficiency factor
- buffer before the ready-by time, default `30 min`

It creates these sensors:

| Sensor | Unit | Description |
|---|---:|---|
| Required charge duration | min | Charging time needed to reach the target charge. |
| Planned charge start | timestamp | Start time calculated from planned end minus required duration. |
| Planned charge end | timestamp | Ready-by time minus buffer. |
| Energy needed | kWh | Estimated energy needed including charging losses. |
| Charge plan status | text | `not_needed`, `waiting`, `charging_window` or `late`. |

### Formula

```text
soc_difference = max(target_soc - current_soc, 0)
energy_needed_kwh = (soc_difference / 100) * battery_size_kwh / efficiency
duration_minutes = ceil((energy_needed_kwh / charge_power_kw) * 60)
planned_end = next_daily_ready_by_time - buffer_minutes
planned_start = planned_end - duration_minutes
```

Example with your Cupra values:

```text
battery_size_kwh = 19.7
charge_power_kw = 10.5
efficiency = 0.93
buffer_minutes = 30
```

### Installation

#### Manual installation

1. Copy the folder `custom_components/ev_and_battery_charger` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration**.
4. Search for **EV and Battery Charger**.
5. Select your current SOC sensor and your target charge helper.

#### HACS custom repository

1. Open HACS.
2. Go to **Integrations → three-dot menu → Custom repositories**.
3. Add your GitHub repository URL.
4. Select category **Integration**.
5. Install **EV and Battery Charger**.
6. Restart Home Assistant.

### Target charge helper

Create an `input_number` helper in Home Assistant:

```yaml
input_number:
  cupra_target_charge:
    name: Cupra Target Charge
    min: 0
    max: 100
    step: 1
    unit_of_measurement: "%"
```

In the UI you can also create this via **Settings → Devices & services → Helpers → Create helper → Number**.

### Automation example

Start charging at the calculated start time:

```yaml
alias: Start charging from EV and Battery Charger
triggers:
  - trigger: time
    at: sensor.cupra_leon_planned_charge_start
actions:
  - action: select.select_option
    target:
      entity_id: select.myenergi_zappi_24278485_charge_mode
    data:
      option: Fast
mode: single
```

Stop charging at the calculated planned end:

```yaml
alias: Stop charging from EV and Battery Charger
triggers:
  - trigger: time
    at: sensor.cupra_leon_planned_charge_end
actions:
  - action: select.select_option
    target:
      entity_id: select.myenergi_zappi_24278485_charge_mode
    data:
      option: Stopped
mode: single
```

Adjust the entity IDs to your own setup.

---

## Deutsch

### Was macht die Integration?

Die Integration verwendet:

- aktuellen Akkustand in Prozent
- Ziel-Ladestand-Helper, normalerweise ein `input_number`
- tägliche Fertig-Uhrzeit
- Batteriegröße in kWh
- Ladeleistung in kW
- Ladeeffizienz-Faktor
- Puffer vor der Fertig-Uhrzeit, Standard `30 min`

Sie erstellt diese Sensoren:

| Sensor | Einheit | Beschreibung |
|---|---:|---|
| Benötigte Ladedauer | min | Benötigte Ladezeit bis zum Ziel-Ladestand. |
| Geplanter Ladestart | Zeitstempel | Ladebeginn aus Ladeende minus benötigter Ladedauer. |
| Geplantes Ladeende | Zeitstempel | Fertig-Uhrzeit minus Puffer. |
| Benötigte Energie | kWh | Geschätzte Energiemenge inklusive Ladeverlusten. |
| Ladeplan Status | Text | `not_needed`, `waiting`, `charging_window` oder `late`. |

### Formel

```text
soc_differenz = max(ziel_soc - aktueller_soc, 0)
benötigte_energie_kwh = (soc_differenz / 100) * batteriegröße_kwh / effizienz
ladedauer_minuten = ceil((benötigte_energie_kwh / ladeleistung_kw) * 60)
geplantes_ladeende = nächste_tägliche_fertig_uhrzeit - puffer_minuten
geplanter_ladestart = geplantes_ladeende - ladedauer_minuten
```

Beispiel mit deinen Cupra-Werten:

```text
battery_size_kwh = 19.7
charge_power_kw = 10.5
efficiency = 0.93
buffer_minutes = 30
```

Ich nutze `ceil`, also Aufrunden auf volle Minuten. Dadurch startet die Ladung lieber etwas früher als zu spät.

### Installation

#### Manuelle Installation

1. Kopiere den Ordner `custom_components/ev_and_battery_charger` in deinen Home-Assistant-Ordner `custom_components`.
2. Starte Home Assistant neu.
3. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen**.
4. Suche nach **EV and Battery Charger**.
5. Wähle deinen aktuellen SOC-Sensor und deinen Ziel-Ladestand-Helper aus.

#### HACS Custom Repository

1. Öffne HACS.
2. Gehe zu **Integrationen → Drei-Punkte-Menü → Benutzerdefinierte Repositories**.
3. Füge die URL deines GitHub-Repositories ein.
4. Wähle Kategorie **Integration**.
5. Installiere **EV and Battery Charger**.
6. Starte Home Assistant neu.

### Ziel-Ladestand-Helper

Lege einen `input_number`-Helper in Home Assistant an:

```yaml
input_number:
  cupra_ziel_ladestand:
    name: Cupra Ziel-Ladestand
    min: 0
    max: 100
    step: 1
    unit_of_measurement: "%"
```

Über die UI geht das auch unter **Einstellungen → Geräte & Dienste → Helfer → Helfer erstellen → Zahl**.

### Automationsbeispiel

Ladung zum berechneten Startzeitpunkt starten:

```yaml
alias: Cupra Ladung nach EV and Battery Charger starten
triggers:
  - trigger: time
    at: sensor.cupra_leon_geplanter_ladestart
actions:
  - action: select.select_option
    target:
      entity_id: select.myenergi_zappi_24278485_charge_mode
    data:
      option: Fast
mode: single
```

Ladung zum berechneten Ladeende stoppen:

```yaml
alias: Cupra Ladung nach EV and Battery Charger stoppen
triggers:
  - trigger: time
    at: sensor.cupra_leon_geplantes_ladeende
actions:
  - action: select.select_option
    target:
      entity_id: select.myenergi_zappi_24278485_charge_mode
    data:
      option: Stopped
mode: single
```

Passe die Entity-IDs an deine Umgebung an.

## Icons / Logo

The repository includes `icon.png`, `logo.png` and `icon.svg` for GitHub/HACS branding. Die Entitäts-Icons sind zusätzlich über `icons.json` definiert.
