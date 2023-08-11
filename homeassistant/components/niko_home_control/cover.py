"""Setup NikoHomeControlShutter."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.cover import (
    PLATFORM_SCHEMA,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.const import CONF_DEVICE_CLASS, CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import Throttle

from .const import DOMAIN, MIN_TIME_BETWEEN_UPDATES

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_DEVICE_CLASS): cv.string,
    }
)

_LOGGER = logging.getLogger(__name__)


async def async_load_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType,
) -> None:
    """Set up the Niko Home Control shutter platform."""

    entities = []
    for action in hass.data[DOMAIN].niko_actions():
        _LOGGER.debug(action.name)
        _LOGGER.debug(", %s", str(action))
        action_state = hass.data[DOMAIN].niko_data.get_state(action.id)
        if action_state == 4:  # blinds/shutters
            entities.append(NikoHomeControlShutter(action, hass.data[DOMAIN].niko_data))

        async_add_entities(entities, True)


class NikoHomeControlShutter(CoverEntity):
    """Representation of a Niko Shutter."""

    def __init__(self, shutter, data):
        """Set up the Niko Home Control shutter platform."""
        self._data = data
        self._shutter = shutter
        self._attr_unique_id = f"shutter-{shutter.id}"
        self._attr_name = shutter.name
        self._attr_is_closed = shutter.is_on

    @property
    def supported_features(self):
        """Flag supported features."""
        return CoverEntityFeature

    def open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        _LOGGER.debug("Open cover: %s", self.name)
        self._shutter.async_open_cover()

    def close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        _LOGGER.debug("Close cover: %s", self.name)
        self._shutter.async_close_cover()

    def turn_on(self, **kwargs: Any) -> None:
        """Open the cover."""
        _LOGGER.debug("Open cover: %s", self.name)
        self._shutter.async_open_cover()

    def turn_off(self, **kwargs: Any) -> None:
        """Close the cover."""
        _LOGGER.debug("Close cover: %s", self.name)
        self._shutter.async_close_cover()

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self) -> None:
        """Get the latest data from NikoHomeControl API."""
        await self._data.async_update()
        state = self._data.get_state(self._shutter.id)
        self._attr_is_closed = state != 0
