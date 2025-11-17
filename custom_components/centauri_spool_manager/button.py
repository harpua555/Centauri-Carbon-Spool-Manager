"""Button platform for Centauri Carbon Spool Manager."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_NUM_SPOOLS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities."""
    num_spools = entry.data.get(CONF_NUM_SPOOLS, 4)

    buttons = []
    for spool_num in range(1, num_spools + 1):
        buttons.extend([
            SpoolResetButton(spool_num),
            SpoolMarkEmptyButton(spool_num),
            SpoolUndoButton(spool_num),
        ])

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
        """Handle the button press."""
        await self.hass.services.async_call(
            DOMAIN,
            "mark_spool_empty",
            {"spool_number": self._spool_num},
            blocking=True,
        )


class SpoolUndoButton(ButtonEntity):
    """Button to undo last print on a spool."""

    def __init__(self, spool_num: int) -> None:
        """Initialize the button."""
        self._spool_num = spool_num
        self._attr_name = f"Centauri Spool Manager Spool {spool_num} Undo Last Print"
        self._attr_unique_id = f"centauri_spool_manager_spool_{spool_num}_undo"
        self._attr_icon = "mdi:undo"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.hass.services.async_call(
            DOMAIN,
            "undo_last_print",
            {"spool_number": self._spool_num},
            blocking=True,
        )
