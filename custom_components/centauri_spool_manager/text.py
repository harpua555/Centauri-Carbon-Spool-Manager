"""Text platform for Centauri Carbon Spool Manager."""
from __future__ import annotations

import json
import logging

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, CONF_NUM_SPOOLS

_LOGGER = logging.getLogger(__name__)


class NewSpoolNameText(TextEntity, RestoreEntity):
    """Text entity for new spool name."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:label"
    _attr_max_length = 50
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, entry_id: str):
        """Initialize the text entity."""
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_new_spool_name"
        self._attr_name = "Centauri Spool Manager New Spool Name"
        self._attr_native_value = ""
        self.entity_id = "text.centauri_spool_manager_new_spool_name"

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

    async def async_set_value(self, value: str) -> None:
        """Update the value."""
        self._attr_native_value = value
        self.async_write_ha_state()


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up text entities."""
    num_spools = entry.options.get(CONF_NUM_SPOOLS, entry.data.get(CONF_NUM_SPOOLS, 4))

    entities = []

    # Add Spool form helper
    entities.append(NewSpoolNameText(entry.entry_id))

    # Per-spool name, URL, and history entities
    for i in range(1, num_spools + 1):
        entities.append(SpoolNameText(entry.entry_id, i))
        entities.append(SpoolUrlText(entry.entry_id, i))
        entities.append(SpoolHistoryText(entry.entry_id, i))

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
            self.entity_id = f"text.{DOMAIN}_spool_{spool_num}_{text_type}"
        else:
            self._attr_unique_id = f"{entry_id}_{text_type}"
            self._attr_name = text_type.replace("_", " ").title()
            self.entity_id = f"text.{DOMAIN}_{text_type}"

        self._attr_native_value = None

    async def async_set_value(self, value: str) -> None:
        """Update the value for generic text entities."""
        self._attr_native_value = value
        self.async_write_ha_state()

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
        # Check if spool is locked
        lock_entity_id = f"switch.centauri_spool_manager_spool_{self._spool_num}_lock"
        lock_state = self.hass.states.get(lock_entity_id)

        if lock_state and lock_state.state == "on":
            _LOGGER.warning(f"Cannot change Spool {self._spool_num} name - spool is locked")
            raise ValueError(f"Spool {self._spool_num} is locked. Unlock it before making changes.")

        self._attr_native_value = value
        self.async_write_ha_state()


class SpoolUrlText(CentauriTextEntity):
    """Spool product URL text entity."""

    _attr_icon = "mdi:link"
    _attr_max_length = 255
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, entry_id: str, spool_num: int):
        """Initialize spool URL."""
        super().__init__(entry_id, "url", spool_num)
        self._attr_native_value = ""


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


class SpoolHistoryText(CentauriTextEntity):
    """Per-spool print history stored as JSON."""

    _attr_icon = "mdi:history"
    # Allow reasonably long JSON payloads when called via text.set_value.
    # The actual HA state string will only be a short summary.
    _attr_max_length = 10000

    def __init__(self, entry_id: str, spool_num: int):
        """Initialize spool history."""
        super().__init__(entry_id, "history", spool_num)
        # Internal Python list of history entries; persisted via attributes.
        self._history: list[dict] = []
        # State shows a short summary (number of entries) to stay well under
        # Home Assistant's 255-character state length limit.
        self._attr_native_value = "0"

    async def async_added_to_hass(self) -> None:
        """Restore history from last state attributes."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None:
            hist = last_state.attributes.get("history")
            if isinstance(hist, list):
                self._history = hist
                self._attr_native_value = str(len(self._history))

    @property
    def extra_state_attributes(self):
        """Expose full history in attributes, not in state string."""
        return {"history": self._history}

    @property
    def max(self) -> int:
        """Maximum allowed length for the history JSON string."""
        return self._attr_max_length

    async def async_set_value(self, value: str) -> None:
        """Update history from a JSON string.

        The coordinator calls text.set_value with the full JSON list. To avoid
        hitting the global 255-character state length limit, we parse that JSON
        into an internal list and keep the entity state as a short summary
        (entry count), while exposing the full list via attributes.
        """
        try:
            data = json.loads(value)
            if isinstance(data, list):
                self._history = data
                self._attr_native_value = str(len(self._history))
            else:
                _LOGGER.warning(
                    "History text for spool %s was not a list, ignoring", self._spool_num
                )
                return
        except (ValueError, TypeError) as err:
            _LOGGER.warning(
                "Failed to decode history JSON for spool %s: %s", self._spool_num, err
            )
            return

        self.async_write_ha_state()
