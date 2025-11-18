"""Data coordinator for Centauri Carbon Spool Manager."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, CONF_PRINTER_DEVICE

_LOGGER = logging.getLogger(__name__)


class CentauriSpoolCoordinator(DataUpdateCoordinator):
    """Coordinator to handle spool tracking automation."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
        )
        self.entry = entry
        self.printer_device_id = entry.data.get(CONF_PRINTER_DEVICE)
        self._tracking_active = False
        self._print_start_extrusion = 0
        self._active_spool = None

        # Track printer status and extrusion
        self._setup_listeners()

    def _setup_listeners(self):
        """Set up state change listeners for printer."""
        # Find printer entities
        entity_registry = er.async_get(self.hass)

        # Look for total_extrusion, current_status and file_name entities
        self.extrusion_entity = None
        self.status_entity = None
        self.file_name_entity = None

        for entity in entity_registry.entities.values():
            if entity.device_id == self.printer_device_id:
                if entity.entity_id.endswith("_total_extrusion"):
                    self.extrusion_entity = entity.entity_id
                elif entity.entity_id.endswith("_current_status"):
                    self.status_entity = entity.entity_id
                elif entity.entity_id.endswith("_file_name"):
                    self.file_name_entity = entity.entity_id

        if not self.extrusion_entity or not self.status_entity:
            _LOGGER.warning("Could not find printer extrusion or status entities")
            return

        # Listen to printer status changes
        async_track_state_change_event(
            self.hass,
            [self.status_entity],
            self._handle_printer_status_change,
        )

        # Listen to extrusion changes (during print)
        async_track_state_change_event(
            self.hass,
            [self.extrusion_entity],
            self._handle_extrusion_change,
        )

        # Listen to tracking switch
        async_track_state_change_event(
            self.hass,
            ["switch.centauri_spool_manager_enable_spool_tracking"],
            self._handle_tracking_toggle,
        )

        # Listen to active spool selector
        async_track_state_change_event(
            self.hass,
            ["select.centauri_spool_manager_active_spool"],
            self._handle_active_spool_change,
        )

    @callback
    def _handle_printer_status_change(self, event):
        """Handle printer status changes."""
        new_state = event.data.get("new_state")
        old_state = event.data.get("old_state")

        if not new_state or not old_state:
            return

        new_status = new_state.state
        old_status = old_state.state

        _LOGGER.debug(f"Printer status changed from {old_status} to {new_status}")

        # Check if print started
        if new_status.lower() in ("printing", "running") and old_status.lower() not in ("printing", "running"):
            self.hass.async_create_task(self._handle_print_start())

        # Check if print ended
        elif old_status.lower() in ("printing", "running") and new_status.lower() not in ("printing", "running"):
            self.hass.async_create_task(self._handle_print_end(new_status))

    @callback
    def _handle_extrusion_change(self, event):
        """Handle extrusion sensor changes during print."""
        if not self._tracking_active:
            return

        new_state = event.data.get("new_state")
        if not new_state or new_state.state in ("unknown", "unavailable"):
            return

        # Update spool usage every minute during print
        self.hass.async_create_task(self._update_spool_usage())

    @callback
    def _handle_tracking_toggle(self, event):
        """Handle tracking enable/disable."""
        new_state = event.data.get("new_state")
        if new_state:
            is_on = new_state.state == "on"
            _LOGGER.info(f"Spool tracking {'enabled' if is_on else 'disabled'}")

    @callback
    def _handle_active_spool_change(self, event):
        """Handle active spool selection change."""
        new_state = event.data.get("new_state")
        if new_state:
            self._active_spool = new_state.state
            _LOGGER.info(f"Active spool changed to: {self._active_spool}")

    async def _handle_print_start(self):
        """Handle print start event."""
        # Check if tracking is enabled
        tracking_state = self.hass.states.get("switch.centauri_spool_manager_enable_spool_tracking")
        if not tracking_state or tracking_state.state != "on":
            _LOGGER.debug("Tracking not enabled, skipping print start")
            return

        # Get active spool
        active_spool_state = self.hass.states.get("select.centauri_spool_manager_active_spool")
        if not active_spool_state or active_spool_state.state == "None":
            _LOGGER.warning("No active spool selected")
            return

        self._active_spool = active_spool_state.state

        # Get current extrusion value
        extrusion_state = self.hass.states.get(self.extrusion_entity)
        if extrusion_state and extrusion_state.state not in ("unknown", "unavailable"):
            self._print_start_extrusion = float(extrusion_state.state)
            self._tracking_active = True

            _LOGGER.info(f"Print started on {self._active_spool}, starting extrusion: {self._print_start_extrusion}mm")

            # Store current spool name for history
            await self.hass.services.async_call(
                "text", "set_value",
                {"entity_id": "text.centauri_spool_manager_current_print_spool", "value": self._active_spool},
                blocking=True,
            )

    async def _handle_print_end(self, end_status: str):
        """Handle print end event."""
        if not self._tracking_active:
            return

        self._tracking_active = False

        # Get final extrusion value
        extrusion_state = self.hass.states.get(self.extrusion_entity)
        if not extrusion_state or extrusion_state.state in ("unknown", "unavailable"):
            _LOGGER.warning("Could not get final extrusion value")
            return

        final_extrusion = float(extrusion_state.state)
        extruded_length = final_extrusion - self._print_start_extrusion
        extruded_length = round(extruded_length)

        _LOGGER.info(f"Print ended ({end_status}), extruded: {extruded_length}mm on {self._active_spool}")

        # Update spool usage
        if self._active_spool and self._active_spool != "None":
            # Extract spool number
            spool_num = self._active_spool.replace("Spool ", "")

            # Update used length
            used_length_entity = f"number.centauri_spool_manager_spool_{spool_num}_used_length"
            used_state = self.hass.states.get(used_length_entity)

            if used_state and used_state.state not in ("unknown", "unavailable"):
                current_used = float(used_state.state)
                new_used = current_used + extruded_length
                new_used = round(new_used)

                await self.hass.services.async_call(
                    "number", "set_value",
                    {"entity_id": used_length_entity, "value": new_used},
                    blocking=True,
                )

                # Store last print length for undo
                await self.hass.services.async_call(
                    "number", "set_value",
                    {"entity_id": f"number.centauri_spool_manager_spool_{spool_num}_last_print_length", "value": extruded_length},
                    blocking=True,
                )

                # Log to history (logbook)
                spool_name_state = self.hass.states.get(f"text.centauri_spool_manager_spool_{spool_num}_name")
                spool_name = spool_name_state.state if spool_name_state else f"Spool {spool_num}"

                await self.hass.services.async_call(
                    "logbook", "log",
                    {
                        "name": "Centauri Spool Manager",
                        "message": f"Print completed on {spool_name}: Used {extruded_length:.0f}mm",
                        # Attach to the printer's status entity when available so
                        # entries appear in the printer's logbook timeline.
                        "entity_id": self.status_entity
                        or f"sensor.centauri_spool_manager_spool_{spool_num}_remaining_length",
                    },
                    blocking=False,
                )

                # Append to per-spool print history entity
                await self._append_print_history(spool_num, spool_name, extruded_length)

        # Reset tracking state
        self._print_start_extrusion = 0
        self._active_spool = None

    async def _append_print_history(self, spool_num: str, spool_name: str, extruded_length: float) -> None:
        """Append a completed print entry to the spool's history text entity."""
        history_entity_id = f"text.centauri_spool_manager_spool_{spool_num}_history"
        history_state = self.hass.states.get(history_entity_id)

        _LOGGER.debug(
            "Starting history append for spool %s: entity_id=%s, raw_state=%s",
            spool_num,
            history_entity_id,
            getattr(history_state, "state", None),
        )

        # Decode existing JSON list (if any)
        entries = []
        if history_state and history_state.state not in ("unknown", "unavailable", ""):
            try:
                data = json.loads(history_state.state)
                if isinstance(data, list):
                    entries = data
            except (ValueError, TypeError):
                _LOGGER.warning("Spool %s history contained invalid JSON, resetting", spool_num)

        # Determine file name if available
        file_name = "Unknown"
        if self.file_name_entity:
            file_state = self.hass.states.get(self.file_name_entity)
            if file_state and file_state.state not in ("unknown", "unavailable"):
                file_name = file_state.state

        # Compute approximate weight in grams
        density_state = self.hass.states.get(f"number.centauri_spool_manager_spool_{spool_num}_density")
        diameter_state = self.hass.states.get("number.centauri_spool_manager_filament_diameter")

        density = 1.24
        diameter = 1.75
        if density_state and density_state.state not in ("unknown", "unavailable"):
            try:
                density = float(density_state.state)
            except (ValueError, TypeError):
                pass
        if diameter_state and diameter_state.state not in ("unknown", "unavailable"):
            try:
                diameter = float(diameter_state.state)
            except (ValueError, TypeError):
                pass

        radius_mm = diameter / 2
        volume_mm3 = 3.14159265359 * (radius_mm ** 2) * extruded_length
        volume_cm3 = volume_mm3 / 1000
        weight_g = volume_cm3 * density

        # New entry structure
        entry = {
            "date": datetime.now().isoformat(timespec="seconds"),
            "spool": spool_name,
            "file": file_name,
            "length_mm": int(round(extruded_length)),
            "weight_g": round(weight_g, 1),
        }

        entries.append(entry)
        # Keep last 10 entries
        entries = entries[-10:]

        _LOGGER.debug(
            "Prepared history entry for spool %s: %s (total_entries=%d)",
            spool_num,
            entry,
            len(entries),
        )

        await self.hass.services.async_call(
            "text",
            "set_value",
            {
                "entity_id": history_entity_id,
                "value": json.dumps(entries),
            },
            blocking=True,
        )

        _LOGGER.info(
            "Updated print history for spool %s (%s); entries=%d",
            spool_num,
            spool_name,
            len(entries),
        )

    async def _update_spool_usage(self):
        """Update spool usage during active print."""
        if not self._tracking_active or not self._active_spool:
            return

        # Get current extrusion
        extrusion_state = self.hass.states.get(self.extrusion_entity)
        if not extrusion_state or extrusion_state.state in ("unknown", "unavailable"):
            return

        current_extrusion = float(extrusion_state.state)
        extruded_length = current_extrusion - self._print_start_extrusion

        # Extract spool number
        spool_num = self._active_spool.replace("Spool ", "")

        # Update used length
        used_length_entity = f"number.centauri_spool_manager_spool_{spool_num}_used_length"
        used_state = self.hass.states.get(used_length_entity)

        if used_state and used_state.state not in ("unknown", "unavailable"):
            # Note: We only update at print end to avoid constant writes
            # This function can be extended for real-time updates if needed
            _LOGGER.debug(f"Current print extrusion: {extruded_length}mm")
