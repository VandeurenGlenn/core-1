"""The niko_home_control component."""
from __future__ import annotations

import logging

import nikohomecontrol
import voluptuous as vol

from homeassistant.components.light import (
    PLATFORM_SCHEMA,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import Throttle

from .const import MIN_TIME_BETWEEN_UPDATES

_LOGGER = logging.getLogger(__name__)

DOMAIN = "niko_home_control"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({vol.Required(CONF_HOST): cv.string})


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Niko Home Control platform."""
    try:
        host = config[CONF_HOST]
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

    hass.async_create_task(async_load_platform(hass, "light", DOMAIN, {}, config))
    hass.async_create_task(async_load_platform(hass, "cover", DOMAIN, {}, config))
    return True


class NikoHomeControlData:
    """The class for handling data retrieval."""

    def __init__(self, hass, nhc):
        """Set up Niko Home Control Data object."""
        self._nhc = nhc
        self.hass = hass
        self.available = True
        self.data = {}
        self._system_info = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Get the latest data from the NikoHomeControl API."""
        _LOGGER.debug("Fetching async state in bulk")
        try:
            self.data = await self.hass.async_add_executor_job(
                self._nhc.list_actions_raw
            )
            self.available = True
        except OSError as ex:
            _LOGGER.error("Unable to retrieve data from Niko, %s", str(ex))
            self.available = False

    def get_state(self, aid):
        """Find and filter state based on action id."""
        for state in self.data:
            if state["id"] == aid:
                return state["value1"]
        _LOGGER.error("Failed to retrieve state off unknown component")
