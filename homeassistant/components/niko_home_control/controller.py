"""Niko Home Control action controller."""
import logging

from nikohomecontrol import NikoHomeControlMonitor

_LOGGER = logging.getLogger(__name__)


class ActionController:
    """Niko Home Control action controller."""

    def __init__(self, host, port):
        """Init Niko Home Control action controller."""
        self._ip = host
        self._port = port
        self._monitor = NikoHomeControlMonitor(host, port)
        self._monitor.callback(self._on_event)

    async def async_list_actions(self):
        """List available actions."""

    def on_event(self, action_event):
        """On Action Event."""
        _LOGGER.debug(action_event)
