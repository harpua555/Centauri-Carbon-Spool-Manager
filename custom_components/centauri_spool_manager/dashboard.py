"""Auto-dashboard creation for Centauri Carbon Spool Manager."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.components.lovelace import dashboard as lovelace_dashboard
from homeassistant.helpers import storage

_LOGGER = logging.getLogger(__name__)

DASHBOARD_URL = "spool-manager"
DASHBOARD_TITLE = "Spool Manager"


async def async_create_dashboard(hass: HomeAssistant, num_spools: int) -> bool:
    """Provide dashboard setup instructions.

    Note: Programmatic dashboard creation in Home Assistant is complex and often
    requires a restart. Instead, we provide a ready-to-use YAML file.

    Args:
        hass: Home Assistant instance
        num_spools: Number of spools to include in dashboard

    Returns:
        bool: Always returns True (info message only)
    """
    _LOGGER.info(
        "╔════════════════════════════════════════════════════════════════╗\n"
        "║  Centauri Spool Manager - Dashboard Setup                     ║\n"
        "╠════════════════════════════════════════════════════════════════╣\n"
        "║  To add the Spool Manager dashboard:                          ║\n"
        "║                                                                ║\n"
        "║  1. Go to Settings → Dashboards → Add Dashboard               ║\n"
        "║  2. Click 'Take Control' to enable YAML mode                  ║\n"
        "║  3. Copy the YAML from:                                       ║\n"
        "║     custom_components/centauri_spool_manager/lovelace/        ║\n"
        "║     dashboard.yaml                                            ║\n"
        "║  4. Paste into your dashboard                                 ║\n"
        "║                                                                ║\n"
        "║  Or view the file in your config at:                          ║\n"
        f"║  .../custom_components/centauri_spool_manager/lovelace/       ║\n"
        "║                                                                ║\n"
        "║  The dashboard includes:                                      ║\n"
        "║  • Overview tab with all spools                               ║\n"
        f"║  • {num_spools} individual spool configuration tabs                    ║\n"
        "║  • Color-coded gauges and status indicators                   ║\n"
        "╚════════════════════════════════════════════════════════════════╝"
    )
    return True


def _generate_dashboard_config(num_spools: int) -> dict[str, Any]:
    """Generate the dashboard configuration dictionary.

    Args:
        num_spools: Number of spools to include

    Returns:
        dict: Dashboard configuration
    """
    views = []

    # Overview tab
    views.append(_generate_overview_view(num_spools))

    # Individual spool tabs
    for spool_num in range(1, num_spools + 1):
        views.append(_generate_spool_view(spool_num))

    return {"views": views}


def _generate_overview_view(num_spools: int) -> dict[str, Any]:
    """Generate the overview tab configuration.

    Args:
        num_spools: Number of spools to include

    Returns:
        dict: Overview view configuration
    """
    # Build grid of spool overview cards
    spool_cards = []
    for spool_num in range(1, num_spools + 1):
        spool_cards.append({
            "type": "vertical-stack",
            "cards": [
                {
                    "type": "markdown",
                    "content": f"""### Spool {spool_num}
**{{{{ states('text.centauri_spool_manager_spool_{spool_num}_name') or 'Unnamed' }}}}**
{{{{ states('select.centauri_spool_manager_spool_{spool_num}_material') }}}}"""
                },
                {
                    "type": "gauge",
                    "entity": f"sensor.centauri_spool_manager_spool_{spool_num}_percentage_remaining",
                    "name": "Remaining",
                    "needle": True,
                    "min": 0,
                    "max": 100,
                    "severity": {
                        "green": 50,
                        "yellow": 20,
                        "red": 0,
                    },
                },
                {
                    "type": "horizontal-stack",
                    "cards": [
                        {
                            "type": "entity",
                            "entity": f"sensor.centauri_spool_manager_spool_{spool_num}_remaining_weight",
                            "name": "Weight",
                            "icon": "mdi:weight-gram",
                        },
                        {
                            "type": "entity",
                            "entity": f"sensor.centauri_spool_manager_spool_{spool_num}_state",
                            "name": "Status",
                            "icon": "mdi:state-machine",
                        },
                    ],
                },
            ],
        })

    return {
        "title": "Overview",
        "path": "overview",
        "icon": "mdi:printer-3d",
        "cards": [
            {
                "type": "vertical-stack",
                "cards": [
                    {
                        "type": "entities",
                        "title": "Spool Manager Controls",
                        "show_header_toggle": False,
                        "entities": [
                            {
                                "entity": "select.centauri_spool_manager_active_spool",
                                "name": "Active Spool",
                                "icon": "mdi:printer-3d-nozzle",
                            },
                            {
                                "entity": "switch.centauri_spool_manager_enable_spool_tracking",
                                "name": "Enable Automatic Tracking",
                                "icon": "mdi:toggle-switch",
                            },
                            {
                                "entity": "number.centauri_spool_manager_filament_diameter",
                                "name": "Filament Diameter",
                                "icon": "mdi:diameter",
                            },
                        ],
                    },
                    {
                        "type": "grid",
                        "columns": 2,
                        "square": False,
                        "cards": spool_cards,
                    },
                ],
            },
        ],
    }


def _generate_spool_view(spool_num: int) -> dict[str, Any]:
    """Generate a spool configuration tab.

    Args:
        spool_num: Spool number (1-based)

    Returns:
        dict: Spool view configuration
    """
    return {
        "title": f"Spool {spool_num}",
        "path": f"spool{spool_num}",
        "icon": f"mdi:numeric-{spool_num}-circle",
        "cards": [
            {
                "type": "vertical-stack",
                "cards": [
                    # Configuration section
                    {
                        "type": "entities",
                        "title": f"Spool {spool_num} Configuration",
                        "show_header_toggle": False,
                        "entities": [
                            {
                                "entity": f"switch.centauri_spool_manager_spool_{spool_num}_lock",
                                "name": "Lock Configuration",
                                "icon": "mdi:lock",
                            },
                            {"type": "divider"},
                            {
                                "entity": f"text.centauri_spool_manager_spool_{spool_num}_name",
                                "name": "Spool Name",
                            },
                            {
                                "entity": f"select.centauri_spool_manager_spool_{spool_num}_material",
                                "name": "Material Type",
                            },
                            {
                                "entity": f"number.centauri_spool_manager_spool_{spool_num}_set_weight",
                                "name": "Initial Weight",
                            },
                            {
                                "entity": f"number.centauri_spool_manager_spool_{spool_num}_density",
                                "name": "Material Density",
                            },
                        ],
                    },
                    # Status gauges
                    {
                        "type": "horizontal-stack",
                        "cards": [
                            {
                                "type": "gauge",
                                "entity": f"sensor.centauri_spool_manager_spool_{spool_num}_percentage_remaining",
                                "name": "Remaining %",
                                "needle": True,
                                "min": 0,
                                "max": 100,
                                "severity": {
                                    "green": 50,
                                    "yellow": 20,
                                    "red": 0,
                                },
                            },
                            {
                                "type": "gauge",
                                "entity": f"sensor.centauri_spool_manager_spool_{spool_num}_remaining_weight",
                                "name": "Weight (g)",
                                "needle": False,
                                "min": 0,
                                "max": 1000,
                                "severity": {
                                    "green": 500,
                                    "yellow": 200,
                                    "red": 0,
                                },
                            },
                        ],
                    },
                    # Detailed stats
                    {
                        "type": "entities",
                        "title": f"Spool {spool_num} Statistics",
                        "show_header_toggle": False,
                        "entities": [
                            {
                                "entity": f"sensor.centauri_spool_manager_spool_{spool_num}_state",
                                "name": "Status",
                                "icon": "mdi:state-machine",
                            },
                            {"type": "divider"},
                            {
                                "entity": f"sensor.centauri_spool_manager_spool_{spool_num}_initial_weight",
                                "name": "Initial Weight",
                            },
                            {
                                "entity": f"sensor.centauri_spool_manager_spool_{spool_num}_remaining_weight",
                                "name": "Remaining Weight",
                            },
                            {
                                "entity": f"sensor.centauri_spool_manager_spool_{spool_num}_used_weight",
                                "name": "Used Weight",
                            },
                            {"type": "divider"},
                            {
                                "entity": f"number.centauri_spool_manager_spool_{spool_num}_initial_length",
                                "name": "Initial Length",
                            },
                            {
                                "entity": f"sensor.centauri_spool_manager_spool_{spool_num}_remaining_length",
                                "name": "Remaining Length",
                            },
                            {
                                "entity": f"number.centauri_spool_manager_spool_{spool_num}_used_length",
                                "name": "Used Length",
                            },
                            {"type": "divider"},
                            {
                                "entity": f"sensor.centauri_spool_manager_spool_{spool_num}_last_print_weight",
                                "name": "Last Print Used",
                            },
                        ],
                    },
                    # Action buttons
                    {
                        "type": "horizontal-stack",
                        "cards": [
                            {
                                "type": "button",
                                "entity": f"button.centauri_spool_manager_spool_{spool_num}_reset",
                                "name": "Reset Spool",
                                "icon": "mdi:refresh",
                                "tap_action": {"action": "toggle"},
                            },
                            {
                                "type": "button",
                                "entity": f"button.centauri_spool_manager_spool_{spool_num}_mark_empty",
                                "name": "Mark Empty (Quick Reload)",
                                "icon": "mdi:checkbox-blank-circle-outline",
                                "tap_action": {"action": "toggle"},
                            },
                            {
                                "type": "button",
                                "entity": f"button.centauri_spool_manager_spool_{spool_num}_undo_last_print",
                                "name": "Undo Last Print",
                                "icon": "mdi:undo",
                                "tap_action": {"action": "toggle"},
                            },
                        ],
                    },
                ],
            },
        ],
    }
