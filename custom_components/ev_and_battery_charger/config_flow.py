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
    CONF_TARGET_SOC_ENTITY,
    CONF_TARGET_SOURCE_PRIORITY,
    CONF_TARGET_TIME,
    DEFAULT_BATTERY_SIZE_KWH,
    DEFAULT_BUFFER_MINUTES,
    DEFAULT_CALENDAR_ENTITY,
    DEFAULT_CHARGE_POWER_KW,
    DEFAULT_EFFICIENCY,
    DEFAULT_NAME,
    DEFAULT_TARGET_SOURCE_PRIORITY,
    DEFAULT_TARGET_TIME,
    DOMAIN,
    TARGET_SOURCE_PRIORITY_OPTIONS,
)


def _required_key(key: str, default: Any | None = None) -> vol.Required:
    """Return a required schema key, optionally with a default value."""
    if default is None:
        return vol.Required(key)
    return vol.Required(key, default=default)


def _target_priority_selector() -> selector.SelectSelector:
    """Return the target source priority selector.

    The selector stores the stable internal values, while Home Assistant uses
    the translation key to display friendly labels such as "Kalendertermin
    zuerst" instead of raw values like "calendar_first".
    """
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=list(TARGET_SOURCE_PRIORITY_OPTIONS),
            translation_key=CONF_TARGET_SOURCE_PRIORITY,
        )
    )


def _build_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build the config/options schema."""
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
            vol.Required(
                CONF_TARGET_SOURCE_PRIORITY,
                default=defaults.get(
                    CONF_TARGET_SOURCE_PRIORITY,
                    DEFAULT_TARGET_SOURCE_PRIORITY,
                ),
            ): _target_priority_selector(),
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


def _normalize_input(user_input: dict[str, Any]) -> dict[str, Any]:
    """Normalize text values before storing them."""
    normalized = dict(user_input)
    normalized[CONF_NAME] = str(normalized.get(CONF_NAME, "")).strip()
    normalized[CONF_SOC_SENSOR] = str(normalized.get(CONF_SOC_SENSOR, "")).strip()
    normalized[CONF_TARGET_SOC_ENTITY] = str(normalized.get(CONF_TARGET_SOC_ENTITY, "")).strip()
    normalized[CONF_TARGET_TIME] = str(normalized.get(CONF_TARGET_TIME, "")).strip()
    normalized[CONF_TARGET_SOURCE_PRIORITY] = str(
        normalized.get(CONF_TARGET_SOURCE_PRIORITY, DEFAULT_TARGET_SOURCE_PRIORITY)
    ).strip()
    normalized[CONF_CALENDAR_ENTITY] = str(normalized.get(CONF_CALENDAR_ENTITY, "")).strip()
    normalized[CONF_BATTERY_SIZE_KWH] = float(normalized[CONF_BATTERY_SIZE_KWH])
    normalized[CONF_CHARGE_POWER_KW] = float(normalized[CONF_CHARGE_POWER_KW])
    normalized[CONF_EFFICIENCY] = float(normalized[CONF_EFFICIENCY])
    normalized[CONF_BUFFER_MINUTES] = int(float(normalized[CONF_BUFFER_MINUTES]))
    return normalized


_OPTIONS_FLOW_BASE = getattr(
    config_entries, "OptionsFlowWithReload", config_entries.OptionsFlow
)


class EVAndBatteryChargerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EV and Battery Charger."""

    VERSION = 1
    MINOR_VERSION = 8

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
        entry = self._get_reconfigure_entry()
        current = {**entry.data, **entry.options}
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input = _normalize_input(user_input)
            errors = _validate_input(user_input)
            if not errors:
                # Keep the same unique ID, update the existing entry, and let
                # Home Assistant reload the entry safely after the flow ends.
                await self.async_set_unique_id(entry.unique_id or slugify(user_input[CONF_NAME]))
                self._abort_if_unique_id_mismatch()
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates=user_input,
                    title=user_input[CONF_NAME],
                    reason="reconfigure_successful",
                )

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
        return EVAndBatteryChargerOptionsFlow()


class EVAndBatteryChargerOptionsFlow(_OPTIONS_FLOW_BASE):
    """Handle EV and Battery Charger options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input = _normalize_input(user_input)
            errors = _validate_input(user_input)
            if not errors:
                return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(user_input or current),
            errors=errors,
        )
