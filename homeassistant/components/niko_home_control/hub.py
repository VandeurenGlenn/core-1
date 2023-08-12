"""The niko_home_control component."""
from __future__ import annotations

import asyncio

import nikohomecontrol
import voluptuous as vol

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DEFAULT_IP, DEFAULT_NAME, DEFAULT_PORT, DOMAIN
from .data import NikoHomeControlData

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Required(CONF_HOST, default=DEFAULT_IP): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
    }
)


class Hub:
    """The niko home control hub."""

    manufacturer = "Niko"
    website = "https://niko.eu"

    def __init__(self, hass: HomeAssistant, name: str, host: str, port: str) -> None:
        """Init niko home control hub."""
        self._host = host
        self._port = port
        self._hass = hass
        self._name = name
        self._id = name

    @property
    def hub_id(self) -> str:
        """Id."""
        return self._id

    async def connect(self) -> bool:
        """connect."""
        try:
            nhc = nikohomecontrol.NikoHomeControl(
                {"ip": self._host, "port": self._port, "timeout": 20000}
            )
            niko_actions = nhc.list_actions
            niko_data = NikoHomeControlData(self._hass, nhc)
            await niko_data.async_update()
            self._hass.data[DOMAIN] = {niko_data, niko_actions}
            return True
        except asyncio.TimeoutError as ex:
            raise ConfigEntryNotReady(
                f"Timeout while connecting to {self._host}:{self._port}"
            ) from ex
