"""Number platform for Centauri Carbon Spool Manager."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, CONF_NUM_SPOOLS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities."""
    num_spools = entry.data.get(CONF_NUM_SPOOLS, 4)

    entities = []

    # Global filament diameter
    entities.append(FilamentDiameterNumber(entry.entry_id))

    # Per-spool entities
    for i in range(1, num_spools + 1):
        entities.extend([
            SpoolInitialLengthNumber(entry.entry_id, i),
            SpoolUsedLengthNumber(entry.entry_id, i),
            SpoolDensityNumber(entry.entry_id, i),
            SpoolLastPrintLengthNumber(entry.entry_id, i),
        ])

    async_add_entities(entities)


class CentauriNumberEntity(NumberEntity, RestoreEntity):
    """Base number entity for Centauri Spool Manager."""

    _attr_has_entity_name = True

    def __init__(self, entry_id: str, number_type: str, spool_num: int | None = None):
        """Initialize the number entity."""
        self._entry_id = entry_id
        self._number_type = number_type
        self._spool_num = spool_num

        if spool_num:
            self._attr_unique_id = f"{entry_id}_spool_{spool_num}_{number_type}"
            self._attr_name = f"Spool {spool_num} {number_type.replace('_', ' ').title()}"
        else:
            self._attr_unique_id = f"{entry_id}_{number_type}"
            self._attr_name = number_type.replace('_', ' ').title()

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
                self._attr_native_value = float(last_state.state)


class FilamentDiameterNumber(CentauriNumberEntity):
    """Filament diameter number entity."""

    _attr_native_min_value = 1.0
    _attr_native_max_value = 3.0
    _attr_native_step = 0.05
    _attr_native_unit_of_measurement = "mm"
    _attr_mode = NumberMode.BOX
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, entry_id: str):
        """Initialize filament diameter."""
        super().__init__(entry_id, "filament_diameter")
        self._attr_native_value = 1.75

    async def async_set_native_value(self, value: float) -> None:
        """Update the value."""
        self._attr_native_value = value
        self.async_write_ha_state()


class SpoolInitialLengthNumber(CentauriNumberEntity):
    """Spool initial length number entity."""

    _attr_native_min_value = 0
    _attr_native_max_value = 500000
    _attr_native_step = 100
    _attr_native_unit_of_measurement = "mm"
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:tape-measure"

    def __init__(self, entry_id: str, spool_num: int):
        """Initialize spool initial length."""
        super().__init__(entry_id, "initial_length", spool_num)
        self._attr_native_value = 0

    async def async_set_native_value(self, value: float) -> None:
        """Update the value."""
        self._attr_native_value = value
        self.async_write_ha_state()


class SpoolUsedLengthNumber(CentauriNumberEntity):
    """Spool used length number entity."""

    _attr_native_min_value = 0
    _attr_native_max_value = 500000
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "mm"
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:tape-measure"

    def __init__(self, entry_id: str, spool_num: int):
        """Initialize spool used length."""
        super().__init__(entry_id, "used_length", spool_num)
        self._attr_native_value = 0

    async def async_set_native_value(self, value: float) -> None:
        """Update the value."""
        self._attr_native_value = value
        self.async_write_ha_state()


class SpoolDensityNumber(CentauriNumberEntity):
    """Spool material density number entity."""

    _attr_native_min_value = 0.5
    _attr_native_max_value = 3.0
    _attr_native_step = 0.01
    _attr_native_unit_of_measurement = "g/cm³"
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:weight"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, entry_id: str, spool_num: int):
        """Initialize spool density."""
        super().__init__(entry_id, "density", spool_num)
        self._attr_native_value = 1.24  # Default PLA density

    async def async_set_native_value(self, value: float) -> None:
        """Update the value."""
        self._attr_native_value = value
        self.async_write_ha_state()


class SpoolLastPrintLengthNumber(CentauriNumberEntity):
    """Last print length number entity (for undo)."""

    _attr_native_min_value = 0
    _attr_native_max_value = 500000
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "mm"
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:printer-3d-nozzle"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry_id: str, spool_num: int):
        """Initialize last print length."""
        super().__init__(entry_id, "last_print_length", spool_num)
        self._attr_native_value = 0

    async def async_set_native_value(self, value: float) -> None:
        """Update the value."""
        self._attr_native_value = value
        self.async_write_ha_state()
