"""Button platform for Centauri Carbon Spool Manager."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_NUM_SPOOLS

_LOGGER = logging.getLogger(__name__)


class AddNewSpoolButton(ButtonEntity):
    """Button to add a new spool using form values."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:plus-circle"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, hass: HomeAssistant, entry_id: str):
        """Initialize the button."""
        self.hass = hass
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_add_new_spool"
        self._attr_name = "Centauri Spool Manager Add New Spool"
        self.entity_id = "button.centauri_spool_manager_add_new_spool"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Centauri Spool Manager",
            "manufacturer": "Centauri",
            "model": "Spool Manager",
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        # Get values from form entities
        slot_entity = f"select.centauri_spool_manager_new_spool_slot"
        name_entity = f"text.centauri_spool_manager_new_spool_name"
        material_entity = f"select.centauri_spool_manager_new_spool_material"
        weight_entity = f"number.centauri_spool_manager_new_spool_weight"
        auto_lock_entity = f"switch.centauri_spool_manager_new_spool_auto_lock"

        slot_state = self.hass.states.get(slot_entity)
        name_state = self.hass.states.get(name_entity)
        material_state = self.hass.states.get(material_entity)
        weight_state = self.hass.states.get(weight_entity)
        auto_lock_state = self.hass.states.get(auto_lock_entity)

        if not all([slot_state, name_state, material_state, weight_state, auto_lock_state]):
            _LOGGER.error("Add Spool form entities not found")
            return

        # Slot is provided as a string option ("1".."4")
        spool_number = int(slot_state.state) if slot_state.state and slot_state.state.isdigit() else 1
        name = name_state.state
        material = material_state.state
        weight_grams = float(weight_state.state)
        auto_lock = auto_lock_state.state == "on"

        if not name:
            _LOGGER.warning("Spool name is required")
            return

        # Check current spool state to avoid overwriting an in-use spool
        spool_state_entity = f"sensor.centauri_spool_manager_spool_{spool_number}_state"
        spool_state = self.hass.states.get(spool_state_entity)
        if spool_state and spool_state.state not in ("unknown", "unavailable"):
            if spool_state.state not in ("ready", "empty"):
                _LOGGER.warning(
                    "Cannot add new spool to slot %s because its state is %s (must be ready or empty)",
                    spool_number,
                    spool_state.state,
                )
                return

        # Call the setup_spool service
        await self.hass.services.async_call(
            DOMAIN,
            "setup_spool",
            {
                "spool_number": spool_number,
                "name": name,
                "material": material,
                "weight_grams": weight_grams,
                "auto_lock": auto_lock,
            },
            blocking=True,
        )

        # Clear the name field
        await self.hass.services.async_call(
            "text",
            "set_value",
            {"entity_id": name_entity, "value": ""},
            blocking=True,
        )

        _LOGGER.info(f"Added {name} to Spool {spool_number}")


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities."""
    num_spools = entry.options.get(CONF_NUM_SPOOLS, entry.data.get(CONF_NUM_SPOOLS, 4))

    buttons: list[ButtonEntity] = []

    # Global "Add New Spool" helper
    buttons.append(AddNewSpoolButton(hass, entry.entry_id))

    # Per-spool management buttons
    for spool_num in range(1, num_spools + 1):
        buttons.extend(
            [
                SpoolResetButton(spool_num),
                SpoolMarkEmptyButton(spool_num),
                SpoolUndoButton(spool_num),
            ]
        )

    async_add_entities(buttons)


class SpoolResetButton(ButtonEntity):
    """Button to reset a spool."""

    def __init__(self, spool_num: int) -> None:
        """Initialize the button."""
        self._spool_num = spool_num
        self._attr_name = f"Centauri Spool Manager Spool {spool_num} Reset"
        self._attr_unique_id = f"centauri_spool_manager_spool_{spool_num}_reset"
        self._attr_icon = "mdi:refresh"

    async def async_press(self) -> None:
        """Handle the button press."""
        # Unlock spool before reset
        lock_entity_id = f"switch.centauri_spool_manager_spool_{self._spool_num}_lock"
        await self.hass.services.async_call(
            "switch",
            "turn_off",
            {"entity_id": lock_entity_id},
            blocking=True,
        )

        # Reset the spool
        await self.hass.services.async_call(
            DOMAIN,
            "reset_spool",
            {"spool_number": self._spool_num},
            blocking=True,
        )


class SpoolMarkEmptyButton(ButtonEntity):
    """Button to mark a spool as empty."""

    def __init__(self, spool_num: int) -> None:
        """Initialize the button."""
        self._spool_num = spool_num
        self._attr_name = f"Centauri Spool Manager Spool {spool_num} Mark Empty"
        self._attr_unique_id = f"centauri_spool_manager_spool_{spool_num}_mark_empty"
        self._attr_icon = "mdi:checkbox-blank-circle-outline"

    async def async_press(self) -> None:
        """Handle the button press - implements Quick Reload."""
        # Store current configuration for quick reload
        name_entity = f"text.centauri_spool_manager_spool_{self._spool_num}_name"
        material_entity = f"select.centauri_spool_manager_spool_{self._spool_num}_material"
        weight_entity = f"number.centauri_spool_manager_spool_{self._spool_num}_set_weight"

        name_state = self.hass.states.get(name_entity)
        material_state = self.hass.states.get(material_entity)
        weight_state = self.hass.states.get(weight_entity)

        # Mark empty
        await self.hass.services.async_call(
            DOMAIN,
            "mark_spool_empty",
            {"spool_number": self._spool_num},
            blocking=True,
        )

        # Quick Reload: Reset with same configuration
        # Unlock spool
        lock_entity_id = f"switch.centauri_spool_manager_spool_{self._spool_num}_lock"
        await self.hass.services.async_call(
            "switch",
            "turn_off",
            {"entity_id": lock_entity_id},
            blocking=True,
        )

        # Reset the spool
        await self.hass.services.async_call(
            DOMAIN,
            "reset_spool",
            {"spool_number": self._spool_num},
            blocking=True,
        )

        # Restore previous configuration if it existed
        if weight_state and weight_state.state not in ("unknown", "unavailable"):
            await self.hass.services.async_call(
                DOMAIN,
                "set_spool_weight",
                {"spool_number": self._spool_num, "weight_grams": float(weight_state.state)},
                blocking=True,
            )


class SpoolUndoButton(ButtonEntity):
    """Button to undo last print on a spool."""

    def __init__(self, spool_num: int) -> None:
        """Initialize the button."""
        self._spool_num = spool_num
        self._attr_name = f"Centauri Spool Manager Spool {spool_num} Undo Last Print"
        # Match dashboard/entity ID naming
        self._attr_unique_id = f"centauri_spool_manager_spool_{spool_num}_undo_last_print"
        self._attr_icon = "mdi:undo"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.hass.services.async_call(
            DOMAIN,
            "undo_last_print",
            {"spool_number": self._spool_num},
            blocking=True,
        )
