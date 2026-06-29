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
    CONF_CHARGE_POWER_KW,
    CONF_EFFICIENCY,
    CONF_NAME,
    CONF_SOC_SENSOR,
    CONF_TARGET_SOC_ENTITY,
    CONF_TARGET_TIME,
    DEFAULT_BATTERY_SIZE_KWH,
    DEFAULT_BUFFER_MINUTES,
    DEFAULT_CHARGE_POWER_KW,
    DEFAULT_EFFICIENCY,
    DEFAULT_NAME,
    DEFAULT_TARGET_TIME,
    DOMAIN,
)


def _number_selector(
    minimum: float,
    maximum: float,
    step: float,
    unit: str | None = None,
) -> selector.NumberSelector:
    """Create a boxed number selector."""
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=minimum,
            max=maximum,
            step=step,
            mode=selector.NumberSelectorMode.BOX,
            unit_of_measurement=unit,
        )
    )


def _required_key(key: str, default: Any | None = None) -> vol.Required:
    """Return a required schema key, optionally with a default value."""
    if default is None:
        return vol.Required(key)
    return vol.Required(key, default=default)


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
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor", "number", "input_number"])
            ),
            _required_key(
                CONF_TARGET_SOC_ENTITY,
                defaults.get(CONF_TARGET_SOC_ENTITY),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["input_number", "number", "sensor"])
            ),
            vol.Required(
                CONF_TARGET_TIME,
                default=defaults.get(CONF_TARGET_TIME, DEFAULT_TARGET_TIME),
            ): selector.TimeSelector(),
            vol.Required(
                CONF_BATTERY_SIZE_KWH,
                default=defaults.get(CONF_BATTERY_SIZE_KWH, DEFAULT_BATTERY_SIZE_KWH),
            ): _number_selector(1, 300, 0.1, "kWh"),
            vol.Required(
                CONF_CHARGE_POWER_KW,
                default=defaults.get(CONF_CHARGE_POWER_KW, DEFAULT_CHARGE_POWER_KW),
            ): _number_selector(0.1, 350, 0.1, "kW"),
            vol.Required(
                CONF_EFFICIENCY,
                default=defaults.get(CONF_EFFICIENCY, DEFAULT_EFFICIENCY),
            ): _number_selector(0.5, 1.0, 0.01),
            vol.Required(
                CONF_BUFFER_MINUTES,
                default=defaults.get(CONF_BUFFER_MINUTES, DEFAULT_BUFFER_MINUTES),
            ): _number_selector(0, 240, 1, "min"),
        }
    )


class EVChargePlannerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EV and Battery Charger."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            if not name:
                errors[CONF_NAME] = "empty_name"
            else:
                await self.async_set_unique_id(slugify(name))
                self._abort_if_unique_id_configured()
                user_input[CONF_NAME] = name
                return self.async_create_entry(title=name, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> EVChargePlannerOptionsFlow:
        """Create the options flow."""
        return EVChargePlannerOptionsFlow()


class EVChargePlannerOptionsFlow(config_entries.OptionsFlow):
    """Handle EV and Battery Charger options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(current),
        )
