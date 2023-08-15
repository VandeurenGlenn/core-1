"""Setup NikoHomeControlcover."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .action import Action
from .const import COVER_CLOSE, COVER_OPEN, COVER_STOP, DOMAIN
from .hub import Hub

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

    should_poll = False

    def __init__(self, cover, hub: Hub) -> None:
        """Set up the Niko Home Control cover."""
        self._hub = hub
        self._cover = cover
        self._attr_unique_id = f"cover-{cover.action_id}"
        self._attr_name = cover.name
        self._moving = False
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, cover.id)},
            manufacturer=hub.manufacturer,
            name=cover.name,
        )

    @property
    def supported_features(self):
        """Flag supported features."""
        return (
            CoverEntityFeature.CLOSE
            | CoverEntityFeature.OPEN
            | CoverEntityFeature.STOP
            | CoverEntityFeature.SET_POSITION
        )

    @property
    def current_cover_position(self):
        """Return the current position of the cover."""
        return self._cover.state

    @property
    def is_closed(self) -> bool:
        """Return if the cover is closed, same as position 0."""
        return self._cover.state == 0

    @property
    def is_closing(self) -> bool:
        """Return if the cover is closing or not."""
        return self._moving

    @property
    def is_opening(self) -> bool:
        """Return if the cover is opening or not."""
        return self._moving

    @property
    def available(self) -> bool:
        """Return True if when available."""
        return True

    @property
    def is_open(self) -> bool:
        """Return if the cover is open, same as position 100."""
        return self._cover.state > 0

    def open_cover(self):
        """Open the cover."""
        _LOGGER.debug("Open cover: %s", self.name)
        # 255 = open
        self._cover.turn_on(COVER_OPEN)

    def close_cover(self):
        """Close the cover."""
        _LOGGER.debug("Close cover: %s", self.name)
        # 254 = close
        self._cover.turn_on(COVER_CLOSE)

    def stop_cover(self):
        """Stop the cover."""
        _LOGGER.debug("Stop cover: %s", self.name)
        # 253 = open
        self._cover.turn_on(COVER_STOP)

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Set the cover position."""
        _LOGGER.debug("Set cover position: %s", self.name)
        self._moving = True
        target = kwargs.get(ATTR_POSITION, 100)

        if target > self.current_cover_position:
            self._cover.turn_on(COVER_OPEN)
            while target > self.current_cover_position:
                await asyncio.sleep(1)

        else:
            self._cover.turn_on(COVER_CLOSE)
            while target < self.current_cover_position:
                await asyncio.sleep(1)

        self.stop_cover()
        self._moving = False

    def update_state(self, state):
        """Update HA state."""
        self._attr_is_closed = state == 0
        self._attr_current_cover_position = state
        self.publish_updates()

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        self._cover.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        self._cover.remove_callback(self.async_write_ha_state)
