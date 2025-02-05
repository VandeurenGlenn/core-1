"""Support for Niko Home Control thermostats."""

from typing import Any

from nhc.const import THERMOSTAT_MODES
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
from .const import _LOGGER
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
    _attr_name = None
    _action: NHCThermostat

    @property
    def hvac_modes(self):
        """Return the list of available hvac modes."""
        return [HVACMode.OFF, HVACMode.COOL, HVACMode.AUTO]

    @property
    def preset_modes(self):
        """Return the list of available preset modes."""
        return ["day", "night", PRESET_ECO, "prog 1", "prog 2", "prog 3"]

    def _get_niko_mode(self, mode: str) -> int | None:
        """Return the Niko mode."""
        for key, value in THERMOSTAT_MODES.items():
            if value == mode:
                return key
        return None

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        await self._action.set_temperature(kwargs.get(ATTR_TEMPERATURE, 20) * 10)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        _LOGGER.debug("Setting preset mode to %s", preset_mode)
        mode = self._get_niko_mode(preset_mode)
        _LOGGER.debug("Setting mode to %s", mode)
        if mode is None:
            _LOGGER.error("Invalid preset mode %s", preset_mode)
        else:
            await self._action.set_mode(mode)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        _LOGGER.debug("Setting hvac mode to %s", hvac_mode)
        mode = self._get_niko_mode(hvac_mode)
        _LOGGER.debug("Setting mode to %s", mode)
        if mode is None:
            _LOGGER.error("Invalid preset mode %s", hvac_mode)
        else:
            await self._action.set_mode(mode)

    async def async_turn_off(self) -> None:
        """Turn off."""
        _LOGGER.debug("Turning off")
        await self._action.set_mode(3)

    def update_state(self) -> None:
        """Update the state of the entity."""
        mode = HVACMode.AUTO
        preset = self.preset_modes[0]
        if self._action.state in (3, 4):
            mode = THERMOSTAT_MODES[self._action.state]
        else:
            preset = THERMOSTAT_MODES[self._action.state]

        self._attr_hvac_mode = mode
        self._attr_preset_mode = preset

        self._attr_target_temperature = self._action.setpoint / 10
        self._attr_current_temperature = self._action.measured / 10
