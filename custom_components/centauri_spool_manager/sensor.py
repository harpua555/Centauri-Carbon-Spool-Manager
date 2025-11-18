"""Sensor platform for Centauri Carbon Spool Manager."""
from __future__ import annotations

import logging
import math

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfLength, UnitOfMass
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, CONF_NUM_SPOOLS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    num_spools = entry.options.get(CONF_NUM_SPOOLS, entry.data.get(CONF_NUM_SPOOLS, 4))

    entities = []

    # Per-spool calculated sensors
    for i in range(1, num_spools + 1):
        entities.extend([
            SpoolRemainingLengthSensor(hass, entry.entry_id, i),
            SpoolRemainingWeightSensor(hass, entry.entry_id, i),
            SpoolInitialWeightSensor(hass, entry.entry_id, i),
            SpoolUsedWeightSensor(hass, entry.entry_id, i),
            SpoolPercentageRemainingSensor(hass, entry.entry_id, i),
            SpoolLastPrintWeightSensor(hass, entry.entry_id, i),
            SpoolStateSensor(hass, entry.entry_id, i),
        ])

    async_add_entities(entities)


class CentauriSensorEntity(SensorEntity):
    """Base sensor entity for Centauri Spool Manager."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, entry_id: str, sensor_type: str, spool_num: int):
        """Initialize the sensor."""
        self.hass = hass
        self._entry_id = entry_id
        self._sensor_type = sensor_type
        self._spool_num = spool_num

        self._attr_unique_id = f"{entry_id}_spool_{spool_num}_{sensor_type}"
        self._attr_name = f"Spool {spool_num} {sensor_type.replace('_', ' ').title()}"

        # Explicit entity_id so dashboard/docs can reference it
        self.entity_id = f"sensor.{DOMAIN}_spool_{spool_num}_{sensor_type}"

        # Track related entities for updates
        self._tracked_entities = []

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
        """Set up state change listener."""
        await super().async_added_to_hass()

        # Listen to related entity changes
        if self._tracked_entities:
            async_track_state_change_event(
                self.hass,
                self._tracked_entities,
                self._handle_state_change,
            )

        # Initial calculation
        self._update_state()

    @callback
    def _handle_state_change(self, event):
        """Handle state changes of tracked entities."""
        self._update_state()
        self.async_write_ha_state()

    def _update_state(self):
        """Update sensor state - to be overridden."""
        pass

    def _get_entity_value(self, entity_id: str, default=0):
        """Get value from entity."""
        state = self.hass.states.get(entity_id)
        if state and state.state not in ("unknown", "unavailable"):
            try:
                return float(state.state)
            except (ValueError, TypeError):
                return default
        return default


class SpoolRemainingLengthSensor(CentauriSensorEntity):
    """Remaining length sensor."""

    _attr_native_unit_of_measurement = UnitOfLength.MILLIMETERS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:tape-measure"

    def __init__(self, hass: HomeAssistant, entry_id: str, spool_num: int):
        """Initialize remaining length sensor."""
        super().__init__(hass, entry_id, "remaining_length", spool_num)
        self._tracked_entities = [
            f"number.centauri_spool_manager_spool_{spool_num}_initial_length",
            f"number.centauri_spool_manager_spool_{spool_num}_used_length",
        ]

    def _update_state(self):
        """Calculate remaining length."""
        initial = self._get_entity_value(self._tracked_entities[0])
        used = self._get_entity_value(self._tracked_entities[1])
        self._attr_native_value = round(max(0, initial - used))


class SpoolRemainingWeightSensor(CentauriSensorEntity):
    """Remaining weight sensor."""

    _attr_native_unit_of_measurement = UnitOfMass.GRAMS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:weight"

    def __init__(self, hass: HomeAssistant, entry_id: str, spool_num: int):
        """Initialize remaining weight sensor."""
        super().__init__(hass, entry_id, "remaining_weight", spool_num)
        self._tracked_entities = [
            f"number.centauri_spool_manager_spool_{spool_num}_initial_length",
            f"number.centauri_spool_manager_spool_{spool_num}_used_length",
            f"number.centauri_spool_manager_spool_{spool_num}_density",
            "number.centauri_spool_manager_filament_diameter",
        ]

    def _update_state(self):
        """Calculate remaining weight."""
        initial_length = self._get_entity_value(self._tracked_entities[0])
        used_length = self._get_entity_value(self._tracked_entities[1])
        density = self._get_entity_value(self._tracked_entities[2], 1.24)
        diameter = self._get_entity_value(self._tracked_entities[3], 1.75)

        remaining_length = max(0, initial_length - used_length)

        # Calculate weight: π * r² * length * density
        # diameter in mm, length in mm, density in g/cm³
        radius_mm = diameter / 2
        volume_mm3 = math.pi * (radius_mm ** 2) * remaining_length
        volume_cm3 = volume_mm3 / 1000  # Convert mm³ to cm³
        weight_g = volume_cm3 * density

        # Round to nearest 0.1 g
        self._attr_native_value = round(weight_g, 1)


class SpoolInitialWeightSensor(CentauriSensorEntity):
    """Initial weight sensor."""

    _attr_native_unit_of_measurement = UnitOfMass.GRAMS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:weight"

    def __init__(self, hass: HomeAssistant, entry_id: str, spool_num: int):
        """Initialize initial weight sensor."""
        super().__init__(hass, entry_id, "initial_weight", spool_num)
        self._tracked_entities = [
            f"number.centauri_spool_manager_spool_{spool_num}_initial_length",
            f"number.centauri_spool_manager_spool_{spool_num}_density",
            "number.centauri_spool_manager_filament_diameter",
        ]

    def _update_state(self):
        """Calculate initial weight."""
        initial_length = self._get_entity_value(self._tracked_entities[0])
        density = self._get_entity_value(self._tracked_entities[1], 1.24)
        diameter = self._get_entity_value(self._tracked_entities[2], 1.75)

        radius_mm = diameter / 2
        volume_mm3 = math.pi * (radius_mm ** 2) * initial_length
        volume_cm3 = volume_mm3 / 1000
        weight_g = volume_cm3 * density

        self._attr_native_value = round(weight_g, 1)


class SpoolUsedWeightSensor(CentauriSensorEntity):
    """Used weight sensor."""

    _attr_native_unit_of_measurement = UnitOfMass.GRAMS
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:weight"

    def __init__(self, hass: HomeAssistant, entry_id: str, spool_num: int):
        """Initialize used weight sensor."""
        super().__init__(hass, entry_id, "used_weight", spool_num)
        self._tracked_entities = [
            f"number.centauri_spool_manager_spool_{spool_num}_used_length",
            f"number.centauri_spool_manager_spool_{spool_num}_density",
            "number.centauri_spool_manager_filament_diameter",
        ]

    def _update_state(self):
        """Calculate used weight."""
        used_length = self._get_entity_value(self._tracked_entities[0])
        density = self._get_entity_value(self._tracked_entities[1], 1.24)
        diameter = self._get_entity_value(self._tracked_entities[2], 1.75)

        radius_mm = diameter / 2
        volume_mm3 = math.pi * (radius_mm ** 2) * used_length
        volume_cm3 = volume_mm3 / 1000
        weight_g = volume_cm3 * density

        self._attr_native_value = round(weight_g, 1)


class SpoolPercentageRemainingSensor(CentauriSensorEntity):
    """Percentage remaining sensor."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:percent"

    def __init__(self, hass: HomeAssistant, entry_id: str, spool_num: int):
        """Initialize percentage remaining sensor."""
        super().__init__(hass, entry_id, "percentage_remaining", spool_num)
        self._tracked_entities = [
            f"number.centauri_spool_manager_spool_{spool_num}_initial_length",
            f"number.centauri_spool_manager_spool_{spool_num}_used_length",
        ]

    def _update_state(self):
        """Calculate percentage remaining."""
        initial = self._get_entity_value(self._tracked_entities[0])
        used = self._get_entity_value(self._tracked_entities[1])

        if initial > 0:
            remaining = max(0, initial - used)
            percentage = (remaining / initial) * 100
            self._attr_native_value = round(percentage, 1)
        else:
            self._attr_native_value = 0


class SpoolLastPrintWeightSensor(CentauriSensorEntity):
    """Last print weight sensor."""

    _attr_native_unit_of_measurement = UnitOfMass.GRAMS
    _attr_icon = "mdi:printer-3d-nozzle"

    def __init__(self, hass: HomeAssistant, entry_id: str, spool_num: int):
        """Initialize last print weight sensor."""
        super().__init__(hass, entry_id, "last_print_weight", spool_num)
        self._tracked_entities = [
            f"number.centauri_spool_manager_spool_{spool_num}_last_print_length",
            f"number.centauri_spool_manager_spool_{spool_num}_density",
            "number.centauri_spool_manager_filament_diameter",
        ]

    def _update_state(self):
        """Calculate last print weight."""
        last_print_length = self._get_entity_value(self._tracked_entities[0])
        density = self._get_entity_value(self._tracked_entities[1], 1.24)
        diameter = self._get_entity_value(self._tracked_entities[2], 1.75)

        radius_mm = diameter / 2
        volume_mm3 = math.pi * (radius_mm ** 2) * last_print_length
        volume_cm3 = volume_mm3 / 1000
        weight_g = volume_cm3 * density

        self._attr_native_value = round(weight_g, 1)


class SpoolStateSensor(SensorEntity):
    """Sensor to track spool state (ready, configured, active, empty)."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_icon = "mdi:state-machine"

    def __init__(self, hass: HomeAssistant, entry_id: str, spool_num: int):
        """Initialize state sensor."""
        self.hass = hass
        self._entry_id = entry_id
        self._spool_num = spool_num
        self._attr_unique_id = f"{entry_id}_spool_{spool_num}_state"
        self._attr_name = f"Spool {spool_num} State"
        self._attr_native_value = "ready"
        self.entity_id = f"sensor.{DOMAIN}_spool_{spool_num}_state"

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
        """Register state change listeners."""
        # Track relevant entities
        entities_to_track = [
            f"number.centauri_spool_manager_spool_{self._spool_num}_initial_length",
            f"number.centauri_spool_manager_spool_{self._spool_num}_used_length",
            f"switch.centauri_spool_manager_spool_{self._spool_num}_lock",
            f"select.centauri_spool_manager_active_spool",
        ]

        async_track_state_change_event(
            self.hass, entities_to_track, self._handle_state_change
        )

        # Calculate initial state
        self._update_state()

    @callback
    def _handle_state_change(self, event):
        """Handle state changes of tracked entities."""
        self._update_state()

    def _update_state(self):
        """Calculate current spool state."""
        # Get entity states
        initial_length_state = self.hass.states.get(
            f"number.centauri_spool_manager_spool_{self._spool_num}_initial_length"
        )
        used_length_state = self.hass.states.get(
            f"number.centauri_spool_manager_spool_{self._spool_num}_used_length"
        )
        lock_state = self.hass.states.get(
            f"switch.centauri_spool_manager_spool_{self._spool_num}_lock"
        )
        active_spool_state = self.hass.states.get(
            "select.centauri_spool_manager_active_spool"
        )

        # Determine state
        if not initial_length_state or initial_length_state.state in ("unknown", "unavailable"):
            self._attr_native_value = "ready"
        else:
            initial_length = float(initial_length_state.state)
            used_length = float(used_length_state.state) if used_length_state and used_length_state.state not in ("unknown", "unavailable") else 0

            # Check if empty
            if used_length >= initial_length and initial_length > 0:
                self._attr_native_value = "empty"
            # Check if active
            elif active_spool_state and active_spool_state.state == f"Spool {self._spool_num}":
                self._attr_native_value = "active"
            # Check if configured
            elif initial_length > 0:
                self._attr_native_value = "configured"
            else:
                self._attr_native_value = "ready"

        self.async_write_ha_state()
