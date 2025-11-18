"""Centauri Carbon Spool Manager Integration."""
from __future__ import annotations

import json
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

UNDO_HISTORY_ENTRY_SCHEMA = vol.Schema(
    {
        vol.Required("spool_number"): cv.positive_int,
        # Zero-based index into the history list (oldest entry = 0)
        vol.Required("entry_index"): vol.All(int, vol.Range(min=0)),
    }
)

SET_SPOOL_WEIGHT_SCHEMA = vol.Schema({
    vol.Required("spool_number"): cv.positive_int,
    vol.Required("weight_grams"): cv.positive_float,
})

SETUP_SPOOL_SCHEMA = vol.Schema({
    vol.Required("spool_number"): cv.positive_int,
    vol.Required("name"): cv.string,
    vol.Required("material"): cv.string,
    vol.Required("weight_grams"): cv.positive_float,
    vol.Optional("auto_lock", default=True): cv.boolean,
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

    # Auto-create dashboard (respect options override)
    num_spools = entry.options.get(CONF_NUM_SPOOLS, entry.data.get(CONF_NUM_SPOOLS, 4))
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
                # Round to nearest mm
                new_used = round(new_used)

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

    async def handle_undo_history_entry(call: ServiceCall) -> None:
        """Handle undo of a specific history entry."""
        spool_num = call.data["spool_number"]
        entry_index = call.data["entry_index"]
        _LOGGER.info(
            "Undoing history entry %s for spool %s", entry_index, spool_num
        )

        history_entity_id = f"text.centauri_spool_manager_spool_{spool_num}_history"
        used_length_entity = f"number.centauri_spool_manager_spool_{spool_num}_used_length"

        history_state = hass.states.get(history_entity_id)
        used_state = hass.states.get(used_length_entity)

        if (
            not history_state
            or history_state.state in ("unknown", "unavailable", "")
        ):
            _LOGGER.warning(
                "No history available for spool %s when undo was requested", spool_num
            )
            return

        try:
            # History is stored as a JSON list; make sure we always have a list.
            entries = cv.ensure_list(json.loads(history_state.state))
        except Exception:  # noqa: BLE001
            _LOGGER.error(
                "Failed to parse history JSON for spool %s during undo", spool_num
            )
            return

        if not entries:
            _LOGGER.warning(
                "History for spool %s is empty; nothing to undo", spool_num
            )
            return

        if entry_index < 0 or entry_index >= len(entries):
            _LOGGER.warning(
                "History index %s out of range for spool %s (len=%s)",
                entry_index,
                spool_num,
                len(entries),
            )
            return

        # Oldest entry is index 0; keep that convention
        entry = entries.pop(entry_index)
        length_mm = float(entry.get("length_mm", 0))

        if used_state and used_state.state not in ("unknown", "unavailable"):
            try:
                current_used = float(used_state.state)
            except (ValueError, TypeError):
                current_used = 0

            new_used = max(0, current_used - length_mm)
            new_used = round(new_used)

            await hass.services.async_call(
                "number",
                "set_value",
                {"entity_id": used_length_entity, "value": new_used},
                blocking=True,
            )

        # Persist updated history
        await hass.services.async_call(
            "text",
            "set_value",
            {"entity_id": history_entity_id, "value": json.dumps(entries)},
            blocking=True,
        )

        await hass.services.async_call(
            "logbook",
            "log",
            {
                "name": "Centauri Spool Manager",
                "message": (
                    f"Undid history entry for Spool {spool_num}: "
                    f"{entry.get('file', 'Unknown file')} "
                    f"({length_mm:.0f}mm)"
                ),
            },
            blocking=False,
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

    async def handle_setup_spool(call: ServiceCall) -> None:
        """Handle setup spool service - wizard-style all-in-one configuration."""
        spool_num = call.data["spool_number"]
        name = call.data["name"]
        material = call.data["material"]
        weight_grams = call.data["weight_grams"]
        auto_lock = call.data.get("auto_lock", True)

        _LOGGER.info(f"Setting up spool {spool_num}: {name} ({material}, {weight_grams}g)")

        # Prevent overwriting a non-empty/non-ready spool
        spool_state_entity = f"sensor.centauri_spool_manager_spool_{spool_num}_state"
        spool_state = hass.states.get(spool_state_entity)
        if spool_state and spool_state.state not in ("unknown", "unavailable"):
            # Only allow setup for "ready" (never configured) or "empty" (explicitly marked empty)
            if spool_state.state not in ("ready", "empty"):
                _LOGGER.warning(
                    "Refusing to configure Spool %s because its state is %s (must be ready or empty)",
                    spool_num,
                    spool_state.state,
                )
                raise ValueError(
                    f"Spool {spool_num} is currently {spool_state.state}. "
                    "Mark it empty or reset it before configuring a new spool."
                )

        # Step 1: Unlock spool
        await hass.services.async_call(
            "switch", "turn_off",
            {"entity_id": f"switch.centauri_spool_manager_spool_{spool_num}_lock"},
            blocking=True,
        )

        # Step 2: Set name
        await hass.services.async_call(
            "text", "set_value",
            {"entity_id": f"text.centauri_spool_manager_spool_{spool_num}_name", "value": name},
            blocking=True,
        )

        # Step 3: Set material
        await hass.services.async_call(
            "select", "select_option",
            {"entity_id": f"select.centauri_spool_manager_spool_{spool_num}_material", "option": material},
            blocking=True,
        )

        # Step 4: Set weight (which calculates length automatically)
        await hass.services.async_call(
            DOMAIN, "set_spool_weight",
            {"spool_number": spool_num, "weight_grams": weight_grams},
            blocking=True,
        )

        # Step 5: Lock spool if requested
        if auto_lock:
            await hass.services.async_call(
                "switch", "turn_on",
                {"entity_id": f"switch.centauri_spool_manager_spool_{spool_num}_lock"},
                blocking=True,
            )
            _LOGGER.info(f"Spool {spool_num} configured and locked")
        else:
            _LOGGER.info(f"Spool {spool_num} configured (unlocked)")

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
    hass.services.async_register(
        DOMAIN, "setup_spool", handle_setup_spool, schema=SETUP_SPOOL_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        "undo_history_entry",
        handle_undo_history_entry,
        schema=UNDO_HISTORY_ENTRY_SCHEMA,
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
        hass.services.async_remove(DOMAIN, "setup_spool")
        hass.services.async_remove(DOMAIN, "undo_history_entry")

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
