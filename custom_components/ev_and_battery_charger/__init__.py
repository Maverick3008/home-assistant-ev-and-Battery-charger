"""The EV and Battery Charger integration."""
from __future__ import annotations

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_TARGET_SOC, DEFAULT_TARGET_SOC, DOMAIN

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.NUMBER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up EV and Battery Charger from a config entry."""
    configured_target_soc = entry.options.get(
        CONF_TARGET_SOC, entry.data.get(CONF_TARGET_SOC, DEFAULT_TARGET_SOC)
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "entry": entry,
        "target_soc": float(configured_target_soc),
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # On Home Assistant versions without OptionsFlowWithReload we still need a
    # listener to reload the integration after options change. Newer versions
    # handle the reload in the options flow itself, avoiding double reloads.
    if not hasattr(config_entries, "OptionsFlowWithReload"):
        entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)
