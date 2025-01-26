"""Support for Niko Home Control thermostats."""

from nhc.thermostat import NHCThermostat

from homeassistant.components.climate import (
    PRESET_ECO,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.components.sensor import UnitOfTemperature
from homeassistant.const import ATTR_TEMPERATURE
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
        NikoHomeControlClimate(
            controller.thermostats[thermostat], controller, entry.entry_id
        )
        for thermostat in controller.thermostats
    )


class NikoHomeControlClimate(NikoHomeControlEntity, ClimateEntity):
    """Representation of a Niko Home Control thermostat."""

    _attr_supported_features: ClimateEntityFeature = (
        ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    _action: NHCThermostat

    @property
    def hvac_modes(self):
        """Return the list of available hvac modes."""
        return (HVACMode.OFF, HVACMode.COOL, HVACMode.AUTO, HVACMode.HEAT)

    @property
    def hvac_mode(self):
        """Return the current hvac mode."""
        return self._mode

    @property
    def preset_modes(self):
        """Return the list of available preset modes."""
        return (PRESET_ECO, "day", "night", "prog 1", "prog 2", "prog 3")

    @property
    def preset_mode(self):
        """Return the current preset mode."""
        return self._preset

    def set_preset_mode(self, preset_mode):
        """Set new preset mode."""
        self._action.set_mode(preset_mode)

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        self._action.set_temperature(kwargs.get(ATTR_TEMPERATURE) * 10)

    def set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        self._action.set_mode(hvac_mode)

    def update_state(self):
        """Update the state of the entity."""
        mode = HVACMode.AUTO
        preset = None
        if self._action.state == 0:
            preset = "day"
        elif self._action.state == 1:
            preset = "night"
        elif self._action.state == 2:
            preset = PRESET_ECO
        elif self._action.state == 3:
            self.mode = HVACMode.OFF
        elif self._action.state == 4:
            self.mode = HVACMode.COOL
        elif self._action.state == 5:
            preset = "prog 1"
        elif self._action.state == 6:
            preset = "prog 2"
        elif self._action.state == 7:
            preset = "prog 3"

        self._mode = mode
        self._preset = preset

        self._attr_hvac_mode = mode
        self._attr_preset_mode = preset

        self._attr_target_temperature = self._action.setpoint / 10
        self._attr_current_temperature = self._action.measured / 10
