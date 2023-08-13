"""Setup NikoHomeControlcover."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .action import Action
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Niko Home Control cover."""
    entities = []
    hub = hass.data[DOMAIN][entry.entry_id]
    for action in hub.actions():
        _LOGGER.debug(action.name)
        action_type = Action(action).action_type
        if action_type == 4:  # blinds/covers
            entities.append(NikoHomeControlCover(action, hub))

        async_add_entities(entities, True)


class NikoHomeControlCover(CoverEntity):
    """Representation of a Niko Cover."""

    def __init__(self, cover, hub):
        """Set up the Niko Home Control cover."""
        self._hub = hub
        self._cover = cover
        self._attr_unique_id = f"cover-{cover.id}"
        self._attr_name = cover.name
        self._attr_is_closed = cover.is_on

    @property
    def supported_features(self):
        """Flag supported features."""
        return CoverEntityFeature.CLOSE | CoverEntityFeature.OPEN

    def open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        _LOGGER.debug("Open cover: %s", self.name)
        self._cover.async_open_cover()

    def close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        _LOGGER.debug("Close cover: %s", self.name)
        self._cover.async_close_cover()

    def turn_on(self, **kwargs: Any) -> None:
        """Open the cover."""
        _LOGGER.debug("Open cover: %s", self.name)
        self._cover.async_open_cover()

    def turn_off(self, **kwargs: Any) -> None:
        """Close the cover."""
        _LOGGER.debug("Close cover: %s", self.name)
        self._cover.async_close_cover()

    async def async_update(self) -> None:
        """Get the latest data from NikoHomeControl API."""
        await self._hub.async_update()
        state = self._hub.get_action_state(self._cover.id)
        self._attr_is_closed = state != 0
