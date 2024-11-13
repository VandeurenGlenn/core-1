"""The Niko home control integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .hub import NHCHub

_LOGGER = logging.getLogger(DOMAIN)

PLATFORMS: list[str] = ["light", "cover", "fan"]

_hub: NHCHub


async def event_handler(event) -> None:
    """Handle events."""
    entity = _hub.get_entity(event["id"])
    entity.update_state(event["value1"])
    _LOGGER.debug(entity)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set Niko Home Control from a config entry."""
    config: dict[str, Any] = entry.data["config"]
    options = entry.data["options"]
    enabled_entities = entry.data["entities"]

    global _hub
    _hub = NHCHub(
        hass,
        config["name"],
        config["host"],
        config["port"],
        entry.entry_id,
        options["importLocations"],
    )

    _hub.add_callback(event_handler)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "hub": _hub,
        "enabled_entities": enabled_entities,
        "options": options,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
