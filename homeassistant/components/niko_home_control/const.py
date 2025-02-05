"""Constants for niko_home_control integration."""

import logging

DOMAIN = "niko_home_control"
DATA_STORE: dict[str, str] = {
    "PREVIOUS_STATE": "previous_state",
}

_LOGGER = logging.getLogger(__name__)
