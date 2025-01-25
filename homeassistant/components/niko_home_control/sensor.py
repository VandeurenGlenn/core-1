"""Support for Niko Home Control energy meter."""

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

    _attr_name = None
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return UnitOfPower.WATT

    def update_state(self) -> None:
        """Update the state of the entity."""
        self._attr_native_value = self._action.state
