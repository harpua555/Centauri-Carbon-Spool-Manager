"""Config flow for Centauri Carbon Spool Manager."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_PRINTER_DEVICE, CONF_NUM_SPOOLS

_LOGGER = logging.getLogger(__name__)


class CentauriSpoolManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Centauri Carbon Spool Manager."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.printer_device_id = None
        self.num_spools = 4

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return CentauriSpoolManagerOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - select printer."""
        # Check if already configured
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors = {}

        if user_input is not None:
            self.printer_device_id = user_input[CONF_PRINTER_DEVICE]
            self.num_spools = user_input.get(CONF_NUM_SPOOLS, 4)

            # Move to confirmation step
            return await self.async_step_confirm()

        # Get all devices with 3D printer capabilities
        device_registry = dr.async_get(self.hass)
        entity_registry = er.async_get(self.hass)

        printer_devices = {}

        # Look for devices with extrusion sensors (from Elegoo integration)
        for entity in entity_registry.entities.values():
            if entity.entity_id.endswith("_total_extrusion") or \
               entity.entity_id.endswith("_current_status") or \
               "printer" in entity.entity_id.lower():
                if entity.device_id:
                    device = device_registry.async_get(entity.device_id)
                    if device:
                        printer_devices[device.id] = f"{device.name} ({device.manufacturer or 'Unknown'})"

        if not printer_devices:
            # No printers found, allow manual setup
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_NUM_SPOOLS, default=4): vol.In([2, 3, 4]),
                }),
                errors={"base": "no_printers_found"},
                description_placeholders={
                    "docs_url": "https://github.com/harpua555/Centauri-Carbon-Spool-Manager"
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_PRINTER_DEVICE): vol.In(printer_devices),
                vol.Required(CONF_NUM_SPOOLS, default=4): vol.In([2, 3, 4]),
            }),
            errors=errors,
            description_placeholders={
                "docs_url": "https://github.com/harpua555/Centauri-Carbon-Spool-Manager"
            },
        )

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm the setup."""
        if user_input is not None or self.printer_device_id:
            return self.async_create_entry(
                title="Centauri Carbon Spool Manager",
                data={
                    CONF_PRINTER_DEVICE: self.printer_device_id,
                    CONF_NUM_SPOOLS: self.num_spools,
                },
            )

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "num_spools": str(self.num_spools),
            },
        )


class CentauriSpoolManagerOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_NUM_SPOOLS,
                    default=self.config_entry.data.get(CONF_NUM_SPOOLS, 4)
                ): vol.In([2, 3, 4]),
            }),
        )
