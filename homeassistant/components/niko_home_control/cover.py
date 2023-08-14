"""Setup NikoHomeControlcover."""
from __future__ import annotations

import logging

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .action import Action
from .const import DOMAIN
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

    def __init__(self, cover, hub: Hub) -> None:
        """Set up the Niko Home Control cover."""
        self._hub = hub
        self._cover = cover
        self._attr_unique_id = f"cover-{cover.id}"
        self._attr_name = cover.name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, cover.id)},
            manufacturer=hub.manufacturer,
            name=cover.name,
        )

    @property
    def supported_features(self):
        """Flag supported features."""
        return CoverEntityFeature.CLOSE | CoverEntityFeature.OPEN

    @property
    def is_closed(self) -> bool:
        """Return if the cover is closed, same as position 0."""
        state = self._hub.get_action_state(self._cover.id)
        return state == 0

    @property
    def available(self) -> bool:
        """Return True if when available."""
        return True

    @property
    def is_open(self) -> bool:
        """Return if the cover is closed, same as position !0."""
        state = self._hub.get_action_state(self._cover.id)
        return state != 0

    async def async_close_cover(self):
        """Close the cover."""
        _LOGGER.debug("Close cover: %s", self.name)
        self._hub.executeActions(self._cover.id, 1)
        # self._cover.turn_off()

    async def async_open_cover(self):
        """Open the cover."""
        _LOGGER.debug("Open cover: %s", self.name)
        self._hub.executeActions(self._cover.id, 100)
        # self._cover.turn_on()

    async def async_update(self):
        """Get the latest data from NikoHomeControl API."""
        await self._hub.async_update()
        state = self._hub.get_action_state(self._cover.id)
        self._attr_is_closed = state == 0
