"""Number platform for EV and Battery Charger."""
from __future__ import annotations

from typing import Any

from homeassistant.components.number import NumberEntity
try:  # Older Home Assistant versions may not expose NumberMode.
    from homeassistant.components.number import NumberMode
except ImportError:  # pragma: no cover
    NumberMode = None  # type: ignore[assignment]
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    CONF_NAME,
    CONF_TARGET_SOC,
    CONF_TARGET_SOC_ENTITY,
    DEFAULT_NAME,
    DEFAULT_TARGET_SOC,
    DOMAIN,
    INVALID_STATES,
    SIGNAL_TARGET_SOC_UPDATED,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EV and Battery Charger number entities."""
    async_add_entities([EVAndBatteryChargerTargetSocNumber(hass, entry)])


class EVAndBatteryChargerTargetSocNumber(NumberEntity, RestoreEntity):
    """Target state of charge number for the charge planner."""

    _attr_has_entity_name = True
    _attr_translation_key = "target_soc"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_icon = "mdi:battery-charging-80"
    if NumberMode is not None:
        _attr_mode = NumberMode.SLIDER

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the target SOC number."""
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_target_soc"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=self.config.get(CONF_NAME, DEFAULT_NAME),
            manufacturer="EV and Battery Charger",
            model="Calendar-aware EV and battery charge planner",
        )
        self._attr_native_value = self._initial_target_soc()

    @property
    def config(self) -> dict[str, Any]:
        """Return merged config entry data and options."""
        return {**self.entry.data, **self.entry.options}

    def _initial_target_soc(self) -> float:
        """Return the configured default target SOC."""
        try:
            return float(self.config.get(CONF_TARGET_SOC, DEFAULT_TARGET_SOC))
        except (TypeError, ValueError):
            return DEFAULT_TARGET_SOC

    def _legacy_target_soc(self) -> float | None:
        """Return the old external target SOC helper value for migration."""
        legacy_entity = str(self.config.get(CONF_TARGET_SOC_ENTITY, "") or "").strip()
        if not legacy_entity:
            return None
        state = self.hass.states.get(legacy_entity)
        if state is None or state.state in INVALID_STATES:
            return None
        try:
            return float(state.state)
        except (TypeError, ValueError):
            return None

    async def async_added_to_hass(self) -> None:
        """Restore the last target SOC and publish it to the integration."""
        target_soc = self._initial_target_soc()

        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state not in INVALID_STATES:
            try:
                target_soc = float(last_state.state)
            except (TypeError, ValueError):
                pass
        else:
            legacy_soc = self._legacy_target_soc()
            if legacy_soc is not None:
                target_soc = legacy_soc

        await self.async_set_native_value(target_soc, write_state=False)

    async def async_set_native_value(self, value: float, write_state: bool = True) -> None:
        """Set the target SOC."""
        target_soc = max(0.0, min(100.0, float(value)))
        self._attr_native_value = target_soc

        entry_data = self.hass.data.setdefault(DOMAIN, {}).setdefault(self.entry.entry_id, {})
        if isinstance(entry_data, dict):
            entry_data["target_soc"] = target_soc

        async_dispatcher_send(
            self.hass,
            f"{DOMAIN}_{self.entry.entry_id}_{SIGNAL_TARGET_SOC_UPDATED}",
        )
        if write_state:
            self.async_write_ha_state()
