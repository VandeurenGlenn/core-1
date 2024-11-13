"""Setup NikoHomeControlLight."""
from __future__ import annotations

from typing import Any

from nhc.light import NHCLight

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Niko Home Control light platform."""
    hub = hass.data[DOMAIN][entry.entry_id]["hub"]
    enabled_entities = hass.data[DOMAIN][entry.entry_id]["enabled_entities"]

    if enabled_entities["lights"] is False:
        return

    entities = []

    for action in hub.actions:
        entity = None
        action_type = action.action_type
        if action_type == 1:
            entity = NikoHomeControlLight(hub, action, options=entry.data["options"])
        if action_type == 2:
            entity = NikoHomeControlDimmableLight(
                hub, action, options=entry.data["options"]
            )

        if entity is not None:
            hub.entities.append(entity)
            entities.append(entity)

    async_add_entities(entities, True)


class NikoHomeControlLight(LightEntity):
    """Representation of an Niko Light."""

    def __init__(self, hub, action: NHCLight, options):
        """Set up the Niko Home Control light platform."""
        self._action = action

        # hass states
        self._attr_name = action.name
        self._attr_is_on = action.is_on
        self._attr_unique_id = f"light-{action.action_id}"
        self._attr_color_mode = ColorMode.ONOFF
        self._attr_supported_color_modes = {ColorMode.ONOFF}

        area = None
        if options["importLocations"] is not False:
            area = action.suggested_area

        if options["treatAsDevice"] is not False:
            self._attr_device_info = {
                "identifiers": {(DOMAIN, self._attr_unique_id)},
                "manufacturer": "Niko",
                "name": action.name,
                "model": "P.O.M",
                "via_device": hub._via_device,
                "suggested_area": area,
            }
        else:
            self._attr_device_info = hub._device_info

    @property
    def should_poll(self) -> bool:
        """No polling needed for a Niko light."""
        return False

    @property
    def id(self):
        """A Niko Action action_id."""
        return self._action.action_id

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        self._action.turn_on(100)

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._action.turn_off()

    def update_state(self, state):
        """Update HA state."""
        self._action.update_state(state)
        self._attr_is_on = state > 0
        self.async_write_ha_state()


class NikoHomeControlDimmableLight(NikoHomeControlLight):
    """Representation of an Niko Dimmable Light."""

    def __init__(self, hub, action, options):
        """Set up the Niko Home Control Dimmable Light platform."""
        super().__init__(hub, action, options)
        self._attr_unique_id = f"dimmable-{action.action_id}"
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        self._attr_brightness = action.state * 2.55

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        self._action.turn_on(kwargs.get(ATTR_BRIGHTNESS, 255) / 2.55)

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._action.turn_off()

    def update_state(self, state):
        """Update HA state."""
        super().update_state(state)
        self._attr_brightness = state * 2.55
        self.async_write_ha_state()
