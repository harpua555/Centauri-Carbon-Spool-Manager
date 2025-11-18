"""Switch platform for Centauri Carbon Spool Manager."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
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
    """Set up switch entities."""
    num_spools = entry.data.get(CONF_NUM_SPOOLS, 4)

    entities = [SpoolTrackingSwitch(entry.entry_id)]

    # Add lock switch for each spool
    for i in range(1, num_spools + 1):
        entities.append(SpoolLockSwitch(entry.entry_id, i))

    async_add_entities(entities)


class SpoolTrackingSwitch(SwitchEntity, RestoreEntity):
    """Enable/disable spool tracking switch."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:toggle-switch"

    def __init__(self, entry_id: str):
        """Initialize the switch."""
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_enable_tracking"
        self._attr_name = "Enable Spool Tracking"
        self._attr_is_on = False

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
            self._attr_is_on = last_state.state == "on"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        self._attr_is_on = False
        self.async_write_ha_state()


class SpoolLockSwitch(SwitchEntity, RestoreEntity):
    """Lock switch to prevent accidental spool modifications."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:lock"

    def __init__(self, entry_id: str, spool_num: int):
        """Initialize the lock switch."""
        self._entry_id = entry_id
        self._spool_num = spool_num
        self._attr_unique_id = f"{entry_id}_spool_{spool_num}_lock"
        self._attr_name = f"Spool {spool_num} Lock"
        self._attr_is_on = True  # Locked by default to prevent accidental changes

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Centauri Spool Manager",
            "manufacturer": "Centauri",
            "model": "Spool Manager",
        }

    @property
    def icon(self):
        """Return icon based on lock state."""
        return "mdi:lock" if self._attr_is_on else "mdi:lock-open"

    async def async_added_to_hass(self) -> None:
        """Restore last state."""
        await super().async_added_to_hass()

        if (last_state := await self.async_get_last_state()) is not None:
            self._attr_is_on = last_state.state == "on"

    async def async_turn_on(self, **kwargs) -> None:
        """Lock the spool."""
        self._attr_is_on = True
        self.async_write_ha_state()
        _LOGGER.info(f"Spool {self._spool_num} locked - configuration protected")

    async def async_turn_off(self, **kwargs) -> None:
        """Unlock the spool."""
        self._attr_is_on = False
        self.async_write_ha_state()
        _LOGGER.info(f"Spool {self._spool_num} unlocked - configuration editable")
