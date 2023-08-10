"""Setup NikoHomeControlLight."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
    brightness_supported,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({vol.Required(CONF_HOST): cv.string})

_LOGGER = logging.getLogger(__name__)


async def async_load_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Niko Home Control light platform."""

    entities = []
    for action in hass.data[DOMAIN].niko_actions():
        _LOGGER.debug(action.name)
        _LOGGER.debug(", %s", str(action))
        action_state = hass.data[DOMAIN].niko_data.get_state(action.id)
        if action_state == 1 | action_state == 2:  # lights & dimmable lights
            entities.append(NikoHomeControlLight(action, hass.data[DOMAIN].niko_data))

        async_add_entities(entities, True)


class NikoHomeControlLight(LightEntity):
    """Representation of an Niko Light."""

    def __init__(self, light, data):
        """Set up the Niko Home Control light platform."""
        self._data = data
        self._light = light
        self._attr_unique_id = f"light-{light.id}"
        self._attr_name = light.name
        self._attr_is_on = light.is_on
        self._attr_color_mode = ColorMode.ONOFF
        self._attr_supported_color_modes = {ColorMode.ONOFF}
        if light._state["type"] == 2:
            self._attr_color_mode = ColorMode.BRIGHTNESS
            self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        _LOGGER.debug("Turn on: %s", self.name)
        self._light.turn_on(kwargs.get(ATTR_BRIGHTNESS, 255) / 2.55)

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        _LOGGER.debug("Turn off: %s", self.name)
        self._light.turn_off()

    async def async_update(self) -> None:
        """Get the latest data from NikoHomeControl API."""
        await self._data.async_update()
        state = self._data.get_state(self._light.id)
        self._attr_is_on = state != 0
        if brightness_supported(self.supported_color_modes):
            self._attr_brightness = state * 2.55
