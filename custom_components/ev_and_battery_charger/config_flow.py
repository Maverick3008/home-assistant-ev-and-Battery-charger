"""Config flow for EV and Battery Charger."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.util import slugify

from .const import (
    CONF_BATTERY_SIZE_KWH,
    CONF_BUFFER_MINUTES,
    CONF_CALENDAR_ENTITY,
    CONF_CHARGE_POWER_KW,
    CONF_EFFICIENCY,
    CONF_NAME,
    CONF_SOC_SENSOR,
    CONF_TARGET_SOC,
    CONF_TARGET_SOURCE_PRIORITY,
    CONF_TARGET_TIME,
    DEFAULT_BATTERY_SIZE_KWH,
    DEFAULT_BUFFER_MINUTES,
    DEFAULT_CALENDAR_ENTITY,
    DEFAULT_CHARGE_POWER_KW,
    DEFAULT_EFFICIENCY,
    DEFAULT_NAME,
    DEFAULT_TARGET_SOC,
    DEFAULT_TARGET_SOURCE_PRIORITY,
    DEFAULT_TARGET_TIME,
    DOMAIN,
    TARGET_SOURCE_PRIORITY_OPTIONS,
)


def _target_priority_selector() -> selector.SelectSelector:
    """Return the target source priority selector with translated labels."""
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=list(TARGET_SOURCE_PRIORITY_OPTIONS),
            translation_key=CONF_TARGET_SOURCE_PRIORITY,
        )
    )


def _soc_entity_selector() -> selector.EntitySelector:
    """Return selector for entities that can provide a SOC percentage."""
    return selector.EntitySelector(
        selector.EntitySelectorConfig(domain=["sensor", "number", "input_number"])
    )


def _calendar_entity_selector() -> selector.EntitySelector:
    """Return selector for a Home Assistant calendar entity."""
    return selector.EntitySelector(selector.EntitySelectorConfig(domain="calendar"))


def _target_soc_selector() -> selector.NumberSelector:
    """Return selector for the internal target SOC number."""
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=0,
            max=100,
            step=1,
            unit_of_measurement="%",
        )
    )


def _build_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build the config/options schema."""
    defaults = defaults or {}
    schema: dict[Any, Any] = {
        vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, DEFAULT_NAME)): str,
    }

    soc_default = defaults.get(CONF_SOC_SENSOR)
    if soc_default:
        schema[vol.Required(CONF_SOC_SENSOR, default=soc_default)] = _soc_entity_selector()
    else:
        schema[vol.Required(CONF_SOC_SENSOR)] = _soc_entity_selector()

    schema.update(
        {
            vol.Required(
                CONF_TARGET_SOC,
                default=defaults.get(CONF_TARGET_SOC, DEFAULT_TARGET_SOC),
            ): _target_soc_selector(),
            vol.Required(
                CONF_TARGET_TIME,
                default=defaults.get(CONF_TARGET_TIME, DEFAULT_TARGET_TIME),
            ): selector.TimeSelector(),
            vol.Required(
                CONF_TARGET_SOURCE_PRIORITY,
                default=defaults.get(CONF_TARGET_SOURCE_PRIORITY, DEFAULT_TARGET_SOURCE_PRIORITY),
            ): _target_priority_selector(),
            vol.Required(
                CONF_BATTERY_SIZE_KWH,
                default=defaults.get(CONF_BATTERY_SIZE_KWH, DEFAULT_BATTERY_SIZE_KWH),
            ): vol.Coerce(float),
            vol.Required(
                CONF_CHARGE_POWER_KW,
                default=defaults.get(CONF_CHARGE_POWER_KW, DEFAULT_CHARGE_POWER_KW),
            ): vol.Coerce(float),
            vol.Required(
                CONF_EFFICIENCY,
                default=defaults.get(CONF_EFFICIENCY, DEFAULT_EFFICIENCY),
            ): vol.Coerce(float),
            vol.Required(
                CONF_BUFFER_MINUTES,
                default=defaults.get(CONF_BUFFER_MINUTES, DEFAULT_BUFFER_MINUTES),
            ): vol.Coerce(int),
        }
    )

    calendar_default = defaults.get(CONF_CALENDAR_ENTITY, DEFAULT_CALENDAR_ENTITY)
    if calendar_default:
        schema[vol.Optional(CONF_CALENDAR_ENTITY, default=calendar_default)] = _calendar_entity_selector()
    else:
        schema[vol.Optional(CONF_CALENDAR_ENTITY)] = _calendar_entity_selector()

    return vol.Schema(schema)

def _as_float(user_input: dict[str, Any], key: str) -> float | None:
    """Return a float from user input, or None if conversion fails."""
    try:
        return float(user_input.get(key))
    except (TypeError, ValueError):
        return None


def _as_int(user_input: dict[str, Any], key: str) -> int | None:
    """Return an int from user input, or None if conversion fails."""
    try:
        return int(float(user_input.get(key)))
    except (TypeError, ValueError):
        return None


def _validate_time(value: Any) -> bool:
    """Validate a time selector or text time value."""
    if hasattr(value, "hour") and hasattr(value, "minute"):
        return True
    try:
        parts = [int(part) for part in str(value).split(":")]
        if len(parts) not in (2, 3):
            return False
        hour, minute = parts[0], parts[1]
        second = parts[2] if len(parts) == 3 else 0
        return 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59
    except (TypeError, ValueError):
        return False


def _validate_input(user_input: dict[str, Any]) -> dict[str, str]:
    """Validate user input and return config flow errors."""
    errors: dict[str, str] = {}

    name = str(user_input.get(CONF_NAME, "")).strip()
    if not name:
        errors[CONF_NAME] = "empty_name"

    soc_sensor = str(user_input.get(CONF_SOC_SENSOR, "")).strip()
    if "." not in soc_sensor:
        errors[CONF_SOC_SENSOR] = "invalid_entity"

    target_soc = _as_float(user_input, CONF_TARGET_SOC)
    if target_soc is None:
        errors[CONF_TARGET_SOC] = "invalid_number"
    elif not (0 <= target_soc <= 100):
        errors[CONF_TARGET_SOC] = "invalid_target_soc"

    calendar_entity = str(user_input.get(CONF_CALENDAR_ENTITY, "") or "").strip()
    if calendar_entity and not calendar_entity.startswith("calendar."):
        errors[CONF_CALENDAR_ENTITY] = "invalid_calendar_entity"

    if not _validate_time(user_input.get(CONF_TARGET_TIME, "")):
        errors[CONF_TARGET_TIME] = "invalid_time"

    target_source_priority = str(
        user_input.get(CONF_TARGET_SOURCE_PRIORITY, DEFAULT_TARGET_SOURCE_PRIORITY)
    ).strip()
    if target_source_priority not in TARGET_SOURCE_PRIORITY_OPTIONS:
        errors[CONF_TARGET_SOURCE_PRIORITY] = "invalid_target_source_priority"

    battery_size = _as_float(user_input, CONF_BATTERY_SIZE_KWH)
    if battery_size is None:
        errors[CONF_BATTERY_SIZE_KWH] = "invalid_number"
    elif battery_size <= 0:
        errors[CONF_BATTERY_SIZE_KWH] = "must_be_positive"

    charge_power = _as_float(user_input, CONF_CHARGE_POWER_KW)
    if charge_power is None:
        errors[CONF_CHARGE_POWER_KW] = "invalid_number"
    elif charge_power <= 0:
        errors[CONF_CHARGE_POWER_KW] = "must_be_positive"

    efficiency = _as_float(user_input, CONF_EFFICIENCY)
    if efficiency is None:
        errors[CONF_EFFICIENCY] = "invalid_number"
    elif not (0 < efficiency <= 1):
        errors[CONF_EFFICIENCY] = "invalid_efficiency"

    buffer_minutes = _as_int(user_input, CONF_BUFFER_MINUTES)
    if buffer_minutes is None:
        errors[CONF_BUFFER_MINUTES] = "invalid_number"
    elif buffer_minutes < 0:
        errors[CONF_BUFFER_MINUTES] = "must_not_be_negative"

    return errors


def _normalize_time(value: Any) -> str:
    """Normalize a time selector value to HH:MM:SS."""
    if hasattr(value, "hour") and hasattr(value, "minute"):
        second = getattr(value, "second", 0)
        return f"{value.hour:02d}:{value.minute:02d}:{second:02d}"
    text = str(value).strip()
    parts = text.split(":")
    if len(parts) == 2:
        return f"{int(parts[0]):02d}:{int(parts[1]):02d}:00"
    if len(parts) == 3:
        return f"{int(parts[0]):02d}:{int(parts[1]):02d}:{int(parts[2]):02d}"
    return text


def _normalize_input(user_input: dict[str, Any]) -> dict[str, Any]:
    """Normalize values before storing them."""
    normalized = dict(user_input)
    normalized[CONF_NAME] = str(normalized.get(CONF_NAME, "")).strip()
    normalized[CONF_SOC_SENSOR] = str(normalized.get(CONF_SOC_SENSOR, "")).strip()
    normalized[CONF_TARGET_SOC] = float(normalized.get(CONF_TARGET_SOC, DEFAULT_TARGET_SOC))
    normalized[CONF_TARGET_TIME] = _normalize_time(normalized.get(CONF_TARGET_TIME, DEFAULT_TARGET_TIME))
    normalized[CONF_TARGET_SOURCE_PRIORITY] = str(
        normalized.get(CONF_TARGET_SOURCE_PRIORITY, DEFAULT_TARGET_SOURCE_PRIORITY)
    ).strip()
    normalized[CONF_CALENDAR_ENTITY] = str(normalized.get(CONF_CALENDAR_ENTITY, "") or "").strip()
    normalized[CONF_BATTERY_SIZE_KWH] = float(normalized[CONF_BATTERY_SIZE_KWH])
    normalized[CONF_CHARGE_POWER_KW] = float(normalized[CONF_CHARGE_POWER_KW])
    normalized[CONF_EFFICIENCY] = float(normalized[CONF_EFFICIENCY])
    normalized[CONF_BUFFER_MINUTES] = int(float(normalized[CONF_BUFFER_MINUTES]))
    return normalized


def _migrate_defaults(defaults: dict[str, Any]) -> dict[str, Any]:
    """Return defaults compatible with older config entries."""
    migrated = dict(defaults)
    migrated.setdefault(CONF_TARGET_SOC, DEFAULT_TARGET_SOC)
    return migrated


_OPTIONS_FLOW_BASE = getattr(config_entries, "OptionsFlowWithReload", config_entries.OptionsFlow)


class EVAndBatteryChargerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EV and Battery Charger."""

    VERSION = 1
    MINOR_VERSION = 11

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = _validate_input(user_input)
            if not errors:
                user_input = _normalize_input(user_input)
                await self.async_set_unique_id(slugify(user_input[CONF_NAME]))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(_migrate_defaults(user_input or {})),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle Home Assistant's reconfigure action for an existing entry."""
        entry = self._get_reconfigure_entry()
        current = _migrate_defaults({**entry.data, **entry.options})
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = _validate_input(user_input)
            if not errors:
                user_input = _normalize_input(user_input)
                await self.async_set_unique_id(entry.unique_id or slugify(user_input[CONF_NAME]))
                self._abort_if_unique_id_mismatch()
                if hasattr(self, "async_update_reload_and_abort"):
                    return self.async_update_reload_and_abort(
                        entry,
                        data_updates=user_input,
                        title=user_input[CONF_NAME],
                        reason="reconfigure_successful",
                    )

                self.hass.config_entries.async_update_entry(
                    entry,
                    data=user_input,
                    title=user_input[CONF_NAME],
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reconfigure_successful")

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_build_schema(_migrate_defaults(user_input or current)),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> EVAndBatteryChargerOptionsFlow:
        """Create the options flow."""
        return EVAndBatteryChargerOptionsFlow()


class EVAndBatteryChargerOptionsFlow(_OPTIONS_FLOW_BASE):
    """Handle EV and Battery Charger options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = _validate_input(user_input)
            if not errors:
                user_input = _normalize_input(user_input)
                return self.async_create_entry(title="", data=user_input)

        current = _migrate_defaults({**self.config_entry.data, **self.config_entry.options})
        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(_migrate_defaults(user_input or current)),
            errors=errors,
        )
