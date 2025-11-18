"""Switch platform for Centauri Carbon Spool Manager."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, CONF_NUM_SPOOLS

_LOGGER = logging.getLogger(__name__)


class NewSpoolAutoLockSwitch(SwitchEntity, RestoreEntity):
    """Switch for auto-locking new spools."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:lock"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, entry_id: str) -> None:
        """Initialize the switch."""
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_new_spool_auto_lock"
        self._attr_name = "Centauri Spool Manager New Spool Auto Lock"
        self._attr_is_on = True  # Default to auto-lock
        self.entity_id = "switch.centauri_spool_manager_new_spool_auto_lock"

    @property
    def device_info(self) -> dict:
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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities."""
    num_spools = entry.options.get(CONF_NUM_SPOOLS, entry.data.get(CONF_NUM_SPOOLS, 4))

    entities: list[SwitchEntity] = [SpoolTrackingSwitch(entry.entry_id)]

    # Add Spool form helper
    entities.append(NewSpoolAutoLockSwitch(entry.entry_id))

    # Add lock switch for each spool
    for spool_num in range(1, num_spools + 1):
        entities.append(SpoolLockSwitch(entry.entry_id, spool_num))

    async_add_entities(entities)


class SpoolTrackingSwitch(SwitchEntity, RestoreEntity):
    """Enable/disable spool tracking switch."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:toggle-switch"

    def __init__(self, entry_id: str) -> None:
        """Initialize the switch."""
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_enable_tracking"
        self._attr_name = "Centauri Spool Manager Enable Spool Tracking"
        self._attr_is_on = False
        self.entity_id = "switch.centauri_spool_manager_enable_spool_tracking"

    @property
    def device_info(self) -> dict:
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

    def __init__(self, entry_id: str, spool_num: int) -> None:
        """Initialize the lock switch."""
        self._entry_id = entry_id
        self._spool_num = spool_num
        self._attr_unique_id = f"{entry_id}_spool_{spool_num}_lock"
        self._attr_name = f"Spool {spool_num} Lock"
        self._attr_is_on = True  # Locked by default to prevent accidental changes
        self.entity_id = f"switch.centauri_spool_manager_spool_{spool_num}_lock"

    @property
    def device_info(self) -> dict:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Centauri Spool Manager",
            "manufacturer": "Centauri",
            "model": "Spool Manager",
        }

    @property
    def icon(self) -> str:
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
        _LOGGER.info("Spool %s locked - configuration protected", self._spool_num)

    async def async_turn_off(self, **kwargs) -> None:
        """Unlock the spool."""
        self._attr_is_on = False
        self.async_write_ha_state()
        _LOGGER.info("Spool %s unlocked - configuration editable", self._spool_num)

