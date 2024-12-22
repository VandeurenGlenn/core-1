"""Setup NikoHomeControlcover."""

from __future__ import annotations

from nhc.const import COVER_CLOSE, COVER_OPEN, COVER_STOP
from nhc.cover import NHCCover

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import NikoHomeControlConfigEntry
from .entity import NikoHomeControlEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NikoHomeControlConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Niko Home Control cover entry."""
    controller = entry.runtime_data

    async_add_entities(
        NikoHomeControlCover(cover, controller, entry.entry_id)
        for cover in controller.covers
    )


class NikoHomeControlCover(NikoHomeControlEntity, CoverEntity):
    """Representation of a Niko Cover."""

    _attr_name = None
    _action = NHCCover

    def __init__(self, cover, controller, unique_id) -> None:
        """Set up the Niko Home Control cover."""
        super().__init__(cover, controller, unique_id)
        self.update_state()
        self._attr_supported_features = (
            CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
        )

    def open_cover(self):
        """Open the cover."""
        self._cover.turn_on(COVER_OPEN)

    def close_cover(self):
        """Close the cover."""
        self._cover.turn_on(COVER_CLOSE)

    def stop_cover(self):
        """Stop the cover."""
        self._cover.turn_on(COVER_STOP)

    def update_state(self):
        """Update HA state."""
        self._attr_is_closed = self._action.state == 0
