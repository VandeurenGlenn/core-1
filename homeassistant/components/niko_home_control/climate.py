"""Support for Niko Home Control thermostats."""

from nhc.thermostat import NHCThermostat

from homeassistant.components.climate import (
    ATTR_TARGET_TEMP_HIGH,
    HVAC_MODES,
    PRESET_AWAY,
    PRESET_ECO,
    PRESET_HOME,
    ClimateEntity,
    ClimateEntityFeature,
)
from homeassistant.components.sensor import UnitOfTemperature
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
        | ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    _action: NHCThermostat

    @property
    def hvac_modes(self):
        """Return the list of available HVAC modes."""
        return [HVAC_MODES.OFF, HVAC_MODES.COOL, HVAC_MODES.AUTO, HVAC_MODES.HEAT]

    @property
    def preset_modes(self):
        """Return the list of available preset modes."""
        return [PRESET_ECO, "day", "night", "prog 1", "prog 2", "prog 3"]

    @property
    def preset_mode(self):
        """Return the current preset mode."""
        return PRESET_AWAY if self._action.mode else PRESET_HOME

    async def async_set_preset_mode(self, preset_mode):
        """Set new preset mode."""
        self._action.set_mode(preset_mode)

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        self._action.set_temperature(kwargs.get(ATTR_TARGET_TEMP_HIGH) * 10)

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        self._action.set_mode(hvac_mode)

    def update_state(self):
        """Update the state of the entity."""
        self._attr_hvac_mode = self._action.state
        self._attr_target_temperature = self._action.setpoint / 10
        self._attr_current_temperature = self._action.measured / 10
