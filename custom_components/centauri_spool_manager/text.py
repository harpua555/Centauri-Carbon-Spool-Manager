"""Text platform for Centauri Carbon Spool Manager."""
from __future__ import annotations

import logging

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, CONF_NUM_SPOOLS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up text entities."""
    num_spools = entry.data.get(CONF_NUM_SPOOLS, 4)

    entities = []

    # Per-spool name entities
    for i in range(1, num_spools + 1):
        entities.append(SpoolNameText(entry.entry_id, i))

    # Current print spool tracking
    entities.append(CurrentPrintSpoolText(entry.entry_id))

    async_add_entities(entities)


class CentauriTextEntity(TextEntity, RestoreEntity):
    """Base text entity for Centauri Spool Manager."""

    _attr_has_entity_name = True

    def __init__(self, entry_id: str, text_type: str, spool_num: int | None = None):
        """Initialize the text entity."""
        self._entry_id = entry_id
        self._text_type = text_type
        self._spool_num = spool_num

        if spool_num:
            self._attr_unique_id = f"{entry_id}_spool_{spool_num}_{text_type}"
            self._attr_name = f"Spool {spool_num} {text_type.replace('_', ' ').title()}"
        else:
            self._attr_unique_id = f"{entry_id}_{text_type}"
            self._attr_name = text_type.replace('_', ' ').title()

        self._attr_native_value = None

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Centauri Spool Manager",
            "manufacturer": "Centauri",
            "model": "Spool Manager",
        }

    async def async_added_to_hass(self) -> None:
        """Restore last state."""
        await super().async_added_to_hass()

        if (last_state := await self.async_get_last_state()) is not None:
            if last_state.state not in ("unknown", "unavailable"):
                self._attr_native_value = last_state.state


class SpoolNameText(CentauriTextEntity):
    """Spool name text entity."""

    _attr_icon = "mdi:printer-3d-nozzle"
    _attr_max_length = 50

    def __init__(self, entry_id: str, spool_num: int):
        """Initialize spool name."""
        super().__init__(entry_id, "name", spool_num)
        self._attr_native_value = f"Spool {spool_num}"

    async def async_set_value(self, value: str) -> None:
        """Update the value."""
        self._attr_native_value = value
        self.async_write_ha_state()


class CurrentPrintSpoolText(CentauriTextEntity):
    """Current print spool tracking text entity."""

    _attr_icon = "mdi:printer-3d"
    _attr_max_length = 20

    def __init__(self, entry_id: str):
        """Initialize current print spool."""
        super().__init__(entry_id, "current_print_spool")
        self._attr_native_value = ""

    async def async_set_value(self, value: str) -> None:
        """Update the value."""
        self._attr_native_value = value
        self.async_write_ha_state()
