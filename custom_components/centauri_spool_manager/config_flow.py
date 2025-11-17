"""Config flow for Centauri Carbon Spool Manager."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class CentauriSpoolManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Centauri Carbon Spool Manager."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        # Check if already configured
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(
                title="Centauri Carbon Spool Manager",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={
                "docs_url": "https://github.com/harpua555/Centauri-Carbon-Spool-Manager"
            },
        )
