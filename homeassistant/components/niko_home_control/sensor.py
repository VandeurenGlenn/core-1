"""Support for Niko Home Control energy meter."""

from nhc.controller import NHCController
from nhc.energy import NHCEnergy

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfPower
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
        NikoHomeControlPowerSensor(
            controller.energy[energy], controller, entry.entry_id
        )
        for energy in controller.energy
    )


class NikoHomeControlPowerSensor(NikoHomeControlEntity, SensorEntity):
    """Representation of a Niko Home Control Power Sensor."""

    def __init__(
        self, action: NHCEnergy, controller: NHCController, unique_id: str
    ) -> None:
        """Set up the Niko Home Control Sensor platform."""
        super().__init__(action, controller, unique_id)
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_suggested_unit_of_measurement = UnitOfPower.WATT

    def update_state(self) -> None:
        """Update the state of the entity."""
        self._attr_native_value = self._action.state
