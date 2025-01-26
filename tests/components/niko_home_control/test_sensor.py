"""Tests for the Niko Home Control Light platform."""

from unittest.mock import AsyncMock

from homeassistant.components.sensor import ATTR_UNIT_OF_MEASUREMENT, SensorDeviceClass
from homeassistant.const import ATTR_DEVICE_CLASS, UnitOfPower
from homeassistant.core import HomeAssistant

from . import find_update_callback, setup_integration

from tests.common import MockConfigEntry


async def test_updating(
    hass: HomeAssistant,
    mock_niko_home_control_connection: AsyncMock,
    mock_config_entry: MockConfigEntry,
    sensor: AsyncMock,
) -> None:
    """Test turning on the light."""
    await setup_integration(hass, mock_config_entry)

    hass_state = hass.states.get("sensor.power")

    assert hass_state.attributes.get(ATTR_UNIT_OF_MEASUREMENT) == UnitOfPower.WATT
    assert hass_state.attributes[ATTR_DEVICE_CLASS] == SensorDeviceClass.POWER
    assert hass_state.state == "100"

    sensor.state = 0
    await find_update_callback(mock_niko_home_control_connection, 4)(0)

    assert hass.states.get("sensor.power").state == "0"
