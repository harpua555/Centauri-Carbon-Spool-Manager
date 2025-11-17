"""Centauri Carbon Spool Manager Integration."""
from __future__ import annotations

import logging
import math
from pathlib import Path

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, PLATFORMS, CONF_NUM_SPOOLS
from .coordinator import CentauriSpoolCoordinator
from .dashboard import async_create_dashboard

_LOGGER = logging.getLogger(__name__)

# Service schemas
RESET_SPOOL_SCHEMA = vol.Schema({
    vol.Required("spool_number"): cv.positive_int,
})

UNDO_LAST_PRINT_SCHEMA = vol.Schema({
    vol.Required("spool_number"): cv.positive_int,
})

MARK_SPOOL_EMPTY_SCHEMA = vol.Schema({
    vol.Required("spool_number"): cv.positive_int,
})

SET_SPOOL_WEIGHT_SCHEMA = vol.Schema({
    vol.Required("spool_number"): cv.positive_int,
    vol.Required("weight_grams"): cv.positive_float,
})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Centauri Carbon Spool Manager from a config entry."""
    _LOGGER.info("Setting up Centauri Carbon Spool Manager")

    # Store config entry data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "config": entry.data,
    }

    # Initialize coordinator for automation
    coordinator = CentauriSpoolCoordinator(hass, entry)
    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    await async_register_services(hass, entry)

    # Register update listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Auto-create dashboard
    num_spools = entry.data.get(CONF_NUM_SPOOLS, 4)
    dashboard_created = await async_create_dashboard(hass, num_spools)
    if dashboard_created:
        _LOGGER.info("Spool Manager dashboard created successfully")
    else:
        _LOGGER.warning("Failed to create dashboard - you can add it manually from the YAML file")

    _LOGGER.info("Centauri Carbon Spool Manager setup complete")
    return True


async def async_register_services(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register integration services."""

    async def handle_reset_spool(call: ServiceCall) -> None:
        """Handle reset spool service."""
        spool_num = call.data["spool_number"]
        _LOGGER.info(f"Resetting spool {spool_num}")

        # Reset all spool values
        await hass.services.async_call(
            "number", "set_value",
            {"entity_id": f"number.centauri_spool_manager_spool_{spool_num}_used_length", "value": 0},
            blocking=True,
        )
        await hass.services.async_call(
            "number", "set_value",
            {"entity_id": f"number.centauri_spool_manager_spool_{spool_num}_last_print_length", "value": 0},
            blocking=True,
        )

    async def handle_undo_last_print(call: ServiceCall) -> None:
        """Handle undo last print service."""
        spool_num = call.data["spool_number"]
        _LOGGER.info(f"Undoing last print for spool {spool_num}")

        # Get last print length
        last_print_entity = f"number.centauri_spool_manager_spool_{spool_num}_last_print_length"
        last_print_state = hass.states.get(last_print_entity)

        if last_print_state and last_print_state.state not in ("unknown", "unavailable"):
            last_print_length = float(last_print_state.state)

            # Get current used length
            used_length_entity = f"number.centauri_spool_manager_spool_{spool_num}_used_length"
            used_state = hass.states.get(used_length_entity)

            if used_state and used_state.state not in ("unknown", "unavailable"):
                current_used = float(used_state.state)
                new_used = max(0, current_used - last_print_length)

                # Update used length
                await hass.services.async_call(
                    "number", "set_value",
                    {"entity_id": used_length_entity, "value": new_used},
                    blocking=True,
                )

                # Reset last print length
                await hass.services.async_call(
                    "number", "set_value",
                    {"entity_id": last_print_entity, "value": 0},
                    blocking=True,
                )

    async def handle_mark_spool_empty(call: ServiceCall) -> None:
        """Handle mark spool empty service."""
        spool_num = call.data["spool_number"]
        _LOGGER.info(f"Marking spool {spool_num} as empty")

        # Get initial length
        initial_length_entity = f"number.centauri_spool_manager_spool_{spool_num}_initial_length"
        initial_state = hass.states.get(initial_length_entity)

        if initial_state and initial_state.state not in ("unknown", "unavailable"):
            initial_length = float(initial_state.state)

            # Set used length to initial length
            await hass.services.async_call(
                "number", "set_value",
                {"entity_id": f"number.centauri_spool_manager_spool_{spool_num}_used_length", "value": initial_length},
                blocking=True,
            )

    async def handle_set_spool_weight(call: ServiceCall) -> None:
        """Handle set spool weight service."""
        spool_num = call.data["spool_number"]
        weight_grams = call.data["weight_grams"]
        _LOGGER.info(f"Setting spool {spool_num} weight to {weight_grams}g")

        # Get density and diameter
        density_entity = f"number.centauri_spool_manager_spool_{spool_num}_density"
        diameter_entity = "number.centauri_spool_manager_filament_diameter"

        density_state = hass.states.get(density_entity)
        diameter_state = hass.states.get(diameter_entity)

        if density_state and diameter_state:
            density = float(density_state.state) if density_state.state not in ("unknown", "unavailable") else 1.24
            diameter = float(diameter_state.state) if diameter_state.state not in ("unknown", "unavailable") else 1.75

            # Calculate length from weight
            # weight = π * r² * length * density
            # length = weight / (π * r² * density)
            radius_mm = diameter / 2
            volume_cm3 = weight_grams / density
            volume_mm3 = volume_cm3 * 1000
            length_mm = volume_mm3 / (math.pi * (radius_mm ** 2))

            # Set initial length
            await hass.services.async_call(
                "number", "set_value",
                {"entity_id": f"number.centauri_spool_manager_spool_{spool_num}_initial_length", "value": round(length_mm)},
                blocking=True,
            )

            # Reset used length
            await hass.services.async_call(
                "number", "set_value",
                {"entity_id": f"number.centauri_spool_manager_spool_{spool_num}_used_length", "value": 0},
                blocking=True,
            )

    # Register all services
    hass.services.async_register(
        DOMAIN, "reset_spool", handle_reset_spool, schema=RESET_SPOOL_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "undo_last_print", handle_undo_last_print, schema=UNDO_LAST_PRINT_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "mark_spool_empty", handle_mark_spool_empty, schema=MARK_SPOOL_EMPTY_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "set_spool_weight", handle_set_spool_weight, schema=SET_SPOOL_WEIGHT_SCHEMA
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading Centauri Carbon Spool Manager")

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

        # Unregister services
        hass.services.async_remove(DOMAIN, "reset_spool")
        hass.services.async_remove(DOMAIN, "undo_last_print")
        hass.services.async_remove(DOMAIN, "mark_spool_empty")
        hass.services.async_remove(DOMAIN, "set_spool_weight")

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
