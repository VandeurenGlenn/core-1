"""The niko_home_control hub."""
from __future__ import annotations

import asyncio
import json
import logging

from nikohomecontrol import NikoHomeControl
import voluptuous as vol

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DEFAULT_IP, DEFAULT_NAME, DEFAULT_PORT
from .data import NikoHomeControlData

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Required(CONF_HOST, default=DEFAULT_IP): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
    }
)
_LOGGER = logging.getLogger(__name__)


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
        self._data: NikoHomeControlData
        self._nhc: NikoHomeControl

    @property
    def hub_id(self) -> str:
        """Id."""
        return self._id

    @property
    def data(self):
        """Data."""
        return self._data

    def actions(self):
        """Actions."""
        return self._nhc.list_actions()

    async def async_update(self):
        """Update data."""
        return await self._data.async_update()

    def get_action_state(self, action_id):
        """Get action state."""
        return self._data.get_state(action_id)

    def executeActions(self, action_id, value):
        """Debug."""
        _LOGGER.debug("execute")
        _LOGGER.debug(action_id)
        _LOGGER.debug(value)
        return self._command(
            '{"cmd":"executeactions", "id": "'
            + str(action_id)
            + '", "value1": "'
            + str(value)
            + '"}'
        )

    def _command(self, cmd):
        data = json.loads(self._nhc.connection.send(cmd))
        _LOGGER.debug(data)
        if "error" in data["data"] and data["data"]["error"] > 0:
            error = data["data"]["error"]
            _LOGGER.error(error)

        return data["data"]

    async def connect(self) -> bool:
        """connect."""
        try:
            self._nhc = NikoHomeControl(
                {"ip": self._host, "port": self._port, "timeout": 20000}
            )
            self._data = NikoHomeControlData(self._hass, self._nhc)
            await self.async_update()
            return True
        except asyncio.TimeoutError as ex:
            raise ConfigEntryNotReady(
                f"Timeout while connecting to {self._host}:{self._port}"
            ) from ex
