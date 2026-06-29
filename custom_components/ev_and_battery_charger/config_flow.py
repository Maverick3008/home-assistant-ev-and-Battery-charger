"""Config flow for EV and Battery Charger."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.util import slugify

from .const import (
    CONF_BATTERY_SIZE_KWH,
    CONF_BUFFER_MINUTES,
    CONF_CALENDAR_ENTITY,
    CONF_CHARGE_POWER_KW,
    CONF_EFFICIENCY,
    CONF_NAME,
    CONF_SOC_SENSOR,
    CONF_TARGET_SOC_ENTITY,
    CONF_TARGET_TIME,
    DEFAULT_BATTERY_SIZE_KWH,
    DEFAULT_BUFFER_MINUTES,
    DEFAULT_CALENDAR_ENTITY,
    DEFAULT_CHARGE_POWER_KW,
    DEFAULT_EFFICIENCY,
    DEFAULT_NAME,
    DEFAULT_TARGET_TIME,
    DOMAIN,
)


def _required_key(key: str, default: Any | None = None) -> vol.Required:
    """Return a required schema key, optionally with a default value."""
    if default is None:
        return vol.Required(key)
    return vol.Required(key, default=default)


def _build_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build the config/options schema.

    This intentionally uses plain schema fields instead of advanced selectors.
    That keeps the config flow compatible with more Home Assistant versions and
    avoids frontend 400 errors caused by selector serialization differences.
    """
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_NAME,
                default=defaults.get(CONF_NAME, DEFAULT_NAME),
            ): str,
            _required_key(
                CONF_SOC_SENSOR,
                defaults.get(CONF_SOC_SENSOR),
            ): str,
            _required_key(
                CONF_TARGET_SOC_ENTITY,
                defaults.get(CONF_TARGET_SOC_ENTITY),
            ): str,
            vol.Required(
                CONF_TARGET_TIME,
                default=defaults.get(CONF_TARGET_TIME, DEFAULT_TARGET_TIME),
            ): str,
            vol.Optional(
                CONF_CALENDAR_ENTITY,
                default=defaults.get(CONF_CALENDAR_ENTITY, DEFAULT_CALENDAR_ENTITY),
            ): str,
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


def _validate_input(user_input: dict[str, Any]) -> dict[str, str]:
    """Validate user input and return config flow errors."""
    errors: dict[str, str] = {}

    name = str(user_input.get(CONF_NAME, "")).strip()
    if not name:
        errors[CONF_NAME] = "empty_name"

    soc_sensor = str(user_input.get(CONF_SOC_SENSOR, "")).strip()
    if "." not in soc_sensor:
        errors[CONF_SOC_SENSOR] = "invalid_entity"

    target_soc_entity = str(user_input.get(CONF_TARGET_SOC_ENTITY, "")).strip()
    if "." not in target_soc_entity:
        errors[CONF_TARGET_SOC_ENTITY] = "invalid_entity"

    calendar_entity = str(user_input.get(CONF_CALENDAR_ENTITY, "")).strip()
    if calendar_entity and not calendar_entity.startswith("calendar."):
        errors[CONF_CALENDAR_ENTITY] = "invalid_calendar_entity"

    target_time = str(user_input.get(CONF_TARGET_TIME, "")).strip()
    try:
        parts = [int(part) for part in target_time.split(":")]
        if len(parts) not in (2, 3):
            raise ValueError
        hour, minute = parts[0], parts[1]
        second = parts[2] if len(parts) == 3 else 0
        if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
            raise ValueError
    except (TypeError, ValueError):
        errors[CONF_TARGET_TIME] = "invalid_time"

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


def _normalize_input(user_input: dict[str, Any]) -> dict[str, Any]:
    """Normalize text values before storing them."""
    normalized = dict(user_input)
    normalized[CONF_NAME] = str(normalized.get(CONF_NAME, "")).strip()
    normalized[CONF_SOC_SENSOR] = str(normalized.get(CONF_SOC_SENSOR, "")).strip()
    normalized[CONF_TARGET_SOC_ENTITY] = str(normalized.get(CONF_TARGET_SOC_ENTITY, "")).strip()
    normalized[CONF_TARGET_TIME] = str(normalized.get(CONF_TARGET_TIME, "")).strip()
    normalized[CONF_CALENDAR_ENTITY] = str(normalized.get(CONF_CALENDAR_ENTITY, "")).strip()
    return normalized


class EVAndBatteryChargerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EV and Battery Charger."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input = _normalize_input(user_input)
            errors = _validate_input(user_input)
            if not errors:
                await self.async_set_unique_id(slugify(user_input[CONF_NAME]))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(user_input),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle Home Assistant's reconfigure action for an existing entry."""
        entry_id = self.context.get("entry_id")
        entry = self.hass.config_entries.async_get_entry(entry_id) if entry_id else None
        if entry is None:
            return self.async_abort(reason="unknown_entry")

        current = {**entry.data, **entry.options}
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input = _normalize_input(user_input)
            errors = _validate_input(user_input)
            if not errors:
                self.hass.config_entries.async_update_entry(
                    entry,
                    title=user_input[CONF_NAME],
                    data=user_input,
                    options={},
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reconfigure_successful")

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_build_schema(user_input or current),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> EVAndBatteryChargerOptionsFlow:
        """Create the options flow."""
        return EVAndBatteryChargerOptionsFlow(config_entry)


class EVAndBatteryChargerOptionsFlow(config_entries.OptionsFlow):
    """Handle EV and Battery Charger options."""

    def __init__(self, config_entry: config_entries.ConfigEntry | None = None) -> None:
        """Initialize the options flow.

        Passing the config entry explicitly keeps the flow compatible with Home
        Assistant versions where OptionsFlow does not automatically expose it.
        """
        self._config_entry = config_entry

    def _entry(self) -> config_entries.ConfigEntry | None:
        """Return the config entry for this options flow."""
        if self._config_entry is not None:
            return self._config_entry
        return getattr(self, "config_entry", None)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        entry = self._entry()
        if entry is None:
            return self.async_abort(reason="unknown_entry")

        errors: dict[str, str] = {}

        if user_input is not None:
            user_input = _normalize_input(user_input)
            errors = _validate_input(user_input)
            if not errors:
                return self.async_create_entry(title="", data=user_input)

        current = {**entry.data, **entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(user_input or current),
            errors=errors,
        )
