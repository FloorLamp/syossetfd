"""Config flow for Syosset Fire Department integration."""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class SyossetFDConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Syosset FD."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Syosset Fire Department",
                data=user_input,
            )

        data_schema = vol.Schema({
            vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=1440)
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            description_placeholders={"scan_interval": str(DEFAULT_SCAN_INTERVAL)},
        )
