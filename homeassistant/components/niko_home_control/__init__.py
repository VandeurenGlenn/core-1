"""The niko_home_control integration."""
from __future__ import annotations

import logging

import nikohomecontrol
import voluptuous as vol

from homeassistant.components.light import (
    PLATFORM_SCHEMA,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .data import NikoHomeControlData

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({vol.Required(CONF_HOST): cv.string})

platforms = [Platform.LIGHT, Platform.COVER]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up the Niko Home Control entry."""
    try:
        host = config_entry.data[CONF_HOST]
        nhc = nikohomecontrol.NikoHomeControl(
            {"ip": host, "port": 8000, "timeout": 20000}
        )
        niko_actions = nhc.list_actions
        niko_data = NikoHomeControlData(hass, nhc)
        await niko_data.async_update()
        hass.data[DOMAIN] = {niko_data, niko_actions}
    except OSError as err:
        _LOGGER.error("Unable to access %s (%s)", host, err)
        raise PlatformNotReady from err
    await hass.config_entries.async_forward_entry_setups(config_entry, platforms)
    return True
