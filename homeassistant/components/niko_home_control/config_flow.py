"""Config flow for the Niko home control integration."""

from __future__ import annotations

from typing import Any

from nhc.controller import NHCController
import voluptuous as vol

from homeassistant.components import dhcp
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import format_mac

from .const import _LOGGER, DOMAIN

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


async def test_connection(host: str) -> str | None:
    """Test if we can connect to the Niko Home Control controller."""

    controller = NHCController(host, 8000)
    try:
        await controller.connect()
    except Exception:  # noqa: BLE001
        return "cannot_connect"
    return None


class NikoHomeControlConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Niko Home Control."""

    MINOR_VERSION = 2

    _discovered_ip: str | None = None
    _discovered_mac: str | None = None

    async def async_step_dhcp(
        self, discovery_info: dhcp.DhcpServiceInfo
    ) -> ConfigFlowResult:
        """Handle DHCP discovery."""
        self._discovered_ip = discovery_info.ip
        self._discovered_mac = discovery_info.macaddress

        _LOGGER.info(f"Discovered IP: {self._discovered_ip}")
        _LOGGER.debug(f"Discovered MAC: {self._discovered_mac}")
        self._async_abort_entries_match({CONF_HOST: self._discovered_ip})

        await self.async_set_unique_id(format_mac(self._discovered_mac))
        self._abort_if_unique_id_configured()
        return await self.async_step_user({CONF_HOST: self._discovered_ip})

    # return await super().async_step_dhcp(discovery_info)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})
            error = await test_connection(user_input[CONF_HOST])
            if not error:
                return self.async_create_entry(
                    title="Niko Home Control",
                    data=user_input,
                )
            errors["base"] = error

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    async def async_step_import(self, import_info: dict[str, Any]) -> ConfigFlowResult:
        """Import a config entry."""
        self._async_abort_entries_match({CONF_HOST: import_info[CONF_HOST]})
        error = await test_connection(import_info[CONF_HOST])

        if not error:
            return self.async_create_entry(
                title="Niko Home Control",
                data={CONF_HOST: import_info[CONF_HOST]},
            )
        return self.async_abort(reason=error)
