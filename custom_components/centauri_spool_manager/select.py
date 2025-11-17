"""Select platform for Centauri Carbon Spool Manager."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, CONF_NUM_SPOOLS, MATERIAL_TYPES, MATERIAL_DENSITIES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities."""
    num_spools = entry.data.get(CONF_NUM_SPOOLS, 4)

    entities = []

    # Active spool selector
    entities.append(ActiveSpoolSelect(entry.entry_id, num_spools))

    # Per-spool material selectors
    for i in range(1, num_spools + 1):
        entities.append(SpoolMaterialSelect(entry.entry_id, i))

    async_add_entities(entities)


class CentauriSelectEntity(SelectEntity, RestoreEntity):
    """Base select entity for Centauri Spool Manager."""

    _attr_has_entity_name = True

    def __init__(self, entry_id: str, select_type: str, spool_num: int | None = None):
        """Initialize the select entity."""
        self._entry_id = entry_id
        self._select_type = select_type
        self._spool_num = spool_num

        if spool_num:
            self._attr_unique_id = f"{entry_id}_spool_{spool_num}_{select_type}"
            self._attr_name = f"Spool {spool_num} {select_type.replace('_', ' ').title()}"
        else:
            self._attr_unique_id = f"{entry_id}_{select_type}"
            self._attr_name = select_type.replace('_', ' ').title()

        self._attr_current_option = None

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
                if last_state.state in self.options:
                    self._attr_current_option = last_state.state


class ActiveSpoolSelect(CentauriSelectEntity):
    """Active spool selector."""

    _attr_icon = "mdi:printer-3d-nozzle-outline"

    def __init__(self, entry_id: str, num_spools: int):
        """Initialize active spool select."""
        super().__init__(entry_id, "active_spool")

        self._attr_options = ["None"] + [f"Spool {i}" for i in range(1, num_spools + 1)]
        self._attr_current_option = "None"

    async def async_select_option(self, option: str) -> None:
        """Update the selected option."""
        self._attr_current_option = option
        self.async_write_ha_state()


class SpoolMaterialSelect(CentauriSelectEntity):
    """Spool material type selector."""

    _attr_icon = "mdi:chemical-weapon"
    _attr_options = MATERIAL_TYPES

    def __init__(self, entry_id: str, spool_num: int):
        """Initialize spool material select."""
        super().__init__(entry_id, "material", spool_num)
        self._attr_current_option = "PLA"
        self._spool_num = spool_num

    async def async_select_option(self, option: str) -> None:
        """Update the selected option."""
        self._attr_current_option = option
        self.async_write_ha_state()

        # Update density when material changes
        if option in MATERIAL_DENSITIES:
            density_entity_id = f"number.centauri_spool_manager_spool_{self._spool_num}_density"
            await self.hass.services.async_call(
                "number",
                "set_value",
                {"entity_id": density_entity_id, "value": MATERIAL_DENSITIES[option]},
                blocking=True,
            )
