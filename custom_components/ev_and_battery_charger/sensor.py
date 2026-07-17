"""Sensor platform for EV and Battery Charger."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from math import ceil
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTime,
)
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt as dt_util

from .const import (
    CONF_BATTERY_SIZE_KWH,
    CONF_BUFFER_MINUTES,
    CONF_CALENDAR_ENTITY,
    CONF_CHARGE_POWER_KW,
    CONF_EFFICIENCY,
    CONF_FULL_CHARGE_EXTRA_MINUTES,
    CONF_NAME,
    CONF_SOC_SENSOR,
    CONF_TARGET_SOC,
    CONF_TARGET_SOC_ENTITY,
    CONF_TARGET_TIME,
    CONF_TARGET_SOURCE_PRIORITY,
    DEFAULT_BATTERY_SIZE_KWH,
    DEFAULT_BUFFER_MINUTES,
    DEFAULT_CHARGE_POWER_KW,
    DEFAULT_FULL_CHARGE_EXTRA_MINUTES,
    DEFAULT_EFFICIENCY,
    DEFAULT_NAME,
    DEFAULT_TARGET_SOC,
    DEFAULT_TARGET_SOURCE_PRIORITY,
    DEFAULT_TARGET_TIME,
    DOMAIN,
    INVALID_STATES,
    SIGNAL_TARGET_SOC_UPDATED,
    TARGET_PRIORITY_CALENDAR_FIRST,
    TARGET_PRIORITY_DAILY_TIME_FIRST,
    TARGET_SOURCE_CALENDAR,
    TARGET_SOURCE_DAILY_TIME,
)


@dataclass(frozen=True)
class ChargeCalculation:
    """Calculated values for the charging plan."""

    current_soc: float | None
    target_soc: float | None
    soc_diff: float
    battery_size_kwh: float
    charge_power_kw: float
    efficiency: float
    buffer_minutes: int
    target_time: str
    target_source: str
    target_source_priority: str
    calendar_entity: str | None
    calendar_event_title: str | None
    calendar_event_start: datetime | None
    calendar_event_end: datetime | None
    calendar_event_all_day: bool | None
    ready_by: datetime
    planned_end: datetime
    planned_start: datetime
    duration_minutes: int
    exact_duration_minutes: float
    full_charge_extra_minutes: int
    energy_needed_kwh: float
    status: str
    minutes_until_start: int
    minutes_until_end: int
    charging_window_locked: bool
    locked_duration_minutes: int | None
    locked_charge_started_at: datetime | None
    locked_charge_finished_at: datetime | None


@dataclass(frozen=True, kw_only=True)
class EVAndBatteryChargerSensorEntityDescription(SensorEntityDescription):
    """Describe an EV and Battery Charger sensor."""

    value_key: str


SENSOR_DESCRIPTIONS: tuple[EVAndBatteryChargerSensorEntityDescription, ...] = (
    EVAndBatteryChargerSensorEntityDescription(
        key="charge_duration_minutes",
        translation_key="charge_duration_minutes",
        value_key="duration_minutes",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EVAndBatteryChargerSensorEntityDescription(
        key="target_ready_time",
        translation_key="target_ready_time",
        value_key="ready_by",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    EVAndBatteryChargerSensorEntityDescription(
        key="planned_charge_start",
        translation_key="planned_charge_start",
        value_key="planned_start",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    EVAndBatteryChargerSensorEntityDescription(
        key="planned_charge_end",
        translation_key="planned_charge_end",
        value_key="planned_end",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    EVAndBatteryChargerSensorEntityDescription(
        key="energy_needed",
        translation_key="energy_needed",
        value_key="energy_needed_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    EVAndBatteryChargerSensorEntityDescription(
        key="next_calendar_event_start",
        translation_key="next_calendar_event_start",
        value_key="calendar_event_start",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    EVAndBatteryChargerSensorEntityDescription(
        key="next_calendar_event_title",
        translation_key="next_calendar_event_title",
        value_key="calendar_event_title",
        icon="mdi:calendar-text",
    ),
    EVAndBatteryChargerSensorEntityDescription(
        key="target_source",
        translation_key="target_source",
        value_key="target_source",
        device_class=SensorDeviceClass.ENUM,
        options=[TARGET_SOURCE_DAILY_TIME, TARGET_SOURCE_CALENDAR],
        icon="mdi:calendar-sync",
    ),
    EVAndBatteryChargerSensorEntityDescription(
        key="target_source_priority",
        translation_key="target_source_priority",
        value_key="target_source_priority",
        device_class=SensorDeviceClass.ENUM,
        options=[TARGET_PRIORITY_CALENDAR_FIRST, TARGET_PRIORITY_DAILY_TIME_FIRST],
        icon="mdi:source-branch-sync",
    ),
    EVAndBatteryChargerSensorEntityDescription(
        key="charge_plan_status",
        translation_key="charge_plan_status",
        value_key="status",
        device_class=SensorDeviceClass.ENUM,
        options=["not_needed", "waiting", "charging_window", "late"],
        icon="mdi:calendar-clock",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EV and Battery Charger sensors from a config entry."""
    calculator = EVAndBatteryChargerCalculator(hass, entry)
    async_add_entities(
        EVAndBatteryChargerSensor(entry, calculator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class EVAndBatteryChargerCalculator:
    """Calculate charging duration and charging window."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the calculator."""
        self.hass = hass
        self.entry = entry
        self._active_charge_window = False
        self._charge_window_signature: str | None = None
        self._locked_ready_by: datetime | None = None
        self._locked_planned_start: datetime | None = None
        self._locked_planned_end: datetime | None = None
        self._locked_duration_minutes: int | None = None
        self._locked_exact_duration_minutes: float | None = None
        self._locked_energy_needed_kwh: float | None = None
        self._locked_charge_started_at: datetime | None = None
        self._locked_charge_finished_at: datetime | None = None
        self._completed_charge_window_signature: str | None = None

    @property
    def config(self) -> dict[str, Any]:
        """Return merged config entry data and options."""
        return {**self.entry.data, **self.entry.options}

    def _get_float_state(self, entity_id: str) -> float | None:
        """Return an entity state as float."""
        state = self.hass.states.get(entity_id)
        if state is None or state.state in INVALID_STATES:
            return None
        try:
            return float(state.state)
        except (TypeError, ValueError):
            return None

    def _get_target_soc(self) -> float | None:
        """Return the configured target SOC.

        Version 1.0.11 adds an internal number entity for the target SOC. Older
        entries may still contain a target_soc_entity from previous releases;
        that value is used only as a migration fallback until the number entity
        has restored or stored its own value.
        """
        entry_data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        if isinstance(entry_data, dict) and "target_soc" in entry_data:
            try:
                return float(entry_data["target_soc"])
            except (TypeError, ValueError):
                pass

        legacy_target_entity = str(self.config.get(CONF_TARGET_SOC_ENTITY, "") or "").strip()
        if legacy_target_entity:
            legacy_value = self._get_float_state(legacy_target_entity)
            if legacy_value is not None:
                return legacy_value

        try:
            return float(self.config.get(CONF_TARGET_SOC, DEFAULT_TARGET_SOC))
        except (TypeError, ValueError):
            return DEFAULT_TARGET_SOC

    @staticmethod
    def _parse_time(value: str | time) -> time:
        """Parse a Home Assistant time selector value."""
        if isinstance(value, time):
            return value
        parts = [int(part) for part in str(value).split(":")]
        while len(parts) < 3:
            parts.append(0)
        return time(parts[0], parts[1], parts[2])

    @staticmethod
    def _parse_datetime(value: Any, now: datetime) -> datetime | None:
        """Parse a Home Assistant datetime/date value and return local datetime."""
        if value in INVALID_STATES or value is None:
            return None

        if isinstance(value, datetime):
            parsed = value
        elif isinstance(value, date):
            parsed = datetime.combine(value, time.min)
        else:
            parsed = dt_util.parse_datetime(str(value))
            if parsed is None:
                parsed_date = dt_util.parse_date(str(value))
                if parsed_date is None:
                    return None
                parsed = datetime.combine(parsed_date, time.min)

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=now.tzinfo)
        return dt_util.as_local(parsed)

    def _get_calendar_ready_by(self, calendar_entity: str, now: datetime) -> tuple[datetime | None, dict[str, Any]]:
        """Return ready-by datetime from the configured calendar entity."""
        if not calendar_entity:
            return None, {
                "calendar_entity": None,
                "calendar_event_title": None,
                "calendar_event_start": None,
                "calendar_event_end": None,
                "calendar_event_all_day": None,
            }

        state = self.hass.states.get(calendar_entity)
        if state is None:
            return None, {
                "calendar_entity": calendar_entity,
                "calendar_event_title": None,
                "calendar_event_start": None,
                "calendar_event_end": None,
                "calendar_event_all_day": None,
            }

        attrs = state.attributes
        event_start = self._parse_datetime(attrs.get("start_time"), now)

        # A calendar entity can continue exposing the currently running event.
        # Its start_time is then already in the past and must no longer be used
        # as a future ready-by target. Returning no event also activates the
        # configured daily ready-time fallback when calendar priority is used.
        if event_start is None or event_start <= now:
            return None, {
                "calendar_entity": calendar_entity,
                "calendar_event_title": None,
                "calendar_event_start": None,
                "calendar_event_end": None,
                "calendar_event_all_day": None,
            }

        event_end = self._parse_datetime(attrs.get("end_time"), now)
        event_title = attrs.get("message")
        event_all_day = attrs.get("all_day")

        return event_start, {
            "calendar_entity": calendar_entity,
            "calendar_event_title": event_title,
            "calendar_event_start": event_start,
            "calendar_event_end": event_end,
            "calendar_event_all_day": event_all_day,
        }

    def _get_daily_ready_by(self, target_time_value: str | time, now: datetime) -> datetime:
        """Return the next daily ready-by datetime."""
        target_time = self._parse_time(target_time_value)
        ready_by = datetime.combine(now.date(), target_time).replace(tzinfo=now.tzinfo)
        if ready_by <= now:
            ready_by += timedelta(days=1)
        return ready_by

    def calculate(self) -> ChargeCalculation | None:
        """Calculate the current charging plan."""
        config = self.config
        soc_entity = config[CONF_SOC_SENSOR]

        current_soc = self._get_float_state(soc_entity)
        target_soc = self._get_target_soc()
        if current_soc is None or target_soc is None:
            return None

        battery_size_kwh = float(config.get(CONF_BATTERY_SIZE_KWH, DEFAULT_BATTERY_SIZE_KWH))
        charge_power_kw = float(config.get(CONF_CHARGE_POWER_KW, DEFAULT_CHARGE_POWER_KW))
        efficiency = float(config.get(CONF_EFFICIENCY, DEFAULT_EFFICIENCY))
        buffer_minutes = int(float(config.get(CONF_BUFFER_MINUTES, DEFAULT_BUFFER_MINUTES)))
        target_time_value = config.get(CONF_TARGET_TIME, DEFAULT_TARGET_TIME)
        target_source_priority = str(
            config.get(CONF_TARGET_SOURCE_PRIORITY, DEFAULT_TARGET_SOURCE_PRIORITY)
        ).strip()
        if target_source_priority not in (
            TARGET_PRIORITY_CALENDAR_FIRST,
            TARGET_PRIORITY_DAILY_TIME_FIRST,
        ):
            target_source_priority = DEFAULT_TARGET_SOURCE_PRIORITY
        calendar_entity = str(config.get(CONF_CALENDAR_ENTITY, "")).strip()

        now = dt_util.now()
        daily_ready_by = self._get_daily_ready_by(target_time_value, now)
        calendar_ready_by, calendar_details = self._get_calendar_ready_by(calendar_entity, now)

        if target_source_priority == TARGET_PRIORITY_DAILY_TIME_FIRST:
            ready_by = daily_ready_by
            target_source = TARGET_SOURCE_DAILY_TIME
            if ready_by is None and calendar_ready_by is not None:
                ready_by = calendar_ready_by
                target_source = TARGET_SOURCE_CALENDAR
        elif calendar_ready_by is not None:
            ready_by = calendar_ready_by
            target_source = TARGET_SOURCE_CALENDAR
        else:
            ready_by = daily_ready_by
            target_source = TARGET_SOURCE_DAILY_TIME

        planned_end = ready_by - timedelta(minutes=buffer_minutes)

        soc_diff = max(target_soc - current_soc, 0)
        if soc_diff <= 0 or battery_size_kwh <= 0 or charge_power_kw <= 0 or efficiency <= 0:
            energy_needed_kwh = 0.0
            exact_duration_minutes = 0.0
            duration_minutes = 0
        else:
            energy_needed_kwh = (soc_diff / 100) * battery_size_kwh / efficiency
            exact_duration_minutes = (energy_needed_kwh / charge_power_kw) * 60
            duration_minutes = ceil(exact_duration_minutes)

        try:
            configured_full_charge_extra_minutes = int(
                float(
                    config.get(
                        CONF_FULL_CHARGE_EXTRA_MINUTES,
                        DEFAULT_FULL_CHARGE_EXTRA_MINUTES,
                    )
                )
            )
        except (TypeError, ValueError):
            configured_full_charge_extra_minutes = DEFAULT_FULL_CHARGE_EXTRA_MINUTES
        configured_full_charge_extra_minutes = max(configured_full_charge_extra_minutes, 0)
        full_charge_extra_minutes = (
            configured_full_charge_extra_minutes
            if target_soc >= 100 and duration_minutes > 0
            else 0
        )
        if full_charge_extra_minutes:
            exact_duration_minutes += full_charge_extra_minutes
            duration_minutes += full_charge_extra_minutes

        planned_start = planned_end - timedelta(minutes=duration_minutes)

        # Once the charge window has started, freeze the initially calculated
        # duration and wait exactly that runtime. While the window is active, SOC
        # changes must not shorten the remaining duration and must not move the
        # planned start/end times. After the frozen duration has elapsed, this
        # charge cycle is marked as completed and reports "not_needed" until the
        # target signature changes, for example because the next daily ready time
        # or the next calendar event changes.
        charge_window_signature = (
            f"{target_source}|{ready_by.isoformat()}|{target_soc}|"
            f"{target_source_priority}|{calendar_entity}"
        )

        if self._charge_window_signature != charge_window_signature:
            self._active_charge_window = False
            self._charge_window_signature = charge_window_signature
            self._completed_charge_window_signature = None
            self._locked_ready_by = None
            self._locked_planned_start = None
            self._locked_planned_end = None
            self._locked_duration_minutes = None
            self._locked_exact_duration_minutes = None
            self._locked_energy_needed_kwh = None
            self._locked_charge_started_at = None
            self._locked_charge_finished_at = None

        charging_window_locked = False

        if self._completed_charge_window_signature == charge_window_signature:
            status = "not_needed"
            duration_minutes = 0
            exact_duration_minutes = 0.0
            energy_needed_kwh = 0.0
        elif self._active_charge_window:
            locked_finished_at = self._locked_charge_finished_at or planned_end
            locked_duration_minutes = self._locked_duration_minutes or duration_minutes
            locked_exact_duration_minutes = self._locked_exact_duration_minutes or exact_duration_minutes
            locked_energy_needed_kwh = self._locked_energy_needed_kwh or energy_needed_kwh

            if now < locked_finished_at:
                status = "charging_window"
                charging_window_locked = True
                duration_minutes = locked_duration_minutes
                exact_duration_minutes = locked_exact_duration_minutes
                energy_needed_kwh = locked_energy_needed_kwh
                if self._locked_ready_by is not None:
                    ready_by = self._locked_ready_by
                if self._locked_planned_start is not None:
                    planned_start = self._locked_planned_start
                planned_end = locked_finished_at
            else:
                status = "not_needed"
                self._active_charge_window = False
                self._completed_charge_window_signature = charge_window_signature
                duration_minutes = 0
                exact_duration_minutes = 0.0
                energy_needed_kwh = 0.0
        elif duration_minutes == 0:
            status = "not_needed"
        elif now < planned_start:
            status = "waiting"
        elif now <= planned_end:
            status = "charging_window"
            charging_window_locked = True
            self._active_charge_window = True
            self._locked_ready_by = ready_by
            self._locked_planned_start = planned_start
            self._locked_duration_minutes = duration_minutes
            self._locked_exact_duration_minutes = exact_duration_minutes
            self._locked_energy_needed_kwh = energy_needed_kwh
            self._locked_charge_started_at = now
            self._locked_charge_finished_at = now + timedelta(minutes=duration_minutes)
            self._locked_planned_end = self._locked_charge_finished_at
            planned_end = self._locked_charge_finished_at
        else:
            status = "late"

        minutes_until_start = round((planned_start - now).total_seconds() / 60)
        minutes_until_end = round((planned_end - now).total_seconds() / 60)

        return ChargeCalculation(
            current_soc=current_soc,
            target_soc=target_soc,
            soc_diff=soc_diff,
            battery_size_kwh=battery_size_kwh,
            charge_power_kw=charge_power_kw,
            efficiency=efficiency,
            buffer_minutes=buffer_minutes,
            target_time=str(target_time_value),
            target_source=target_source,
            target_source_priority=target_source_priority,
            ready_by=ready_by,
            planned_end=planned_end,
            planned_start=planned_start,
            duration_minutes=duration_minutes,
            exact_duration_minutes=exact_duration_minutes,
            full_charge_extra_minutes=full_charge_extra_minutes,
            energy_needed_kwh=round(energy_needed_kwh, 4),
            status=status,
            minutes_until_start=minutes_until_start,
            minutes_until_end=minutes_until_end,
            charging_window_locked=charging_window_locked,
            locked_duration_minutes=self._locked_duration_minutes,
            locked_charge_started_at=self._locked_charge_started_at,
            locked_charge_finished_at=self._locked_charge_finished_at,
            **calendar_details,
        )


class EVAndBatteryChargerSensor(SensorEntity):
    """Representation of an EV and Battery Charger sensor."""

    entity_description: EVAndBatteryChargerSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        entry: ConfigEntry,
        calculator: EVAndBatteryChargerCalculator,
        description: EVAndBatteryChargerSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        self.entry = entry
        self.calculator = calculator
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=self.calculator.config.get(CONF_NAME, DEFAULT_NAME),
            manufacturer="EV and Battery Charger",
            model="Calendar-aware EV and battery charge planner",
        )

    async def async_added_to_hass(self) -> None:
        """Subscribe to source entity changes and minute ticks."""
        config = self.calculator.config
        watched_entities = [config[CONF_SOC_SENSOR]]
        legacy_target_entity = str(config.get(CONF_TARGET_SOC_ENTITY, "") or "").strip()
        if legacy_target_entity:
            watched_entities.append(legacy_target_entity)
        calendar_entity = str(config.get(CONF_CALENDAR_ENTITY, "")).strip()
        if calendar_entity:
            watched_entities.append(calendar_entity)

        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                watched_entities,
                self._async_source_changed,
            )
        )
        self.async_on_remove(
            async_track_time_interval(
                self.hass,
                self._async_time_changed,
                timedelta(minutes=1),
            )
        )
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{DOMAIN}_{self.entry.entry_id}_{SIGNAL_TARGET_SOC_UPDATED}",
                self._async_target_soc_changed,
            )
        )

    @callback
    def _async_source_changed(self, event: Event) -> None:
        """Handle source entity state changes."""
        self.async_write_ha_state()

    @callback
    def _async_target_soc_changed(self) -> None:
        """Handle target SOC number changes."""
        self.async_write_ha_state()

    @callback
    def _async_time_changed(self, now: datetime) -> None:
        """Handle time changes."""
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return if source values are available."""
        return self.calculator.calculate() is not None

    @property
    def native_value(self) -> StateType | datetime:
        """Return the native value."""
        calculation = self.calculator.calculate()
        if calculation is None:
            return None

        value = getattr(calculation, self.entity_description.value_key)
        if isinstance(value, float):
            if self.entity_description.key == "energy_needed":
                return round(value, 2)
            return round(value, 2)
        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        calculation = self.calculator.calculate()
        if calculation is None:
            return None

        return {
            "current_soc": calculation.current_soc,
            "target_soc": calculation.target_soc,
            "soc_difference": round(calculation.soc_diff, 2),
            "battery_size_kwh": calculation.battery_size_kwh,
            "charge_power_kw": calculation.charge_power_kw,
            "efficiency": calculation.efficiency,
            "buffer_minutes": calculation.buffer_minutes,
            "target_source": calculation.target_source,
            "target_source_priority": calculation.target_source_priority,
            "daily_ready_time": calculation.target_time,
            "ready_by": calculation.ready_by.isoformat(),
            "planned_start": calculation.planned_start.isoformat(),
            "planned_end": calculation.planned_end.isoformat(),
            "duration_minutes_exact": round(calculation.exact_duration_minutes, 2),
            "full_charge_extra_minutes": calculation.full_charge_extra_minutes,
            "energy_needed_kwh": calculation.energy_needed_kwh,
            "status": calculation.status,
            "charging_window_locked": calculation.charging_window_locked,
            "locked_duration_minutes": calculation.locked_duration_minutes,
            "locked_charge_started_at": calculation.locked_charge_started_at.isoformat() if calculation.locked_charge_started_at else None,
            "locked_charge_finished_at": calculation.locked_charge_finished_at.isoformat() if calculation.locked_charge_finished_at else None,
            "minutes_until_start": calculation.minutes_until_start,
            "minutes_until_end": calculation.minutes_until_end,
            "source_soc_entity": self.calculator.config[CONF_SOC_SENSOR],
            "target_soc_source": "integration_number",
            "legacy_target_soc_entity": self.calculator.config.get(CONF_TARGET_SOC_ENTITY),
            "calendar_entity": calculation.calendar_entity,
            "calendar_event_title": calculation.calendar_event_title,
            "calendar_event_start": calculation.calendar_event_start.isoformat() if calculation.calendar_event_start else None,
            "calendar_event_end": calculation.calendar_event_end.isoformat() if calculation.calendar_event_end else None,
            "calendar_event_all_day": calculation.calendar_event_all_day,
            "units": {
                "soc": PERCENTAGE,
                "energy": UnitOfEnergy.KILO_WATT_HOUR,
                "power": UnitOfPower.KILO_WATT,
                "time": UnitOfTime.MINUTES,
            },
        }
