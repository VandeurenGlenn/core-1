"""The niko_home_control controller."""
from nhc.controller import NHCController

from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .cover import NikoHomeControlCover
from .fan import NikoHomeControlFan
from .light import NikoHomeControlDimmableLight, NikoHomeControlLight


class NHCHub(NHCController):
    """The niko home control controller."""

    def __init__(self, hass, name, host, port, entry_id, importLocations) -> None:
        """Init niko home control controller."""
        super().__init__(host, port)
        self.entities = []
        self.hass = hass
        self._entry_id = entry_id

        self.entities: list[
            NikoHomeControlLight
            | NikoHomeControlDimmableLight
            | NikoHomeControlCover
            | NikoHomeControlFan
        ] = []

        suggested_area = None

        if importLocations is not False:
            suggested_area = "garage"

        self._via_device = (DOMAIN, entry_id)
        self._device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "manufacturer": "Niko",
            "model": "Connected controller (550-00004)",
            "name": name,
            "sw_version": self.system_info["swversion"],
            "hw_version": "1.0",
        }

        device_registry = dr.async_get(hass)

        device_registry.async_get_or_create(
            config_entry_id=entry_id,
            identifiers={(DOMAIN, entry_id)},
            manufacturer="Niko",
            suggested_area=suggested_area,
            name="Niko Home Control Controller",
            model="Connected controller (550-00004)",
            sw_version=self.system_info["swversion"],
            hw_version="1.0",
        )

    def get_entity(self, action_id):
        """Get entity by id."""
        actions = [
            action for action in self.entities if str(action.id) == str(action_id)
        ]
        return actions[0]
