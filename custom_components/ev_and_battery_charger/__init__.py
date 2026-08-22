"""The EV and Battery Charger integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    CALENDAR_REFRESH_INTERVAL_MINUTES,
    CONF_CALENDAR_ENTITY,
    CONF_TARGET_SOC,
    DEFAULT_TARGET_SOC,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.NUMBER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up EV and Battery Charger from a config entry."""
    configured_target_soc = entry.options.get(
        CONF_TARGET_SOC, entry.data.get(CONF_TARGET_SOC, DEFAULT_TARGET_SOC)
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "entry": entry,
        "target_soc": float(configured_target_soc),
        "calendar_target_event": None,
        "calendar_completed_event": None,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Remote Calendar polls only every 24 hours by default. Refresh the calendar
    # selected for this charger every 30 minutes so newly added events become
    # visible to the charging plan much sooner. The standard update_entity
    # action also works with other calendar integrations that support updates.
    async def _async_refresh_calendar(_now: datetime | None = None) -> None:
        config = {**entry.data, **entry.options}
        calendar_entity = str(config.get(CONF_CALENDAR_ENTITY, "") or "").strip()
        if not calendar_entity or hass.states.get(calendar_entity) is None:
            return

        try:
            await hass.services.async_call(
                "homeassistant",
                "update_entity",
                {"entity_id": calendar_entity},
                blocking=True,
            )
        except Exception:  # Home Assistant must keep running if one refresh fails.
            _LOGGER.exception("Failed to refresh calendar entity %s", calendar_entity)

    entry.async_on_unload(
        async_track_time_interval(
            hass,
            _async_refresh_calendar,
            timedelta(minutes=CALENDAR_REFRESH_INTERVAL_MINUTES),
        )
    )
    hass.async_create_task(_async_refresh_calendar())

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
